
import subprocess
import os

# Lê lista de canais
with open("canais.txt", "r", encoding="utf-8") as file:
    linhas = file.readlines()

for linha in linhas:
    linha = linha.strip()

    if not linha or "|" not in linha:
        continue

    nome, url = linha.split("|", 1)

    print(f"Atualizando {nome}...")

    result = subprocess.run(
        ["yt-dlp.exe", "-f", "best[ext=m3u8]/best", "-g", url],
        capture_output=True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    hls_url = result.stdout.strip()

    if hls_url:
        os.makedirs("lives", exist_ok=True)

        with open(f"lives/{nome}.m3u8", "w", encoding="utf-8") as f:
            f.write(hls_url)

        print(f"{nome} atualizado com sucesso.")
    else:
        print(f"Erro ao atualizar {nome}")

# Commit automático
subprocess.run(
    ["git", "add", "."],
    creationflags=subprocess.CREATE_NO_WINDOW
)

subprocess.run(
    ["git", "commit", "-m", "auto update lives"],
    creationflags=subprocess.CREATE_NO_WINDOW
)

subprocess.run(
    ["git", "push"],
    creationflags=subprocess.CREATE_NO_WINDOW
)

print("Processo finalizado.")
