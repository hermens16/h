import requests

URL_ORIGINAL = "http://lmdns.online/get.php?username=4x6cXF&password=ehfxdp&type=m3u_plus&output=m3u8"

GROUP_EVENTOS = 'group-title="EVENTOS"'
GROUP_TV_ABERTA = 'group-title="TV ABERTA"'

# Pega apenas EVENTOS da lista externa
response = requests.get(URL_ORIGINAL)
origem = response.text.splitlines()

eventos = []
i = 0
while i < len(origem):
    if origem[i].startswith("#EXTINF") and GROUP_EVENTOS in origem[i]:
        eventos.append(origem[i])
        if i + 1 < len(origem):
            eventos.append(origem[i + 1])
        i += 2
    else:
        i += 1

# Lê sua lista principal
with open("h.m3u8", "r", encoding="utf-8") as f:
    lista = f.read().splitlines()

# Remove EVENTOS antigos da sua lista
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

# Agora vamos inserir EVENTOS após o ÚLTIMO canal de TV ABERTA
nova_lista = []
i = 0

while i < len(lista_limpa):
    nova_lista.append(lista_limpa[i])

    # Detecta último canal TV ABERTA
    if (
        lista_limpa[i].startswith("#EXTINF")
        and GROUP_TV_ABERTA in lista_limpa[i]
        and (
            i + 2 >= len(lista_limpa)
            or GROUP_TV_ABERTA not in lista_limpa[i + 2]
        )
    ):
        nova_lista.extend(eventos)

    i += 1

# Salva
with open("h.m3u8", "w", encoding="utf-8") as f:
    f.write("\n".join(nova_lista))