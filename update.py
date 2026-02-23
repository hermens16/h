import subprocess
import json
import os

with open("channels.json") as f:
    channels = json.load(f)

os.makedirs("live", exist_ok=True)

for name, url in channels.items():
    print(f"Processando: {name}")

    result = subprocess.run(
        ["yt-dlp", "-f", "best[ext=m3u8]", "-g", url],
        capture_output=True,
        text=True
    )

    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    hls_url = result.stdout.strip()

    if hls_url:
        with open(f"live/{name}.m3u8", "w") as f:
            f.write(hls_url)
        print("Arquivo criado.")
    else:
        print("Nenhum link gerado.")