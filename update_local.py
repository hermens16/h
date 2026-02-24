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
        ["yt-dlp.exe", "-g", url],
        capture_output=True,
        text=True
    )

    hls_url = result.stdout.strip()

    if hls_url:
        with open(f"lives/{nome}.m3u8", "w", encoding="utf-8") as f:
            f.write(hls_url)

        print(f"{nome} atualizado com sucesso.")
    else:
        print(f"Erro ao atualizar {nome}")

# Commit automático
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", "auto update lives"])
subprocess.run(["git", "push"])

print("Processo finalizado.")
