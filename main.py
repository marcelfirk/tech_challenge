from datetime import datetime
import pandas as pd
import shutil
import os
import fnmatch
import json
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import csv
# from flask_jwt_extended import jwt_required
from paginasDados import PaginasDados

# Parâmetros globais
url_home = 'http://vitibrasil.cnpuv.embrapa.br/'
url_opt = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao='
arquivo_origem = 'lista_paginas.json'


def movimenta_csv_para_backup(diretorio, prefixo):
    diretorio_backup = f'{diretorio}\\Backups'
    arquivos = os.listdir(diretorio)
    for arquivo in arquivos:
        if fnmatch.fnmatch(arquivo, f'{prefixo}*'):
            if not os.path.exists(diretorio_backup):
                os.makedirs(diretorio_backup)
            path_origem = os.path.join(diretorio, arquivo)
            path_destino = f'{diretorio_backup}\\{arquivo}'
            shutil.move(path_origem, path_destino)


def download_csv(url, diretorio, nome_arquivo, user):
    response = requests.get(url)
    response.raise_for_status()
    if not os.path.exists(diretorio):
        os.makedirs(diretorio)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    movimenta_csv_para_backup(diretorio, nome_arquivo)
    nome_arquivo = f"{nome_arquivo}_{timestamp}.csv"
    path_arquivo = os.path.join(diretorio, nome_arquivo)
    with open(path_arquivo, 'wb') as file:
        file.write(response.content)
    log_download(path_arquivo, user)
    return path_arquivo


def log_download(nome_arquivo, user):
    log_file = "download_log.txt"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entrada_log = f"{timestamp}: {nome_arquivo} - user: {user}\n"
    with open(log_file, 'a') as file:
        file.write(entrada_log)


def abre_json(nome_arquivo):
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
            data = json.load(arquivo)
        return data
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def percorre_json(dados, campo1, valor1, campo2=None, valor2=None):
    for entry in dados:
        if valor2 is None:
            if entry.get(campo1) == valor1:
                return entry
        else:
            if entry.get(campo1) == valor1 and entry.get(campo2) == valor2:
                return entry
    return None


