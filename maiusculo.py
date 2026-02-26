arquivo = "h.m3u8"

with open(arquivo, "r", encoding="utf-8") as f:
    linhas = f.readlines()

nova_lista = []

for linha in linhas:
    if linha.startswith("#EXTINF") and "," in linha:
        antes, nome = linha.rsplit(",", 1)
        nome = nome.strip().upper()
        linha = f"{antes},{nome}\n"

    nova_lista.append(linha)

with open(arquivo, "w", encoding="utf-8") as f:
    f.writelines(nova_lista)

print("Canais convertidos para MAIÚSCULO com sucesso!")