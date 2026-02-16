import requests

URL_ORIGINAL = "http://lmdns.online/get.php?username=4x6cXF&password=ehfxdp&type=m3u_plus&output=m3u8"
GROUP_EVENTOS = 'group-title="EVENTOS"'
GROUP_TV_ABERTA = 'group-title="TV ABERTA"'

response = requests.get(URL_ORIGINAL)
linhas = response.text.splitlines()

eventos = []

# Captura canais EVENTOS
i = 0
while i < len(linhas):
    linha = linhas[i]

    if linha.startswith("#EXTINF") and GROUP_EVENTOS in linha:
        eventos.append(linha)
        if i + 1 < len(linhas):
            eventos.append(linhas[i + 1])
        i += 2
    else:
        i += 1

# Lê lista principal
with open("h.m3u8", "r", encoding="utf-8") as f:
    lista = f.read().splitlines()

# Remove EVENTOS antigos
lista_limpa = []
pular = False

for linha in lista:
    if GROUP_EVENTOS in linha:
        pular = True
        continue
    if pular:
        pular = False
        continue
    lista_limpa.append(linha)

# Separa em blocos
cabecalho = [lista_limpa[0]]
resto = lista_limpa[1:]

nova_lista = cabecalho.copy()
i = 0

while i < len(resto):
    linha = resto[i]

    if linha.startswith("#EXTINF") and GROUP_TV_ABERTA in linha:
        # adiciona TV ABERTA
        nova_lista.append(linha)
        if i + 1 < len(resto):
            nova_lista.append(resto[i + 1])
        i += 2

        # insere EVENTOS logo depois
        nova_lista.extend(eventos)

    else:
        nova_lista.append(linha)
        i += 1

# Salva
with open("h.m3u8", "w", encoding="utf-8") as f:
    f.write("\n".join(nova_lista))