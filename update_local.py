import subprocess
import os

print("🚀 ATUALIZADOR DE LIVES (YT-DLP MODO ANDROID + COOKIES.TXT)")

# Garante que está sincronizado com o GitHub antes de tudo
print("🔄 Sincronizando com repositório remoto...")
subprocess.run(["git", "pull"], creationflags=subprocess.CREATE_NO_WINDOW)

# Verifica cookies.txt
if not os.path.exists("cookies.txt"):
    print("❌ cookies.txt não encontrado na pasta!")
    input("Coloque o arquivo cookies.txt e pressione ENTER...")
    exit()

# Lê lista de canais
with open("canais.txt", "r", encoding="utf-8") as file:
    linhas = file.readlines()

# Cria pasta
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
                "--cookies", "cookies.txt",
                "--js-runtimes", "node",
                "--extractor-args", "youtube:player_client=android",
                "-g",
                url
            ],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        output = result.stdout.strip()

        if not output:
            print(f"❌ Nenhuma saída para {nome}")
            print(result.stderr)
            continue

        hls_url = output.split("\n")[0]

        # valida se é link correto
        if "manifest.googlevideo.com" not in hls_url:
            print(f"❌ Link inválido para {nome}")
            print(hls_url)
            continue

        # salva arquivo
        with open(f"lives/{nome}.m3u8", "w", encoding="utf-8") as f:
            f.write(hls_url)

        print(f"✅ {nome} atualizado com sucesso.")

    except Exception as e:
        print(f"❌ Erro em {nome}: {e}")

# Commit automático (SOMENTE arquivos necessários)
print("📤 Enviando para Git...")

# adiciona apenas o que interessa
subprocess.run(
    ["git", "add", "lives/"],
    creationflags=subprocess.CREATE_NO_WINDOW
)

subprocess.run(
    ["git", "add", "canais.txt"],
    creationflags=subprocess.CREATE_NO_WINDOW
)

# (opcional) adiciona o próprio script
subprocess.run(
    ["git", "add", "*.py"],
    shell=True,
    creationflags=subprocess.CREATE_NO_WINDOW
)

# commit (só se houver mudança)
subprocess.run(
    ["git", "commit", "-m", "update lives (auto yt-dlp)"],
    creationflags=subprocess.CREATE_NO_WINDOW
)

subprocess.run(
    ["git", "push"],
    creationflags=subprocess.CREATE_NO_WINDOW
)

print("✅ Processo finalizado com segurança.")
