import requests

URL_ORIGINAL = "http://lmdns.online/get.php?username=4x6cXF&password=ehfxdp&type=m3u_plus&output=m3u8"
GROUP_NAME = 'group-title="EVENTOS"'

response = requests.get(URL_ORIGINAL)
linhas = response.text.splitlines()

eventos = []

i = 0
while i < len(linhas):
    linha = linhas[i]

    if linha.startswith("#EXTINF") and GROUP_NAME in linha:
        # Separa antes e depois da vírgula
        partes = linha.rsplit(",", 1)

        if len(partes) == 2:
            antes, nome = partes
            nome = nome.strip().upper()  # CONVERTE PARA MAIÚSCULO
            linha = f"{antes},{nome}"

        eventos.append(linha)

        # adiciona o link da linha seguinte
        if i + 1 < len(linhas):
            eventos.append(linhas[i + 1])

        i += 2
    else:
        i += 1

# Lê lista principal
with open("h.m3u8", "r", encoding="utf-8") as f:
    lista_principal = f.read().splitlines()

# Remove EVENTOS antigos da lista
nova_lista_limpa = []
pular_proxima = False

for linha in lista_principal:
    if GROUP_NAME in linha:
        pular_proxima = True
        continue
    if pular_proxima:
        pular_proxima = False
        continue
    nova_lista_limpa.append(linha)

# Garante cabeçalho
if not nova_lista_limpa or not nova_lista_limpa[0].startswith("#EXTM3U"):
    nova_lista_limpa.insert(0, "#EXTM3U")

cabecalho = [nova_lista_limpa[0]]
resto = nova_lista_limpa[1:]

# Insere EVENTOS no topo
lista_final = cabecalho + eventos + resto

with open("h.m3u8", "w", encoding="utf-8") as f:
    f.write("\n".join(lista_final))

print("EVENTOS atualizados e convertidos para MAIÚSCULO com sucesso!")