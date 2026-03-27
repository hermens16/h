
#!/usr/bin/env python3
# update_lives_win.py
# Versão final: extrai MASTER/VARIANT HLS (index.m3u8) com yt-dlp, prefere H.264/AAC,
# salva URL e manifesto para debug, e faz git add/commit/push apenas de lives/ e canais.txt.
#
# Uso: coloque este script na pasta do projeto (com canais.txt e cookies.txt opcional),
# e execute: python update_lives_win.py

import subprocess
import os
import sys
import json
from datetime import datetime

# ---------------- Configurações ----------------
BASE = os.path.abspath(os.path.dirname(__file__))
COOKIES = os.path.join(BASE, "cookies.txt")       # opcional
CANAL_FILE = os.path.join(BASE, "canais.txt")
LIVES_DIR = os.path.join(BASE, "lives")
LOG_DIR = os.path.join(BASE, "logs")
LOG_FILE = os.path.join(LOG_DIR, "update.log")
YTDLP = "yt-dlp.exe"      # ajuste se necessário (caminho absoluto se preciso)
CURL = "curl"             # opcional
FFMPEG = "ffmpeg"         # opcional
# ------------------------------------------------

os.makedirs(LIVES_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def run_cmd(cmd, timeout=None):
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, shell=False, timeout=timeout)
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as e:
        return 1, "", str(e)

def choose_variant_from_master(master_content):
    """
    Parse simples do master.m3u8 para escolher a sub-playlist cujo EXT-X-STREAM-INF
    contém CODECS com avc1 (H264) e mp4a (AAC). Retorna a URL relativa/absoluta da variante.
    """
    lines = [l.strip() for l in master_content.splitlines() if l.strip()]
    chosen = None
    for i, line in enumerate(lines):
        if line.upper().startswith("#EXT-X-STREAM-INF"):
            info = line
            # procurar codecs
            lowinfo = info.lower()
            # prefer avc1 + mp4a
            if "avc1" in lowinfo and "mp4a" in lowinfo:
                if i + 1 < len(lines):
                    candidate = lines[i + 1]
                    if not candidate.startswith("#"):
                        return candidate
            # se não tiver ambos, aceitar se houver avc1 (H264)
            if "avc1" in lowinfo or "h264" in lowinfo:
                if i + 1 < len(lines):
                    candidate = lines[i + 1]
                    if not candidate.startswith("#"):
                        chosen = candidate
    return chosen

def extract_candidate_url_from_json(url):
    """
    Usa yt-dlp -j para obter JSON e escolher candidate URL (preferir m3u8_variant/index.m3u8).
    Retorna tuple (candidate_url or None, raw_json_output, raw_stderr).
    """
    # montar comando; sem --extractor-args que forçam client=android
    cmd = [YTDLP, "--cookies", COOKIES, "-j", url] if os.path.exists(COOKIES) else [YTDLP, "-j", url]
    rc, out, err = run_cmd(cmd, timeout=30)
    if rc != 0 or not out:
        log(f"yt-dlp JSON falhou para {url}: rc={rc} err={err[:400]}")
        return None, out, err

    try:
        info = json.loads(out)
    except Exception as e:
        log(f"Erro ao parsear JSON do yt-dlp: {e}")
        return None, out, err

    formats = info.get("formats", []) or []
    # 1) procurar m3u8_native com 'variant'/'index' em url
    for f in formats:
        u = f.get("url","")
        proto = f.get("protocol","")
        if u and ".m3u8" in u:
            low = u.lower()
            if "variant" in low or "index.m3u8" in low or "hls_variant" in low:
                log(f"Escolhido (m3u8 variant) diretamente do JSON: {u}")
                return u, out, err
            if proto == "m3u8_native":
                log(f"Escolhido (m3u8_native) do JSON: {u}")
                return u, out, err

    # fallback: escolher última .m3u8 disponível (muitas vezes é a mais completa)
    for f in reversed(formats):
        u = f.get("url","")
        if u and ".m3u8" in u:
            log(f"Fallback escolhido do JSON: {u}")
            return u, out, err

    log("Nenhuma URL .m3u8 encontrada no JSON do yt-dlp.")
    return None, out, err

def download_to(path, url, ua="Mozilla/5.0 (Linux; Android 12)"):
    """
    Tenta usar curl para baixar; se não disponível, usa requests.
    """
    # tentar curl
    try:
        rc, out, err = run_cmd([CURL, "-L", "-A", ua, "-o", path, url], timeout=30)
        if rc == 0:
            return True, None
    except Exception:
        pass

    # fallback requests
    try:
        import requests
        headers = {"User-Agent": ua}
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            return True, None
        else:
            return False, f"HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)

def normalize_url(base_url, sub_url):
    # se sub_url já for absoluta, retorna; se for relativa, constrói absoluta a partir de base_url
    if sub_url.startswith("http://") or sub_url.startswith("https://"):
        return sub_url
    try:
        from urllib.parse import urljoin
        return urljoin(base_url, sub_url)
    except Exception:
        return sub_url

def safe_name(name):
    return "".join(c for c in name if c.isalnum() or c in " _-").strip()

