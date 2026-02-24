import subprocess

url = "https://www.youtube.com/watch?v=GENH9mWlvb4"

result = subprocess.run(
    ["yt-dlp.exe", "-g", url],
    capture_output=True,
    text=True
)

hls_url = result.stdout.strip()

if hls_url:
    with open("lives/livro24h.m3u8", "w") as f:
        f.write(hls_url)
    print("Arquivo atualizado com sucesso.")
else:
    print("Não conseguiu gerar link.")
