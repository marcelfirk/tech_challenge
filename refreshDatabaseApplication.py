import flask
from flask import Flask, jsonify, request
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import mysql.connector


# Conexão ao banco de dados no RDS
# host = 'database-vitivinicultura.clqys6a4wwhq.us-east-2.rds.amazonaws.com'
# port = '3306'
# user = 'aborteiras'
# pw = '4b0rt3ir4s'
# db = 'db_vitivinicultura'
# conexao = mysql.connector.connect(host=host, database=db, user=user, password=pw)'´
# cursor = conexao.cursor()
# cursor.execute('Sentença_sql')


class paginasDados:
    def __init__(self, url, nome_pagina, categoria1, sub_option=None, categoria2=None):
        self.url = url
        self.nome_pagina = nome_pagina
        self.sub_option = sub_option
        self.categoria1 = categoria1
        self.categoria2 = categoria2
    def imprime_dados(self):
        print(self.nome_pagina)



# Função que pega a primeira página do site
def geturl(url):
    conteudo = requests.get(url).content
    return conteudo


# Função que transforma data no formato do site para datetime
def str_para_data(str):
    data = datetime(2000 + int(str[6:8]), int(str[3:5]), int(str[0:2]))
    return data


# Função que traz a URL da sub option conforme opt e sopt enviadas
def url_sopt(opt, sopt):
    url_sopt = f'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao={sopt}&opcao={opt}'
    return url_sopt


# URLs para consumo
url_home = 'http://vitibrasil.cnpuv.embrapa.br/'
url_opt = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao='


# Home para scrapping inicial
html = BeautifulSoup(geturl(url_home),'html.parser')


# Variável para verificação se é necessária atualização do RDS
data_mod_str = html.find('table', attrs={"class": 'tb_base tb_footer'}).td.text.split()[-1]
data_mod = str_para_data(data_mod_str)


# Obtendo a data da última modificação do banco de dados
data_bd = datetime(2023,1,1) # arrumar para a consulta no banco de dados dps


# Quando RDS desatualizado, atualizar tabelas
if data_bd < data_mod:

    # Achando o nome da página
    paginas = html.find('td', attrs={"class": 'col_center', 'id': 'row_height'}).p

    # Achando os botões das options
    botoes = paginas.find_all('button', class_='btn_opt')
    nomes_botoes = [button['value'] for button in botoes]
    nomes_botoes.pop(0)
    nomes_botoes.pop(-1)

    # Início do loop para obtenção dos csv
    lista_paginas = []

    for i in range(len(nomes_botoes)):
        html_pagina = BeautifulSoup(geturl(''.join([url_opt,nomes_botoes[i]])),'html.parser')

        # Achando o nome da página
        paginas = html_pagina.find('td', attrs={"class": 'col_center', "id": "row_height"})
        nome_pagina = paginas.find('button', {'value': f'{nomes_botoes[i]}'}).text #tirar essa parte depois incluindo o nome na lista

        # Verificando se há subtópicos
        subtopicos = html_pagina.find('table', class_='tb_base tb_header no_print').p
        buttons = subtopicos.find_all('button', class_='btn_sopt')
        nomes_subtopicos = [[button['value'], button.text] for button in buttons]

        # Tratando o caso onde não há subtópicos
        if len(nomes_subtopicos) == 0:
            # Obtendo o link de download
            link = html_pagina.find('a', class_='footer_content', href=True)['href']

            # Montando o item da fila de execução
            lista_paginas.append(paginasDados(link, nome_pagina, 'categoria1'))

        # Tratando os casos onde há subtópicos
        else:
            for k in range(len(nomes_subtopicos)):
                html_pagina_sopt = BeautifulSoup(geturl(url_sopt(nomes_botoes[i],nomes_subtopicos[k][0])),'html.parser')
                link_sopt = html_pagina_sopt.find('a', class_='footer_content', href=True)['href']
                lista_paginas.append(paginasDados(link, nome_pagina, 'categoria1', sub_option=nomes_subtopicos[k][1]))

for i in lista_paginas:
    i.imprime_dados()