def git_push_changes(repo_dir):
    """
    Adiciona lives/ e canais.txt, comita apenas se houver mudanças e faz push.
    Logs detalhados em LOG_FILE.
    """
    try:
        # adicionar arquivos relevantes
        rc, out, err = run_cmd(["git", "add", "--", "lives/", "canais.txt"])
        if rc != 0:
            log(f"git add falhou: rc={rc}, err={err}")
            return False

        # checar se há mudanças staged
        rc, status_out, status_err = run_cmd(["git", "status", "--porcelain"])
        if rc != 0:
            log(f"git status falhou: rc={rc}, err={status_err}")
            return False

        if not status_out.strip():
            log("Nada para commitar no Git.")
            return True  # não é erro; só não houve mudanças

        # commit com mensagem incluindo timestamp
        message = f"Auto-update lives: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        rc, out, err = run_cmd(["git", "commit", "-m", message])
        if rc != 0:
            log(f"git commit falhou: rc={rc}, err={err}")
            return False
        log("git commit realizado.")

        # push (capturando saída)
        rc, out, err = run_cmd(["git", "push"])
        if rc != 0:
            log(f"git push falhou: rc={rc}, err={err[:800]}")
            return False
        log("git push realizado com sucesso.")
        return True

    except Exception as e:
        log(f"Exceção durante git push: {e}")
        return False

# ----------------- Execução -----------------
log("🚀 ATUALIZADOR DE LIVES (yt-dlp modo VARIANT/MASTER preferido)")

if not os.path.exists(CANAL_FILE):
    log("❌ canais.txt não encontrado. Crie canais.txt com linhas: Nome|URL")
    sys.exit(1)

if not os.path.exists(COOKIES):
    log("⚠ cookies.txt não encontrado. O yt-dlp tentará rodar sem cookies (se necessário, adicione).")

with open(CANAL_FILE, "r", encoding="utf-8") as f:
    linhas = [l.strip() for l in f if l.strip() and "|" in l]

for linha in linhas:
    nome, url = [p.strip() for p in linha.split("|",1)]
    sname = safe_name(nome)
    log(f"🔄 Processando {sname} -> {url}")

    candidate, json_out, json_err = extract_candidate_url_from_json(url)
    if not candidate:
        log(f"❌ Não foi possível extrair candidate .m3u8 para {sname} (ver logs JSON).")
        # salvar info JSON bruto para debug
        with open(os.path.join(LIVES_DIR, f"{sname}.yt-dlp.json.txt"), "w", encoding="utf-8") as jf:
            jf.write(json_out or "")
            jf.write("\n\n--- stderr ---\n")
            jf.write(json_err or "")
        continue

    # baixar o master/variant para analisar
    master_path = os.path.join(LIVES_DIR, f"{sname}.master.m3u8")
    ok, err = download_to(master_path, candidate)
    if not ok:
        log(f"⚠ Falha ao baixar master manifest para {sname}: {err}; salvando URL mesmo assim.")
        # salvar apenas a URL
        with open(os.path.join(LIVES_DIR, f"{sname}.m3u8"), "w", encoding="utf-8") as out:
            out.write(candidate + "\n")
        continue

    log(f"Manifest salvo: {master_path}")

    # ler manifest e tentar escolher variante H264/AAC
    try:
        with open(master_path, "r", encoding="utf-8", errors="ignore") as mf:
            master_content = mf.read()
    except Exception as e:
        log(f"Erro ao ler manifest salvo: {e}")
        master_content = ""

    # se este manifest for já uma playlist de segmentos (não master), verificamos e salvamos diretamente
    if "#EXT-X-STREAM-INF" not in master_content.upper():
        # é uma playlist de nível inferior (media playlist). Salvar a URL final.
        final_url = candidate
        log(f"Manifest aparenta ser MEDIA playlist; usando URL direta.")
    else:
        # é master; procurar variante H264/AAC
        sub = choose_variant_from_master(master_content)
        if sub:
            final_url = normalize_url(candidate, sub)
            log(f"Escolhida variante H264/AAC: {final_url}")
            # baixar a subplaylist para debug
            sub_path = os.path.join(LIVES_DIR, f"{sname}.variant.m3u8")
            ok2, err2 = download_to(sub_path, final_url)
            if ok2:
                log(f"Variant salvo: {sub_path}")
            else:
                log(f"Aviso: falha ao baixar variant: {err2}")
        else:
            final_url = candidate
            log("Nenhuma variante H264/AAC encontrada explicitamente; usando master URL.")

    # salvar final_url em lives/<nome>.m3u8
    url_path = os.path.join(LIVES_DIR, f"{sname}.m3u8")
    with open(url_path, "w", encoding="utf-8") as uf:
        uf.write(final_url + "\n")
    log(f"✅ URL final salva: {url_path}")

    # (opcional) teste rápido com ffmpeg se disponível: tenta ler 5 segundos
    try:
        rc, out, err = run_cmd([FFMPEG, "-hide_banner", "-loglevel", "error",
                                "-headers", "User-Agent: Mozilla/5.0 (Linux; Android 12)",
                                "-i", final_url, "-t", "5", "-c", "copy", os.devnull], timeout=25)
        if rc == 0:
            log(f"ffmpeg conseguiu ler a stream (teste rápido) para {sname}.")
        else:
            log(f"ffmpeg teste falhou (código {rc}); isso pode indicar incompatibilidade no player.")
    except Exception as e:
        log(f"ffmpeg não disponível ou erro no teste: {e}")

# Ao final, fazer git add/commit/push apenas se tiver mudanças
git_push_changes(BASE)

log("✅ Processo finalizado.")
