import requests

urls = [
    'download/Producao.csv',
    'download/ProcessaViniferas.csv',
    'download/ProcessaAmericanas.csv',
    'download/ProcessaMesa.csv',
    'download/ProcessaSemclass.csv',
    'download/Comercio.csv',
    'download/ImpVinhos.csv',
    'download/ImpEspumantes.csv',
    'download/ImpFrescas.csv',
    'download/ImpPassas.csv',
    'download/ImpSuco.csv',
    'download/ExpVinho.csv',
    'download/ExpEspumantes.csv',
    'download/ExpUva.csv',
    'download/ExpSuco.csv'
]

url_base = 'http://localhost:5000/api/atualizaCsv?csvDownload='

for i in urls:
    url = url_base + i
    response = requests.post(url)