def geturl(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException:
        return None


def url_sopt(opt, sopt):
    return f'http://vitibrasil.cnpuv.embrapa.br/index.php?subopcao={sopt}&opcao={opt}'


def url_sopt_ano(opt, sopt, ano):
    return f'http://vitibrasil.cnpuv.embrapa.br/index.php?ano={ano}&subopcao={sopt}&opcao={opt}'


def pesquisa_site(html_pagina_sopt, pai, filho):
    try:
        headers = html_pagina_sopt.thead
        table = html_pagina_sopt.tbody
    except AttributeError:
        return jsonify({"error": "Erro, verifique se passou parâmetros corretos de paginas e subpaginas"}), 400

    lista_resultados = []
    if headers:
        lista_headers = [th.text.strip() for th in headers.find_all('th')]
    else:
        return jsonify({"error": "Erro, verifique se passou parâmetros corretos de paginas e subpaginas"}), 400
    if table:
        trs = table.find_all('tr')
        control = None
        found = False
        for tr in trs:
            tds = tr.find_all('td')
            if "tb_item" in tds[0].get('class', []):
                control = tds[0].text.strip()
            if tds[0].text.strip() == filho:
                resultado = {lista_headers[j]: tds[j].text.strip() for j in range(len(tds))}
                if control:
                    resultado['Control'] = control
                if (pai and control == pai) or not pai:
                    lista_resultados.append(resultado)
                found = True
        if not found:
            return jsonify({"error": "Item não encontrado no escopo solicitado"}), 400
    else:
        return jsonify({"error": "Erro, verifique se passou parâmetros corretos de paginas e subpaginas"}), 400

    return jsonify(lista_resultados)


def detectar_delimitador(arquivo):
    with open(arquivo, 'r', encoding='utf-8') as file:
        sample = file.read(-1)
        sniffer = csv.Sniffer()
        try:
            delimiter = sniffer.sniff(sample).delimiter
        except csv.Error:
            delimiter = ';'
    return delimiter


def pesquisa_valor(dataframe, nome_coluna, valor_coluna, ano, control):
    # Filter the DataFrame for the specific country and year
    if not control:
        result = dataframe.query(f'{nome_coluna} == @valor_coluna and ano == @ano')
        result_json_str = result.to_json(orient='records', date_format='iso', force_ascii=False)
        result_json = json.loads(result_json_str)
        return result_json
    else:
        result = dataframe.query(f'{nome_coluna} == @valor_coluna and ano == @ano and control == @control')
        result_json_str = result.to_json(orient='records', date_format='iso', force_ascii=False)
        result_json = json.loads(result_json_str)
        return result_json


def verifica_nome_arquivo(diretorio, prefixo):
    arquivos = os.listdir(diretorio)
    for arquivo in arquivos:
        if fnmatch.fnmatch(arquivo, f'{prefixo}*'):
            return os.path.join(diretorio, arquivo)
        else:
            return None


def pesquisa_csv(selecao, ano, valor_coluna, control=None):
    diretorio = os.path.join(os.getcwd(), 'CSVs', selecao.get('pagina'))
    prefixo = selecao.get('pagina')
    if selecao.get('codSubpagina'):
        diretorio = os.path.join(diretorio, selecao.get('subpagina'))
        prefixo = f"{prefixo}_{selecao.get('subpagina')}"
    arquivo = verifica_nome_arquivo(diretorio, prefixo)
    delimiter = detectar_delimitador(arquivo)
    df = pd.read_csv(arquivo, sep=delimiter, encoding='utf-8')
    colunas = df.columns.tolist()
    index_1970 = colunas.index('1970')
    colunas_precedentes = colunas[:index_1970]
    colunas_para_limpar = colunas[1:index_1970]
    df[colunas_para_limpar] = df[colunas_para_limpar].apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df_pivotada = df.melt(id_vars=colunas_precedentes, var_name="ano", value_name="valor")
    df_pivotada["ano"] = df_pivotada["ano"].str.replace(".1", "")
    if 'control' in df_pivotada.columns and df_pivotada['control'].notnull().any():
        df_pivotada['control'] = substituir_valor(df_pivotada['control'])
    nome_coluna = colunas_precedentes[-1]
    resultado = pesquisa_valor(df_pivotada, nome_coluna, valor_coluna, ano, control)
    lista_resultados = []
    if selecao.get('feature1'):
        for i in range(len(resultado)):
            lista_resultados.append({
                selecao.get('item'): resultado[i].get(nome_coluna),
                selecao.get(f'feature{i}'): resultado[i].get('valor')
            })
    else:
        for i in range(len(resultado)):
            lista_resultados.append({
                'Control': resultado[i].get('control'),
                selecao.get('item'): resultado[i].get(nome_coluna),
                selecao.get('feature0'): resultado[i].get('valor')
            })
    return jsonify(lista_resultados)


def substituir_valor(col):
    while col.str.contains("_", na=False).any():
        col_anterior = col.shift(1)
        col = col.where(~col.str.contains("_", na=False), col_anterior)
    return col


def extrair_itens_site(data):
    html_pagina_sopt = BeautifulSoup(
        geturl(
            url_sopt(data.get('codPagina'), data.get('codSubpagina'))
        ), 'html.parser').find('table', attrs={"class": 'tb_base tb_dados'})
    try:
        headers = html_pagina_sopt.thead
    except AttributeError:
        return jsonify({"error": "Erro, verifique se passou parâmetros corretos de paginas e subpaginas"}), 400
    table = html_pagina_sopt.tbody
    if len(table) == 1:
        return jsonify({"error": "Verifique os parâmetros enviados"}), 400
    item = headers.find_all('th')[0].text.strip()

    dict_itens = {}
    sem_classificacao = True
    if table:
        trs = table.find_all('tr')
        for i in range(len(trs)):
            tds = trs[i].find_all('td')
            if "tb_item" in tds[0].get('class', []):
                pai = tds[0].text.strip()
            elif "tb_subitem" in tds[0].get('class', []):
                sem_classificacao = False
                filho = tds[0].text.strip()
                if pai in dict_itens:
                    dict_itens[pai].append(filho)
                else:
                    dict_itens[pai] = [filho]
            elif tds:
                sem_classificacao = False
                if item in dict_itens:
                    dict_itens[item].append(tds[0].text.strip())
                else:
                    dict_itens[item] = [tds[0].text.strip()]

        if sem_classificacao:
            dict_itens[item] = [pai]

    return dict_itens


def extrair_itens_csv(dados):
    return jsonify({"maluco": "preciso fazer esse código"})

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
    # Inicializando a lista localmente
    lista_paginas = []

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
                                 cod_subpagina=cod_sopt, feature1=features[2]).to_dict())

    with open(arquivo_origem, 'w', encoding='utf-8') as file:
        json.dump(lista_paginas, file, ensure_ascii=False, indent=4)
    return jsonify(lista_paginas)


