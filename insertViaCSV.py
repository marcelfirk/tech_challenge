import requests
import pandas as pd
from paginasDados import PaginasDados
from bs4 import BeautifulSoup
import csv
import psycopg2
import math


# Função que pega o conteúdo do html
def geturl(url):
    lista = requests.get(url).content
    return lista


def converter_para_float(valor):
    try:
        if math.isnan(float(valor)):
            return 0
        else:
            return float(valor)
    except ValueError:
        return 0


def nulo_para_string(valor):
    if valor is None:
        return 'null'
    else:
        return f"'{valor}'"


def gerar_insert_statement(objeto, valor_categoria2, valor_categoria3, ano, valor, data, tipo, cursor, conexao):

    sub_option = nulo_para_string(objeto.sub_option)

    # Para saber qual o tipo de feature para os casos que tem duas
    if tipo == 0:
        categoria = objeto.categoria1
    else:
        categoria = objeto.categoria2

    valor_categoria2 = nulo_para_string(valor_categoria2)

    valor_fix = converter_para_float(valor)

    f = open("names.txt", "a")
    insert_statement = f"""insert into dados (pagina, categoria, valor_categoria1, valor_categoria2, valor_categoria3, ano, feature, valor_feature, data_inclusao) values ('{objeto.nome_pagina}','{objeto.categoria0}',{sub_option},{valor_categoria2},'{valor_categoria3}',{ano},'{categoria}', {valor_fix}, '2024-01-01')"""
    cursor.execute(insert_statement)
    conexao.commit()

def insert_via_csv(objetos, data):


    # Conexão ao banco de dados no RDS
    host = 'localhost'
    port = '5432'
    user = 'postgres'
    pw = 'admin'
    db = 'postgres'
    conexao = psycopg2.connect(host=host, database=db, user=user, password=pw, port=port)
    cursor = conexao.cursor()


    # Baixando o csv
    download_url = 'http://vitibrasil.cnpuv.embrapa.br/' + objetos.url
    arquivo = geturl(download_url).decode('utf-8')
    indice_separador = arquivo.find('1970')
    fim_separador = arquivo.find('19', indice_separador+1)
    separador = arquivo[indice_separador+4:fim_separador]
    df = pd.read_csv(download_url, sep=separador)
    df.columns = df.columns.str.lower()
    list_colunas = list(df.columns)
    index_ano = list_colunas.index('1970')
    len_colunas = len(list_colunas)

    # Iniciando iterações para varrer data frame
    for i in range(index_ano, len_colunas):
        for j in range (0, len(df.id)):
            if df.iat[j, i] != 0:
                # Se não há valor_categoria2
                if index_ano == 2:
                    # Se é primeira feature
                    if len(df.columns[i]) == 4:
                        gerar_insert_statement(objetos, None, df.iat[j, 1], df.columns[i], df.iat[j, i], data, 0, cursor, conexao)
                    # Se é segunda feature
                    elif len(df.columns[i]) > 4:
                        gerar_insert_statement(objetos, None, df.iat[j, 1], df.columns[i][0:4], df.iat[j, i], data, 1, cursor, conexao)
                # Se há valor_categoria2
                if index_ano == 3:

                    if df.iat[j, 1] != df.iat[j, 2]:
                        # Se é primeira feature
                        if len(df.columns[i]) == 4:
                            gerar_insert_statement(objetos, df.iat[j, 1], df.iat[j, 2], df.columns[i], df.iat[j,i], data, 0, cursor, conexao)
                        # Se é segunda feature
                        elif len(df.columns[i]) > 4:
                            gerar_insert_statement(objetos, df.iat[j, 1], df.iat[j, 2], df.columns[i][0:4], df.iat[j, i], data, 1, cursor, conexao)

    conexao.close()