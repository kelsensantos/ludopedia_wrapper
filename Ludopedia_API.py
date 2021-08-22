import requests
import json
from math import ceil
from decouple import config
from Connection import Connection


class Ludopedia:
    """ Consome os métodos da API da Ludopedia. """

    def __init__(self, conf_file=config('APP_CONF_PATH', default='app_conf.json')):
        self.conexao = Connection(conf_file=conf_file)
        self.headers = {
                "Content-type": "aplication-json",
                "Authorization": f"Bearer {self.conexao.ACCESS_TOKEN}"
            }

    def _request_json(self, url):
        """ Realiza consulta e obtém resposta em formato json. """
        response = requests.get(url, headers=self.headers)
        response_json = json.loads(response.text)
        return response_json

    @staticmethod
    def _mount_url(url, first=True, **kwargs):
        """ Monta a URL para requisição a partir de dicinário com parâmetros.
        Todos os parâmetros precisam ser informados a partir do inicial,
        ou seja, a url de entrada não poder conter outros patrâmetros pré-definidos. """
        mounted_url = url
        for item in kwargs.keys():
            complemento = kwargs.get(item)
            if first:
                mounted_url = mounted_url + '?' + str(item) + '=' + str(complemento)
            else:
                mounted_url = mounted_url + '&' + str(item) + '=' + str(complemento)
            first = False
        return mounted_url

    @staticmethod
    def _modelar_kwargs(**kwargs):
        return kwargs

    def get_endpoint(self, url, **kwargs):
        """ Método genérico para consumir de qualquer endpoint via get. """
        url = Ludopedia._mount_url(url, **kwargs)
        response = self._request_json(url)
        return response

    def buscar_colecao(self, todos=True, lista='colecao', ordem='nome', page=1, rows=100, **kwargs):
        """ Método para consumir do endpoint "colecao". """
        if todos and page != 1:
            print('Só possível retornar todos a partir da primeira página. Se for o caso, corriga o parâmetro.')
        url = 'https://ludopedia.com.br/api/v1/colecao'
        url = Ludopedia._mount_url(
            url,
            lista=lista,
            rows=rows,
            ordem=ordem,
            page=page,
            **kwargs
        )
        print(f'Obtendo dados de {url} ...')
        response = self._request_json(url)
        # implementa atributo para buscar todos os jogos (default: true)
        if todos and page == 1:
            total_de_paginas = ceil(response["total"] / rows)
            jogos = response["colecao"]
            print(f'Total de páginas: {total_de_paginas}')
            for page in range(2, total_de_paginas + 1):
                proxima_pagina = self.buscar_colecao(page=page)
                jogos += proxima_pagina["colecao"]
            response = jogos
        return response
