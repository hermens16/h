import subprocess
import os

print("🚀 ATUALIZADOR DE LIVES (YT-DLP MODO NAVEGADOR)")

# Lê lista de canais
with open("canais.txt", "r", encoding="utf-8") as file:
    linhas = file.readlines()

os.makedirs("lives", exist_ok=True)

for linha in linhas:
    linha = linha.strip()

    if not linha or "|" not in linha:
        continue

    nome, url = linha.split("|", 1)

    print(f"🔄 Atualizando {nome}...")

    try:
        result = subprocess.run(
            [
                "yt-dlp.exe",
                "--cookies-from-browser", "edge",
                "--add-header", "User-Agent: Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Mobile Safari/537.36",
                "--add-header", f"Referer: {url}",
                "-g",
                url
            ],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        hls_url = result.stdout.strip().split("\n")[0]  # pega só a primeira linha

        if hls_url and "m3u8" in hls_url:

            with open(f"lives/{nome}.m3u8", "w", encoding="utf-8") as f:
                f.write(hls_url)

            print(f"✅ {nome} atualizado com sucesso.")

        else:
            print(f"❌ Falha ao extrair URL válida de {nome}")
            print(result.stderr)

    except Exception as e:
        print(f"❌ Erro em {nome}: {e}")

# Commit automático
print("📤 Enviando para Git...")

subprocess.run(
    ["git", "add", "."],
    creationflags=subprocess.CREATE_NO_WINDOW
)

subprocess.run(
    ["git", "commit", "-m", "update lives com cookies + headers"],
    creationflags=subprocess.CREATE_NO_WINDOW
)

subprocess.run(
    ["git", "push"],
    creationflags=subprocess.CREATE_NO_WINDOW
)

print("✅ Processo finalizado.")
