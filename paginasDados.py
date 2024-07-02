class PaginasDados:
    def __init__(self, url, nome_pagina, categoria0, sub_option=None, categoria1=None, categoria2=None):
        self.url = url
        self.nome_pagina = nome_pagina
        self.sub_option = sub_option
        self.categoria0 = categoria0
        self.categoria1 = categoria1
        self.categoria2 = categoria2

    def print_data(self):
        dados = self.url + ", " + self.nome_pagina
        if self.sub_option is not None:
            dados += ", " + self.sub_option
        dados += ", " + self.categoria0
        if self.categoria1 is not None:
            dados += ", " + self.categoria1
        if self.categoria2 is not None:
            dados += ", " + self.categoria2
        return print(dados)

