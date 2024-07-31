import requests

url_base = 'http://localhost:5000/api/atualizaCsv?pagina=Processamento&subPagina=Viníferas'

response = requests.post(url_base)