@app.route('/api/ultimaAtualizacaoSite', methods=['GET'])
def get_ultima_atualizacao_site():
    # Home para scrapping inicial
    html = BeautifulSoup(geturl(url_home), 'html.parser')
    data_mod_str = html.find('table', attrs={"class": 'tb_base tb_footer'}).td.text.split()[-1]
    data_mod = {"dataAtualizacaoSite": data_mod_str}
    return jsonify(data_mod)


@app.route('/api/disponibilidadeSite', methods=['GET'])
def get_disponibilidade():
    try:
        response = requests.get(url_home)
        status = "disponivel" if response.status_code == 200 else "indisponivel"
    except requests.RequestException:
        status = "indisponivel"
    return jsonify({"status": status})


@app.route('/api/pesquisaItem', methods=['GET'])
# @jwt_required()
def get_pesquisa_item():
    pagina = request.args.get('pagina')
    subpagina = request.args.get('subpagina')
    ano = request.args.get('ano')
    pai = request.args.get('itemPai')
    filho = request.args.get('item')
    origem = request.args.get('origem')

    if not filho or not pagina or not ano:
        return jsonify({"error": "Parâmetros obrigatórios insuficientes. Obrigatórios: pagina, ano, item"}), 400

    dados = percorre_json(abre_json(arquivo_origem), 'pagina', pagina, 'subpagina', subpagina)

    if origem == 'csv':
        site_offline = True
    else:
        site_offline = False

    try:
        html_pagina_sopt = BeautifulSoup(
            geturl(
                url_sopt_ano(dados.get('codPagina'), dados.get('codSubpagina'), ano)
            ), 'html.parser').find('table', attrs={"class": 'tb_base tb_dados'})
    except requests.exceptions.RequestException:
        site_offline = True

    if not site_offline:
        return pesquisa_site(html_pagina_sopt, pai, filho)

    else:
        if pai:
            return pesquisa_csv(dados, subpagina, ano, filho, pai)
        else:
            return pesquisa_csv(dados, subpagina, ano, filho)


@app.route('/api/getItens', methods=['GET'])
# @jwt_required()
def get_params():
    pagina = request.args.get('pagina')
    subpagina = request.args.get('subpagina')
    origem = request.args.get('origem')

    if not pagina:
        return jsonify({"error": "Parâmetros obrigatórios insuficientes. Obrigatórios: Pagina"}), 400

    dados = percorre_json(abre_json(arquivo_origem), 'pagina', pagina, 'subpagina', subpagina)

    if origem == 'csv':
        return extrair_itens_csv(dados)
    else:
        return extrair_itens_site(dados)


@app.route('/api/atualizaCsv', methods=['POST'])
def post_atualiza_csv():
    pagina = request.args.get('pagina')
    subpagina = request.args.get('subpagina')

    if not pagina:
        return jsonify({"error": "Parâmetros obrigatórios faltando. Obrigatório: pagina"})

    data = percorre_json(abre_json(arquivo_origem), 'pagina', pagina, 'subpagina', subpagina)

    if data.get("subpagina"):
        dir_aux = f'{data.get('pagina')}\\{data.get('subpagina')}'
        nome_arquivo = f'{data.get('pagina')}_{data.get('subpagina')}'
    else:
        dir_aux = f'{data.get('pagina')}'
        nome_arquivo = f'{data.get('pagina')}'

    diretorio_csv = os.getcwd() + '\\CSVs\\' + dir_aux
    user = 'Marcel Firkowski'  # Ajustar para pegar o usuário autenticado que fez a requisição
    path_arquivo = download_csv(url_home + data.get('csvDownload'), diretorio_csv, nome_arquivo, user)

    return jsonify(({"status": f"Atualizado com sucesso arquivo {path_arquivo}"}))


@app.route('/')
def index():
    return 'Hello!'


if __name__ == '__main__':
    app.run(debug=True)
