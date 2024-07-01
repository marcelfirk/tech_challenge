import requests
import re
from bs4 import BeautifulSoup
import csv


# Função que pega o conteúdo do html
def geturl(url):
    lista = requests.get(url).content
    # lista = requests.get(url).text.split("\n")
    return lista


# Achando a última modificação
html = BeautifulSoup(geturl(f'http://vitibrasil.cnpuv.embrapa.br/'),'html.parser')


# Achando o nome da página
paginas = html.find('td', attrs={"class": 'col_center', 'id': 'row_height'}).p
botoes = paginas.find_all('button', class_='btn_opt')
nomes_botoes = [button['value'] for button in botoes]
nomes_botoes.pop(0)
nomes_botoes.pop(-1)

# nome_pagina = paginas.find('button', {'value': f'{opcao}'}).text
# Verificando se há subtópicos
# subtopicos = html.find('table', class_='tb_base tb_header no_print').p
# buttons = subtopicos.find_all('button', class_='btn_sopt')
# nomes_subtopicos = [button['value'] for button in buttons]


# Quando não há subtópicos
# if len(nomes_subtopicos) == 0:
    # Encontrando o link de download do csv
#     link = html.find('a', class_='footer_content', href=True)['href']
#     dados = geturl(f'http://vitibrasil.cnpuv.embrapa.br/{link}')





