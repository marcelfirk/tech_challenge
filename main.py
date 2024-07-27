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
def geturl(url: str) -> bytes:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException:
        return b''


# Função que transforma data no formato do site para datetime
def str_para_data(data_str: str) -> datetime:
    return datetime(2000 + int(data_str[6:8]), int(data_str[3:5]), int(data_str[0:2]))


# Função que traz a URL da sub option conforme opt e sopt enviadas
def url_sopt(opt: str, sopt: str) -> str:
    return f'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao={sopt}&opcao={opt}'


def url_sopt_ano(opt: str, sopt: str, ano: str) -> str:
    return f'http://vitibrasil.cnpuv.embrapa.br/index.php?ano={ano}&subopcao={sopt}&opcao={opt}'


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

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
    try:
        html = BeautifulSoup(geturl(url_home), 'html.parser')
    except:
        return jsonify({"error": "Erro ao obter html da página"})

    # Achando os nomes das páginas
    paginas = html.find('td', attrs={"class": 'col_center', 'id': 'row_height'}).p

    # Achando os botões das options
    botoes = paginas.find_all('button', class_='btn_opt')
    nomes_botoes = [botao['value'] for botao in botoes][1:-1]

    for nome_botao in nomes_botoes:
        html_pagina = BeautifulSoup(geturl(''.join([url_opt, nome_botao])), 'html.parser')

        # Achando o nome da página
        paginas = html_pagina.find('td', attrs={"class": 'col_center', "id": "row_height"})
        pagina = paginas.find('button', {'value': f'{nome_botao}'}).text

        # Verificando se há subtópicos
        subtopicos = html_pagina.find('table', class_='tb_base tb_header no_print').p
        buttons = subtopicos.find_all('button', class_='btn_sopt')
        nomes_subtopicos = [[button['value'], button.text] for button in buttons]

        # Achando a tabela com as features
        table = html_pagina.find('table', class_='tb_base tb_dados')
        ths = table.find_all('th')
        features = [None, None, None]
        for idx, feature in enumerate(ths):
            features[idx] = feature.get_text(strip=True)

        # Tratando o caso onde não há subtópicos
        if not nomes_subtopicos:
            # Obtendo o link de download
            link = html_pagina.find('a', class_='footer_content', href=True)['href']
            # Montando o item da fila de execução
            lista_paginas.append(
                PaginasDados(pagina, nome_botao, link, features[0], features[1], feature1=features[2]).to_dict())

        # Tratando os casos onde há subtópicos
        else:
            for cod_sopt, nome_sopt in nomes_subtopicos:
                html_pagina_sopt = BeautifulSoup(geturl(url_sopt(nome_botao, cod_sopt)), 'html.parser')
                link_sopt = html_pagina_sopt.find('a', class_='footer_content', href=True)['href']
                lista_paginas.append(
                    PaginasDados(pagina, nome_botao, link_sopt, features[0], features[1], subpagina=nome_sopt,
                                 cod_subpagina=cod_sopt,  feature1=features[2]).to_dict())

    # lista_json = json.dumps(lista_paginas, ensure_ascii=False, indent=4)
    return jsonify(lista_paginas)


@app.route('/api/ultimaAtualizacao', methods=['GET'])
def get_ultima_atualizacao():
    # Home para scrapping inicial
    html = BeautifulSoup(geturl(url_home), 'html.parser')
    data_mod_str = html.find('table', attrs={"class": 'tb_base tb_footer'}).td.text.split()[-1]
    data_mod = {"dataAtualizacaoSite": data_mod_str}
    return jsonify(data_mod)


@app.route('/api/disponibilidade', methods=['GET'])
def get_disponibilidade():
    try:
        response = requests.get(url_home)
        status = "disponivel" if response.status_code == 200 else "indisponivel"
    except requests.RequestException:
        status = "indisponivel"
    return jsonify({"status": status})


@app.route('/api/pesquisa', methods=['GET'])
# @jwt_required()
def get_pesquisa():
    cod_pagina = request.args.get('codPagina')
    cod_subpagina = request.args.get('codSubpagina')
    ano = request.args.get('ano')
    pai = request.args.get('itemPai')
    filho = request.args.get('item')

    if not filho or not cod_pagina or not ano:
        return jsonify({"error": "Parâmetros obrigatórios insuficientes. Obrigatórios: codPagina, ano, item"}), 400

    html_pagina_sopt = BeautifulSoup(
        geturl(
            url_sopt_ano(cod_pagina, cod_subpagina, ano)
        ), 'html.parser').find('table', attrs={"class": 'tb_base tb_dados'})
    try:
        headers = html_pagina_sopt.thead
    except AttributeError as e:
        return jsonify({"error": "Erro, verifique se passou parâmetros corretos de paginas e subpaginas"}), 400
    table = html_pagina_sopt.tbody
    lista_headers = []
    lista_resultados = {}

    # Encontrando os nomes dos valores
    if headers:
        ths = headers.find_all('th')
        lista_headers = [th.text.strip() for th in ths]
    else:
        return jsonify({"error": "Erro, verifique se passou parâmetros corretos de paginas e subpaginas"}), 400

    # Encontrando os valores
    if table:
        trs = table.find_all('tr')
        found = False
        escopo = False if pai else True
        for tr in trs:
            tds = tr.find_all('td')
            if "tb_item" in tds[0].get('class', []) and not escopo:
                escopo = True if tds[0].text.strip() == pai else False
            if tds[0].text.strip() == filho and escopo:
                lista_resultados = {lista_headers[j]: tds[j].text.strip() for j in range(len(tds))}
                found = True
                break
        if not found:
            return jsonify({"error": "Item não encontrado no escopo solicitado"}), 400
    else:
        return jsonify({"error": "Erro, verifique se passou parâmetros corretos de paginas e subpaginas"}), 400

    return jsonify(lista_resultados)


@app.route('/api/getItens', methods=['GET'])
# @jwt_required()
def get_params():
    cod_pagina = request.args.get('codPagina')
    cod_subpagina = request.args.get('codSubpagina')
    if not cod_pagina:
        return jsonify({"error": "Parâmetros obrigatórios insuficientes. Obrigatórios: codPagina"}), 400

    html_pagina_sopt = BeautifulSoup(
        geturl(
            url_sopt(cod_pagina, cod_subpagina)
        ), 'html.parser').find('table', attrs={"class": 'tb_base tb_dados'})
    try:
        headers = html_pagina_sopt.thead
    except AttributeError as e:
        return jsonify({"error": "Erro, verifique se passou parâmetros corretos de paginas e subpaginas"}), 400
    table = html_pagina_sopt.tbody
    item = headers.find_all('th')[0].text.strip()
    itens = {"item": item}
    lista_itens = []

    # Encontrando os valores
    if table:
        trs = table.find_all('tr')
        for i in range(len(trs)):
            tds = trs[i].find_all('td')
            if "tb_item" in tds[0].get('class', []):
                pai = tds[0].text.strip()
            else:
                filho = tds[0].text.strip()
            lista_itens = lista_itens.append([pai, filho])



    return jsonify(lista_itens)

@app.route('/')
def index():
    return 'Hello!'


if __name__ == '__main__':
    app.run(debug=True)