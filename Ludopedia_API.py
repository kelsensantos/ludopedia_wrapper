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
        self.base_url = 'https://ludopedia.com.br/api/v1'

    def _request_json(self, url):
        """ Realiza consulta e obtém resposta em formato json. """
        response = requests.get(url, headers=self.headers)
        response_json = json.loads(response.text)
        return response_json

    def _mount_url(self, endpoint, first_parameter=True, **kwargs):
        """ Monta a URL para requisição a partir de dicinário com parâmetros.
        Todos os parâmetros precisam ser informados a partir do inicial,
        ou seja, a url de entrada não poder conter outros patrâmetros pré-definidos. """
        mounted_url = self.base_url + endpoint
        for item in kwargs.keys():
            complemento = kwargs.get(item)
            if first_parameter:
                mounted_url = mounted_url + '?' + str(item) + '=' + str(complemento)
            else:
                mounted_url = mounted_url + '&' + str(item) + '=' + str(complemento)
            first_parameter = False
        return mounted_url

    @staticmethod
    def _modelar_kwargs(**kwargs):
        return kwargs

    def get_endpoint(self, endpoint, **kwargs):
        """ Método genérico para consumir de qualquer endpoint via get. """
        url = self._mount_url(endpoint, **kwargs)
        response = self._request_json(url)
        return response

    def post_endpoint(self, endpoint, payload):
        """ Método genérico para consumir de qualquer endpoint via get. """
        url = self.base_url + endpoint
        response = requests.post(url, data=payload, headers=self.headers)
        return response

    def buscar_colecao(self, todos=True, lista='colecao', ordem='nome', page=1, rows=100, **kwargs):
        """ Método para consumir do endpoint "colecao". """
        if todos and page != 1:
            print('Só possível retornar todos a partir da primeira página. Se for o caso, corriga o parâmetro.')
        endpoint = '/colecao'
        url = self._mount_url(
            endpoint=endpoint,
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
        # acrescenta coluna base_game (true/false)
        return response

    def buscar_jogo_na_colecao(self, id_jogo, retornar_somente_tags=False):
        """ Retorna a relação do usuário com o jogo (Nota, Comentario, coleção, etc). """
        endpoint = f'/colecao/item/{id_jogo}'
        url = self._mount_url(endpoint)
        print(f'Obtendo dados de {url} ...')
        response = self._request_json(url)
        if retornar_somente_tags:
            tags_list = []
            for tag in response['tags']:
                tags_list.append(tag['nm_tag'])
            return tags_list
        return response

    def buscar_jogo_detalhes(self, id_jogo):
        """ Busca os detalhes de um jogo, consumindo o endpoint /jogos/id_jogo. """
        endpoint = f'/jogos/{id_jogo}'
        url = self._mount_url(endpoint)
        print(f'Obtendo dados de {url} ...')
        response = self._request_json(url)
        return response

    # noinspection PyTypeChecker
    def atualizar_jogo_na_colecao(self, id_jogo, **kwargs):
        # define endpoint
        endpoint = '/colecao'
        # busca dados atuais do jogo
        dados = self.buscar_jogo_na_colecao(id_jogo)
        # lista de chaves exigidas pela API
        keys = ['id_jogo', 'fl_tem', 'fl_quer', 'fl_teve', 'fl_jogou', 'comentario', 'comentario_privado', 'vl_nota',
                'vl_custo', 'tags']
        # altera dados
        for kwarg in kwargs:
            if kwarg not in keys:
                return f'Parâmetro {kwarg} não existe. Por favor, corrija.'
            else:
                dados[kwarg] = kwargs[kwarg]
        # filtra dicionário para selecionar chaves exigidas pela API
        payload = {key: dados[key] for key in keys}
        # realiza requisição
        r = self.post_endpoint(endpoint, json.dumps(payload))
        # debug
        print(f"Alterando dados de {dados['nm_jogo']}...")
        return r
