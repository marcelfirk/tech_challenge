import requests
import pandas as pd
from bs4 import BeautifulSoup
import csv


# Função que pega o conteúdo do html
def geturl(url):
    lista = requests.get(url).content
    return lista


# Variáveis que vão vir do outro código
lista_paginas = [['download/Producao.csv', 'Produção'], ['download/ProcessaViniferas.csv', 'Processamento', 'Viníferas']]

# Baixando o csv
for n in range(len(lista_paginas)):
    path_download = (lista_paginas[n][0])
    download_url = 'http://vitibrasil.cnpuv.embrapa.br/' + path_download
    df = pd.read_csv(download_url, sep=';')
    list_colunas = list(df.columns)
    index_ano = list_colunas.index('1970')
    len_colunas = len(list_colunas)
    lista_insert = []

# Quando tem subcategorias no csv
    if len(lista_paginas[n]) == 2:
        if index_ano == 3:
            for i in range(index_ano,len_colunas):
                for j in range(0,len(df.id)):
                    insert_statement = f"""insert into dados
                    (pagina, categoria, valor_categoria2, valor_categoria3, ano, feature, valor_feature, data_inclusao)
                    values ('{lista_paginas[n][1]}','{list_colunas[index_ano-1]}','{df.iat[j, 1]}','{df.iat[j, 2]}',{list_colunas[i]},'feature',{df.iat[j, i]}, '2024-06-30')"""
                    lista_insert.append(insert_statement)
        elif index_ano == 2:
            for i in range(index_ano,len_colunas):
                for j in range(0,len(df.id)):
                    insert_statement = f"""insert into dados
                    (pagina, categoria, valor_categoria2, ano, feature, valor_feature, data_inclusao)
                    values ('{lista_paginas[n][1]}','{list_colunas[index_ano-1]}','{df.iat[j, 1]}',{list_colunas[i]},'feature',{df.iat[j, i]}, '2024-06-30')"""
                    lista_insert.append(insert_statement)
    elif len(lista_paginas[n]) == 3:
        if index_ano == 3:
            for i in range(index_ano, len_colunas):
                for j in range(0, len(df.id)):
                    insert_statement = f"""insert into dados
                    (pagina, categoria, valor_categoria1, valor_categoria2, valor_categoria3, ano, feature, valor_feature, data_inclusao)
                    values ('{lista_paginas[n][1]}','{list_colunas[index_ano - 1]}','{lista_paginas[n][2]}','{df.iat[j, 1]}','{df.iat[j, 2]}',{list_colunas[i]},'feature',{df.iat[j, i]}, '2024-06-30')"""
                    lista_insert.append(insert_statement)
        elif index_ano == 2:
            for i in range(index_ano, len_colunas):
                for j in range(0, len(df.id)):
                    insert_statement = f"""insert into dados
                        (pagina, categoria, valor_categoria1, valor_categoria2, ano, feature, valor_feature, data_inclusao)
                        values ('{lista_paginas[n][1]}','{list_colunas[index_ano - 1]}','{lista_paginas[n][2]}','{df.iat[j, 1]}',{list_colunas[i]},'feature',{df.iat[j, i]}, '2024-06-30')"""
                    lista_insert.append(insert_statement)



# Quando nao tem subcategorias no csv ainda a fazer

print(lista_insert)

