import requests
from collections import defaultdict

URL_ORIGINAL = "http://lmdns.online/get.php?username=4x6cXF&password=ehfxdp&type=m3u_plus&output=m3u8"

response = requests.get(URL_ORIGINAL)
linhas = response.text.splitlines()

grupos = defaultdict(list)

i = 0
while i < len(linhas):
    linha = linhas[i]

    if linha.startswith("#EXTINF"):
        # Extrai nome do grupo
        inicio = linha.find('group-title="')
        if inicio != -1:
            inicio += len('group-title="')
            fim = linha.find('"', inicio)
            grupo = linha[inicio:fim]
        else:
            grupo = "OUTROS"

        grupos[grupo].append(linha)

        if i + 1 < len(linhas):
            grupos[grupo].append(linhas[i + 1])

        i += 2
    else:
        i += 1

# Ordem desejada
ordem_final = []

# Cabeçalho
ordem_final.append("#EXTM3U")

# 1️⃣ TV ABERTA
if "TV ABERTA" in grupos:
    ordem_final.extend(grupos["TV ABERTA"])

# 2️⃣ EVENTOS
if "EVENTOS" in grupos:
    ordem_final.extend(grupos["EVENTOS"])

# 3️⃣ Restante dos grupos
for grupo in grupos:
    if grupo not in ["TV ABERTA", "EVENTOS"]:
        ordem_final.extend(grupos[grupo])

# Salva
with open("h.m3u8", "w", encoding="utf-8") as f:
    f.write("\n".join(ordem_final))