import requests
import pandas as pd
from bs4 import BeautifulSoup
import csv


# Função que pega o conteúdo do html
def geturl(url):
    lista = requests.get(url).content
    return lista


# Variáveis que vão vir do outro código
nome_pagina = 'Processamento'
nome_subopt = 'Viníferas'

# Baixando o csv
df = pd.read_csv('http://vitibrasil.cnpuv.embrapa.br/download/Producao.csv', sep=';')
list_colunas = list(df.columns)
index_ano = list_colunas.index('1970')
len_colunas = len(list_colunas)
lista_insert = []

# Quando tem subcategorias no csv
if index_ano == 3:
    for i in range(index_ano,len_colunas):
        for j in range(0,len(df.id)):
            insert_statement = f"""insert into dados
            (pagina, categoria, valor_categoria2, valor_categoria3, ano, feature, valor_feature, data_inclusao)
            values ('{nome_pagina}','{list_colunas[index_ano-1]}','{df.iat[j, 1]}','{df.iat[j, 2]}',{list_colunas[i]},'feature',{df.iat[j, i]}, '2024-06-30')"""
            lista_insert.append(insert_statement)

# Quando nao tem subcategorias no csv ainda a fazer

print(lista_insert)

