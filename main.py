import json

import requests
from paginasDados import PaginasDados
from bs4 import BeautifulSoup
from datetime import datetime
from flask import Flask, jsonify, request
import pandas as pd
from io import StringIO
# from flask_jwt_extended import JWTManager, create_access_token, decode_token, jwt_required


# Parâmetros globais
url_home = 'http://vitibrasil.cnpuv.embrapa.br/'
url_opt = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao='
lista_paginas = []


# Funções globais
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


app = Flask(__name__)

# Cria uma chave para a autenticação JWT
# app.config['JWT_SECRET_KEY'] = 'marcelGabriel'  # Troque por uma chave secreta forte
# jwt = JWTManager(app)

# Rota de login
# @app.route('/login', methods=['POST'])
# def post_login():
#     if not request.is_json:
#         return jsonify({"msg": "Missing JSON in request"}), 400
#
#     username = request.json.get('username', None)
#     password = request.json.get('password', None)
#
#     if username != 'Teley' or password != 'teley1991':  # Validação simples, substitua pelo seu método de validação
#         return jsonify({"msg": "Bad username or password"}), 401
#
#     access_token = create_access_token(identity=username)
#     return jsonify(access_token=access_token), 200


@app.route('/api/listaPaginas', methods=['GET'])
# @jwt_required()
def get_lista_paginas():
    # Home para scrapping inicial
    html = BeautifulSoup(geturl(url_home), 'html.parser')

    # Achando o nome da página
    paginas = html.find('td', attrs={"class": 'col_center', 'id': 'row_height'}).p

    # Achando os botões das options
    botoes = paginas.find_all('button', class_='btn_opt')
    nomes_botoes = [button['value'] for button in botoes]
    nomes_botoes.pop(0)
    nomes_botoes.pop(-1)

    for i in range(len(nomes_botoes)):
        html_pagina = BeautifulSoup(geturl(''.join([url_opt, nomes_botoes[i]])), 'html.parser')

        # Achando o nome da página
        paginas = html_pagina.find('td', attrs={"class": 'col_center', "id": "row_height"})
        nome_pagina = paginas.find('button', {
            'value': f'{nomes_botoes[i]}'}).text  # tirar essa parte depois incluindo o nome na lista

        # Verificando se há subtópicos
        subtopicos = html_pagina.find('table', class_='tb_base tb_header no_print').p
        buttons = subtopicos.find_all('button', class_='btn_sopt')
        nomes_subtopicos = [[button['value'], button.text] for button in buttons]

        # Achando a tabela com as features
        table = html_pagina.find('table', class_='tb_base tb_dados')
        features = table.find_all('th')
        categorias = [None, None, None]
        for idx in range(len(features)):
            categorias[idx] = features[idx].get_text(strip=True)

        # Tratando o caso onde não há subtópicos
        if len(nomes_subtopicos) == 0:
            # Obtendo o link de download
            link = html_pagina.find('a', class_='footer_content', href=True)['href']
            # Montando o item da fila de execução
            lista_paginas.append(
                PaginasDados(link, nome_pagina, categorias[0], categoria1=categorias[1], categoria2=categorias[2]).to_dict())

        # Tratando os casos onde há subtópicos
        else:
            for k in range(len(nomes_subtopicos)):
                html_pagina_sopt = BeautifulSoup(geturl(url_sopt(nomes_botoes[i], nomes_subtopicos[k][0])),
                                                 'html.parser')
                link_sopt = html_pagina_sopt.find('a', class_='footer_content', href=True)['href']

                lista_paginas.append(
                    PaginasDados(link_sopt, nome_pagina, categorias[0], sub_option=nomes_subtopicos[k][1],
                                 categoria1=categorias[1], categoria2=categorias[2]).to_dict())

    lista_json = json.dumps(lista_paginas, ensure_ascii=False, indent=4)
    return lista_json

@app.route('/api/ultimaAtualizacao', methods=['GET'])
def get_ultima_atualizacao():
    # Home para scrapping inicial
    html = BeautifulSoup(geturl(url_home), 'html.parser')

    # Variável para verificação se é necessária atualização do RDS
    data_mod_str = html.find('table', attrs={"class": 'tb_base tb_footer'}).td.text.split()[-1]
    data_mod = {"dataAtualizacaoSite": data_mod_str}

    # Obtendo a data da última modificação do banco de dados
    data_bd = datetime(2023, 1, 1)  # arrumar para a consulta no banco de dados dps

    return json.dumps(data_mod, ensure_ascii=False, indent=4)

@app.route('/api/disponibilidade', methods=['GET'])
def get_disponibilidade():
    try:
        response = requests.get(url_home)
        if response.status_code == 200:
            return json.dumps({"status": "disponivel"}, ensure_ascii=False, indent=4)
    except requests.exceptions.RequestException:
        return json.dumps({"status": "indisponivel"}, ensure_ascii=False, indent=4)


@app.route('/')
def index():
    return 'Hello!'

if __name__ == '__main__':
    app.run(debug=True)