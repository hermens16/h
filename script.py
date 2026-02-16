import requests

URL_ORIGINAL = "http://lmdns.online/get.php?username=4x6cXF&password=ehfxdp&type=m3u_plus&output=m3u8"

GROUP_EVENTOS = 'group-title="EVENTOS"'
GROUP_TV_ABERTA = 'group-title="TV ABERTA"'

response = requests.get(URL_ORIGINAL)
linhas_origem = response.text.splitlines()

# Captura apenas canais EVENTOS da lista original
eventos = []
i = 0
while i < len(linhas_origem):
    if linhas_origem[i].startswith("#EXTINF") and GROUP_EVENTOS in linhas_origem[i]:
        eventos.append(linhas_origem[i])
        if i + 1 < len(linhas_origem):
            eventos.append(linhas_origem[i + 1])
        i += 2
    else:
        i += 1

# Lê sua lista principal
with open("h.m3u8", "r", encoding="utf-8") as f:
    linhas = f.read().splitlines()

# Remove EVENTOS antigos
lista_sem_eventos = []
pular = False

for linha in linhas:
    if GROUP_EVENTOS in linha:
        pular = True
        continue
    if pular:
        pular = False
        continue
    lista_sem_eventos.append(linha)

# Montagem final
nova_lista = []
inserido = False

i = 0
while i < len(lista_sem_eventos):
    linha = lista_sem_eventos[i]
    nova_lista.append(linha)

    # Detecta final do grupo TV ABERTA
    if (
        linha.startswith("#EXTINF")
        and GROUP_TV_ABERTA in linha
        and i + 2 < len(lista_sem_eventos)
        and lista_sem_eventos[i + 2].startswith("#EXTINF")
        and GROUP_TV_ABERTA not in lista_sem_eventos[i + 2]
        and not inserido
    ):
        nova_lista.extend(eventos)
        inserido = True

    i += 1

# Se por algum motivo não inseriu, coloca após cabeçalho
if not inserido:
    nova_lista = [nova_lista[0]] + eventos + nova_lista[1:]

with open("h.m3u8", "w", encoding="utf-8") as f:
    f.write("\n".join(nova_lista))