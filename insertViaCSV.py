import requests
import pandas as pd
from paginasDados import PaginasDados
from bs4 import BeautifulSoup
import csv


# Função que pega o conteúdo do html
def geturl(url):
    lista = requests.get(url).content
    return lista


def gerar_insert_statement(objeto, categoria, valor_categoria2, valor_categoria3, ano, feature, valor, data):
    insert_statement = f"""insert into dados
                        (pagina, categoria, valor_categoria1, valor_categoria2, valor_categoria3, ano, feature, valor_feature, data_inclusao)
                        values ('{objeto.nome_pagina}','{categoria}','{objeto.sub_option}','{valor_categoria2}','{valor_categoria3}',{ano},'{feature}', {valor}, '{data}')"""


f = open("names.txt", "a")


# Variáveis que vão vir do outro código
lista_paginas = [['download/Producao.csv', 'Produção'], ['download/ProcessaViniferas.csv', 'Processamento', 'Viníferas'], ['download/ProcessaAmericanas.csv', 'Processamento', 'Americanas e híbridas'], ['download/ProcessaMesa.csv', 'Processamento', 'Uvas de mesa'], ['download/ProcessaSemclass.csv', 'Processamento', 'Sem classificação'], ['download/Comercio.csv', 'Comercialização'], ['download/ImpVinhos.csv', 'Importação', 'Vinhos de mesa'], ['download/ImpEspumantes.csv', 'Importação', 'Espumantes'], ['download/ImpFrescas.csv', 'Importação', 'Uvas frescas'], ['download/ImpPassas.csv', 'Importação', 'Uvas passas'], ['download/ImpSuco.csv', 'Importação', 'Suco de uva'], ['download/ExpVinho.csv', 'Exportação', 'Vinhos de mesa'], ['download/ExpEspumantes.csv', 'Exportação', 'Espumantes'], ['download/ExpUva.csv', 'Exportação', 'Uvas frescas'], ['download/ExpSuco.csv', 'Exportação', 'Suco de uva']]
data_inclusao = 'data'

# Baixando o csv
for n in range(len(lista_paginas)):
    path_download = (lista_paginas[n][0])
    download_url = 'http://vitibrasil.cnpuv.embrapa.br/' + path_download
    arquivo = geturl(download_url).decode('utf-8')
    indice_separador = arquivo.find('1970')
    fim_separador = arquivo.find('19', indice_separador+1)
    separador = arquivo[indice_separador+4:fim_separador]
    df = pd.read_csv(download_url, sep=separador)
    df.columns = df.columns.str.lower()
    list_colunas = list(df.columns)
    index_ano = list_colunas.index('1970')
    len_colunas = len(list_colunas)
    lista_insert = []


# Quando tem subcategorias no csv
    if len(lista_paginas[n]) == 2:
        if index_ano == 3:
            for i in range(index_ano,len_colunas):
                for j in range(0,len(df.id)):
                    if df.iat[j, i] != 0:
                        insert_statement = f"""insert into dados
                        (pagina, categoria, valor_categoria2, valor_categoria3, ano, feature, valor_feature, data_inclusao)
                        values ('{lista_paginas[n][1]}','{list_colunas[index_ano-1]}','{df.iat[j, 1]}','{df.iat[j, 2]}',{list_colunas[i]},'feature',{df.iat[j, i]}, '2024-06-30')"""
                        f.write('\n' + insert_statement)
        elif index_ano == 2:
            for i in range(index_ano,len_colunas):
                for j in range(0,len(df.id)):
                    if df.iat[j, i] != 0:
                        insert_statement = f"""insert into dados
                        (pagina, categoria, valor_categoria2, ano, feature, valor_feature, data_inclusao)
                        values ('{lista_paginas[n][1]}','{list_colunas[index_ano-1]}','{df.iat[j, 1]}',{list_colunas[i]},'feature',{df.iat[j, i]}, '2024-06-30')"""
                        f.write('\n' + insert_statement)
    elif len(lista_paginas[n]) == 3:
        if index_ano == 3:
            for i in range(index_ano, len_colunas):
                for j in range(0, len(df.id)):
                    print(df.iat[j, i])
                    if df.iat[j, i] != 0:
                        insert_statement = f"""insert into dados
                        (pagina, categoria, valor_categoria1, valor_categoria2, valor_categoria3, ano, feature, valor_feature, data_inclusao)
                        values ('{lista_paginas[n][1]}','{list_colunas[index_ano - 1]}','{lista_paginas[n][2]}','{df.iat[j, 1]}','{df.iat[j, 2]}',{list_colunas[i]},'feature',{df.iat[j, i]}, '2024-06-30')"""
                        f.write('\n' + insert_statement)
        elif index_ano == 2:
            for i in range(index_ano, len_colunas):
                for j in range(0, len(df.id)):
                    print(df.iat[j, i])
                    if df.iat[j, i] != 0:
                        insert_statement = f"""insert into dados
                        (pagina, categoria, valor_categoria1, valor_categoria2, ano, feature, valor_feature, data_inclusao)
                        values ('{lista_paginas[n][1]}','{list_colunas[index_ano - 1]}','{lista_paginas[n][2]}','{df.iat[j, 1]}',{list_colunas[i]},'feature',{df.iat[j, i]}, '2024-06-30')"""
                        f.write('\n' + insert_statement)




