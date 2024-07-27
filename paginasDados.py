class PaginasDados:
    def __init__(self, pagina, cod_pagina, csv_download, item, feature0,
                 subpagina=None, cod_subpagina=None, feature1=None):
        self.pagina = pagina
        self.cod_pagina = cod_pagina
        self.csv_download = csv_download
        self.item = item
        self.feature0 = feature0
        self.subpagina = subpagina
        self.cod_subpagina = cod_subpagina
        self.feature1 = feature1

    def to_dict(self):
        # Cria um dicionário com os atributos do objeto
        data = {
            "pagina": self.pagina,
            "codPagina": self.cod_pagina,
            "subpagina": self.subpagina,
            "codSubpagina": self.cod_subpagina,
            "csvDownload": self.csv_download,
            "item": self.item,
            "feature0": self.feature0,
            "feature1": self.feature1
        }
        # Converte o dicionário para uma string JSON
        return data

