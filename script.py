import requests

URL_ORIGINAL = "http://lmdns.online/get.php?username=4x6cXF&password=ehfxdp&type=m3u_plus&output=m3u8"
GROUP_NAME = 'group-title="EVENTOS"'

response = requests.get(URL_ORIGINAL)
linhas = response.text.splitlines()

jogos = []

i = 0
while i < len(linhas):
    linha = linhas[i]

    if linha.startswith("#EXTINF") and GROUP_NAME in linha:
        jogos.append(linha)
        if i + 1 < len(linhas):
            jogos.append(linhas[i + 1])
        i += 2
    else:
        i += 1

# Lê lista principal
with open("h.m3u8", "r", encoding="utf-8") as f:
    lista_principal = f.read().splitlines()

# Remove jogos antigos
lista_sem_jogos = [
    linha for linha in lista_principal
    if GROUP_NAME not in linha
]

# Garante cabeçalho
if not lista_sem_jogos[0].startswith("#EXTM3U"):
    lista_sem_jogos.insert(0, "#EXTM3U")

# Mantém cabeçalho separado
cabecalho = [lista_sem_jogos[0]]
resto_lista = lista_sem_jogos[1:]

# Nova lista com jogos no topo
nova_lista = cabecalho + jogos + resto_lista

with open("h.m3u8", "w", encoding="utf-8") as f:
    f.write("\n".join(nova_lista))
