#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scriptlattes.__main__
~~~~~~~~~~~~~~~~~~~~~

The main entry point for the command line interface.

Invoke as ``scriptlattes`` (if installed)
or ``python -m scriptlattes`` (no install required).
"""
from __future__ import absolute_import, unicode_literals
from configobj import ConfigObj
import logging
import sys
from grupo import Grupo

from scriptLattes.log import configure_stream
from util import criarDiretorio, copiarArquivos
from validate import Validator

logger = logging.getLogger(__name__)


def load_config(filename):
    spec = """
    global-nome_do_grupo = ''])
    global-arquivo_de_entrada = ''])
    global-diretorio_de_saida = ''])
    global-email_do_admin = ''])
    global-idioma = 'PT'])
    global-itens_desde_o_ano = ''])
    global-itens_ate_o_ano = ''])  # hoje
    global-itens_por_pagina = '1000'])
    global-criar_paginas_jsp = 'nao'])
    global-google_analytics_key = ''])
    global-prefixo = ''])
    global-diretorio_de_armazenamento_de_cvs = ''])
    global-diretorio_de_armazenamento_de_doi = ''])
    global-salvar_informacoes_em_formato_xml = 'nao'])

    global-identificar_publicacoes_com_qualis = 'nao'])
    global-usar_cache_qualis = 'sim'])
    global-arquivo_areas_qualis = ''])
    global-arquivo_qualis_de_congressos = ''])
    global-arquivo_qualis_de_periodicos = ''])

    relatorio-salvar_publicacoes_em_formato_ris = 'nao'])
    relatorio-incluir_artigo_em_periodico = 'sim'])
    relatorio-incluir_livro_publicado = 'sim'])
    relatorio-incluir_capitulo_de_livro_publicado = 'sim'])
    relatorio-incluir_texto_em_jornal_de_noticia = 'sim'])
    relatorio-incluir_trabalho_completo_em_congresso = 'sim'])
    relatorio-incluir_resumo_expandido_em_congresso = 'sim'])
    relatorio-incluir_resumo_em_congresso = 'sim'])
    relatorio-incluir_artigo_aceito_para_publicacao = 'sim'])
    relatorio-incluir_apresentacao_de_trabalho = 'sim'])
    relatorio-incluir_outro_tipo_de_producao_bibliografica = 'sim'])

    relatorio-incluir_software_com_patente = 'sim'])
    relatorio-incluir_software_sem_patente = 'sim'])
    relatorio-incluir_produto_tecnologico = 'sim'])
    relatorio-incluir_processo_ou_tecnica = 'sim'])
    relatorio-incluir_trabalho_tecnico = 'sim'])
    relatorio-incluir_outro_tipo_de_producao_tecnica = 'sim'])

    relatorio-incluir_patente = 'sim'])
    relatorio-incluir_programa_computador = 'sim'])
    relatorio-incluir_desenho_industrial = 'sim'])

    relatorio-incluir_producao_artistica = 'sim'])

    relatorio-mostrar_orientacoes = 'sim'])
    relatorio-incluir_orientacao_em_andamento_pos_doutorado = 'sim'])
    relatorio-incluir_orientacao_em_andamento_doutorado = 'sim'])
    relatorio-incluir_orientacao_em_andamento_mestrado = 'sim'])
    relatorio-incluir_orientacao_em_andamento_monografia_de_especializacao = 'sim'])
    relatorio-incluir_orientacao_em_andamento_tcc = 'sim'])
    relatorio-incluir_orientacao_em_andamento_iniciacao_cientifica = 'sim'])
    relatorio-incluir_orientacao_em_andamento_outro_tipo = 'sim'])

    relatorio-incluir_orientacao_concluida_pos_doutorado = 'sim'])
    relatorio-incluir_orientacao_concluida_doutorado = 'sim'])
    relatorio-incluir_orientacao_concluida_mestrado = 'sim'])
    relatorio-incluir_orientacao_concluida_monografia_de_especializacao = 'sim'])
    relatorio-incluir_orientacao_concluida_tcc = 'sim'])
    relatorio-incluir_orientacao_concluida_iniciacao_cientifica = 'sim'])
    relatorio-incluir_orientacao_concluida_outro_tipo = 'sim'])

    relatorio-incluir_projeto = 'sim'])
    relatorio-incluir_premio = 'sim'])
    relatorio-incluir_participacao_em_evento = 'sim'])
    relatorio-incluir_organizacao_de_evento = 'sim'])
    relatorio-incluir_internacionalizacao = 'nao'])

    grafo-mostrar_grafo_de_colaboracoes = 'sim'])
    grafo-mostrar_todos_os_nos_do_grafo = 'sim'])
    grafo-considerar_rotulos_dos_membros_do_grupo = 'sim'])
    grafo-mostrar_aresta_proporcional_ao_numero_de_colaboracoes = 'sim'])

    grafo-incluir_artigo_em_periodico = 'sim'])
    grafo-incluir_livro_publicado = 'sim'])
    grafo-incluir_capitulo_de_livro_publicado = 'sim'])
    grafo-incluir_texto_em_jornal_de_noticia = 'sim'])
    grafo-incluir_trabalho_completo_em_congresso = 'sim'])
    grafo-incluir_resumo_expandido_em_congresso = 'sim'])
    grafo-incluir_resumo_em_congresso = 'sim'])
    grafo-incluir_artigo_aceito_para_publicacao = 'sim'])
    grafo-incluir_apresentacao_de_trabalho = 'sim'])
    grafo-incluir_outro_tipo_de_producao_bibliografica = 'sim'])

    grafo-incluir_software_com_patente = 'sim'])
    grafo-incluir_software_sem_patente = 'sim'])
    grafo-incluir_produto_tecnologico = 'sim'])
    grafo-incluir_processo_ou_tecnica = 'sim'])
    grafo-incluir_trabalho_tecnico = 'sim'])
    grafo-incluir_outro_tipo_de_producao_tecnica = 'sim'])

    grafo-incluir_patente = 'sim'])
    grafo-incluir_programa_computador = 'sim'])
    grafo-incluir_desenho_industrial = 'sim'])

    grafo-incluir_producao_artistica = 'sim'])
    grafo-incluir_grau_de_colaboracao = 'nao'])

    mapa-mostrar_mapa_de_geolocalizacao = 'sim'])
    mapa-incluir_membros_do_grupo = 'sim'])
    mapa-incluir_alunos_de_pos_doutorado = 'sim'])
    mapa-incluir_alunos_de_doutorado = 'sim'])
    mapa-incluir_alunos_de_mestrado = 'nao'])
    """
    spec = spec.split("\n")
    config = ConfigObj(infile=filename, configspec=spec, file_error=False)
    validator = Validator()
    config.validate(validator, copy=True)



def cli():
    """Add some useful functionality here or import from a submodule."""
    # configure root logger to print to STDERR
    configure_stream(level='DEBUG')

    # launch the command line interface
    logger.info("Executando '{}'".format(' '.join(sys.argv)))

    # FIXME: use docopt for command line arguments (or argparse)
    config = load_config(sys.argv[1])

    # os.chdir( os.path.abspath(os.path.join(config_file, os.pardir)))
    group = Grupo(config_file)
    # group.imprimirListaDeParametros()
    group.imprimirListaDeRotulos()

    if criarDiretorio(group.obterParametro('global-diretorio_de_saida')):
        group.carregarDadosCVLattes()  # obrigatorio
        group.compilarListasDeItems()  # obrigatorio
        group.identificarQualisEmPublicacoes()  # obrigatorio
        group.calcularInternacionalizacao()  # obrigatorio
        # group.imprimirMatrizesDeFrequencia()

        group.gerarGrafosDeColaboracoes()  # obrigatorio
        # group.gerarGraficosDeBarras() # java charts
        group.gerarMapaDeGeolocalizacao()  # obrigatorio
        group.gerarPaginasWeb()  # obrigatorio
        group.gerarArquivosTemporarios()  # obrigatorio

        # copiar images e css
        copiarArquivos(group.obterParametro('global-diretorio_de_saida'))

        # finalizando o processo
        print('\n\n\n[PARA REFERENCIAR/CITAR ESTE SOFTWARE USE]')
        print('    Jesus P. Mena-Chalco & Roberto M. Cesar-Jr.')
        print('    scriptLattes: An open-source knowledge extraction system from the Lattes Platform.')
        print('    Journal of the Brazilian Computer Society, vol.15, n.4, páginas 31-39, 2009.')
        print('    http://dx.doi.org/10.1007/BF03194511')
        print('\n\nscriptLattes executado!')

        # return 0


if __name__ == '__main__':
    # exit using whatever exit code the CLI returned
    sys.exit(cli())
