#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scriptLattes
~~~~~~~~~~~~

The main entry point for the command line interface.

Invoke as ``scriptlattes`` (if installed)
or ``python -m scriptlattes`` (no install required).

Usage:
  scriptlattes [options] all CONFIG_FILE [--offline] [--xml|--html]
  scriptlattes [options] obtain CONFIG_FILE [--offline] [--xml|--html]
  scriptlattes [options] extract CONFIG_FILE [--offline] [--xml|--html]
  scriptlattes [options] process CONFIG_FILE [--offline] [--xml|--html]
  scriptlattes [options] report CONFIG_FILE [--offline] [--xml|--html]
  scriptlattes (-h | --help | --version)

Arguments:
  CONFIG_FILE       arquivo de configuração

Options:
  -h --help         show this help message and exit
  --version         show version and exit
  -v --verbose      log debug messages
  -q --quiet        log only warning and error messages

Other:
  --offline         do not try to download data; instead, use persisted data configured in CONFIG_FILE
  --xml             (default) use XML curricula (will search or store 'ID-LATTES.xml' files in cache)
  --html            use HTML curricula (will search or store 'ID-LATTES' files in cache)
"""

from __future__ import absolute_import, unicode_literals

import logging
import sys
from pathlib import Path

import pandas
from configobj import ConfigObj
from docopt import docopt

import scriptLattes
from extract.lattes_xml_parser import LattesXMLParser
from extract.parserLattesHTML import ParserLattesHTML
from extract.parserLattesXML import ParserLattesXML
from fetch.download_html import download_html
from grupo import Grupo
from persist.cache import cache
from persist.store import Store
from qualis.qualis import Qualis
from report.charts.collaboration_graph import CollaborationGraph
from report.web_pages_generator import WebPagesGenerator
from scriptLattes.log import configure_stream
from scriptLattes.util import util, config_migrator
from validate import Validator

logger = logging.getLogger(__name__)

# FIXME: implementar opção de gravar arquivo de configuração padrão (http://www.voidspace.org.uk/python/configobj.html#copy-mode)
# UPDATE: ver config_migrator
default_configuration = u"""
# ---------------------------------------------------------------------------- #
# INFORMAÇÕS GERAIS                                                            #
# ---------------------------------------------------------------------------- #
[geral]
nome_do_grupo = string
arquivo_de_entrada = string
diretorio_de_saida = string
email_do_admin = string
idioma = string(default='PT')
itens_desde_o_ano = integer(min=1990)
itens_ate_o_ano = integer
itens_por_pagina = "integer(min='1'", default='1000')
criar_paginas_jsp = boolean(default='não')
google_analytics_key = string
prefixo = string
diretorio_de_armazenamento_de_cvs = string
diretorio_de_armazenamento_de_doi = string
salvar_informacoes_em_formato_xml = boolean(default='não')

identificar_publicacoes_com_qualis = boolean(default='não')
usar_cache_qualis = boolean(default='sim')
arquivo_areas_qualis = string(default=None)
arquivo_qualis_de_congressos = string(default=None)
arquivo_qualis_de_periodicos = string(default=None)
area_qualis_de_congressos = string(default=None)

tabela_de_pontuacoes_qualis = string(default=None)

# ---------------------------------------------------------------------------- #
# RELATÓRIOS DE PRODUÇÃO EM C,T & A                                            #
# Serão criadas listas de publicações apenas para os  tipos = sim              #
# ---------------------------------------------------------------------------- #
[relatorio]
salvar_publicacoes_em_formato_ris = boolean(default='não')
incluir_artigo_em_periodico = boolean(default='sim')
incluir_livro_publicado = boolean(default='sim')
incluir_capitulo_de_livro_publicado = boolean(default='sim')
incluir_texto_em_jornal_de_noticia = boolean(default='sim')
incluir_trabalho_completo_em_congresso = boolean(default='sim')
incluir_resumo_expandido_em_congresso = boolean(default='sim')
incluir_resumo_em_congresso = boolean(default='sim')
incluir_artigo_aceito_para_publicacao = boolean(default='sim')
incluir_apresentacao_de_trabalho = boolean(default='sim')
incluir_outro_tipo_de_producao_bibliografica = boolean(default='sim')

incluir_software_com_patente = boolean(default='sim')
incluir_software_sem_patente = boolean(default='sim')
incluir_produto_tecnologico = boolean(default='sim')
incluir_processo_ou_tecnica = boolean(default='sim')
incluir_trabalho_tecnico = boolean(default='sim')
incluir_outro_tipo_de_producao_tecnica = boolean(default='sim')

incluir_patente = boolean(default='sim')
incluir_programa_computador = boolean(default='sim')
incluir_desenho_industrial = boolean(default='sim')

incluir_producao_artistica = boolean(default='sim')

# ---------------------------------------------------------------------------- #
# RELATÓRIOS DE ORIENTAÇÕES                                                    #
# ---------------------------------------------------------------------------- #
mostrar_orientacoes = boolean(default='sim')
incluir_orientacao_em_andamento_pos_doutorado = boolean(default='sim')
incluir_orientacao_em_andamento_doutorado = boolean(default='sim')
incluir_orientacao_em_andamento_mestrado = boolean(default='sim')
incluir_orientacao_em_andamento_monografia_de_especializacao = boolean(default='sim')
incluir_orientacao_em_andamento_tcc = boolean(default='sim')
incluir_orientacao_em_andamento_iniciacao_cientifica = boolean(default='sim')
incluir_orientacao_em_andamento_outro_tipo = boolean(default='sim')

incluir_orientacao_concluida_pos_doutorado = boolean(default='sim')
incluir_orientacao_concluida_doutorado = boolean(default='sim')
incluir_orientacao_concluida_mestrado = boolean(default='sim')
incluir_orientacao_concluida_monografia_de_especializacao = boolean(default='sim')
incluir_orientacao_concluida_tcc = boolean(default='sim')
incluir_orientacao_concluida_iniciacao_cientifica = boolean(default='sim')
incluir_orientacao_concluida_outro_tipo = boolean(default='sim')

# ---------------------------------------------------------------------------- #
# RELATÓRIOS ADICIONAIS                                                        #
# ---------------------------------------------------------------------------- #
incluir_projeto = boolean(default='sim')
incluir_premio = boolean(default='sim')
incluir_participacao_em_evento = boolean(default='sim')
incluir_organizacao_de_evento = boolean(default='sim')
incluir_internacionalizacao = boolean(default='não')

# ---------------------------------------------------------------------------- #
# GRAFO DE COLABORAÇÕES                                                        #
# ---------------------------------------------------------------------------- #
[grafo]
mostrar_grafo_de_colaboracoes = boolean(default='sim')
mostrar_todos_os_nos_do_grafo = boolean(default='sim')
considerar_rotulos_dos_membros_do_grupo = boolean(default='sim')
mostrar_aresta_proporcional_ao_numero_de_colaboracoes = boolean(default='sim')

incluir_artigo_em_periodico = boolean(default='sim')
incluir_livro_publicado = boolean(default='sim')
incluir_capitulo_de_livro_publicado = boolean(default='sim')
incluir_texto_em_jornal_de_noticia = boolean(default='sim')
incluir_trabalho_completo_em_congresso = boolean(default='sim')
incluir_resumo_expandido_em_congresso = boolean(default='sim')
incluir_resumo_em_congresso = boolean(default='sim')
incluir_artigo_aceito_para_publicacao = boolean(default='sim')
incluir_apresentacao_de_trabalho = boolean(default='sim')
incluir_outro_tipo_de_producao_bibliografica = boolean(default='sim')

incluir_software_com_patente = boolean(default='sim')
incluir_software_sem_patente = boolean(default='sim')
incluir_produto_tecnologico = boolean(default='sim')
incluir_processo_ou_tecnica = boolean(default='sim')
incluir_trabalho_tecnico = boolean(default='sim')
incluir_outro_tipo_de_producao_tecnica = boolean(default='sim')

incluir_patente = boolean(default='sim')
incluir_programa_computador = boolean(default='sim')
incluir_desenho_industrial = boolean(default='sim')

incluir_producao_artistica = boolean(default='sim')
incluir_grau_de_colaboracao = boolean(default='não')

# ---------------------------------------------------------------------------- #
# MAPA DE GEOLOCALIZAÇÃO                                                       #
# ---------------------------------------------------------------------------- #
[mapa]
mostrar_mapa_de_geolocalizacao = boolean(default='sim')
incluir_membros_do_grupo = boolean(default='sim')
incluir_alunos_de_pos_doutorado = boolean(default='sim')
incluir_alunos_de_doutorado = boolean(default='sim')
incluir_alunos_de_mestrado = boolean(default='não')
"""


def load_config(filename):
    if not config_migrator.is_last_version(filename):
        logger.warn("Atualizando o formato do arquivo de configuração.")
        config_migrator.migrate_config_file(filename)
    spec = default_configuration.split("\n")
    config = ConfigObj(infile=filename, configspec=spec, file_error=False)
    validator = Validator()
    res = config.validate(validator, copy=True)
    return config


def read_list_file(ids_file_path):
    # ids = pandas.read_csv(ids_file_path.open(), sep=None, comment='#', encoding='utf-8', skip_blank_lines=True)
    ids = pandas.read_csv(ids_file_path.open(), sep="[\t,;]", header=None, engine='python',
                          encoding='utf-8', skip_blank_lines=True, converters={0: lambda x: str(x)})
    num_columns = len(ids.columns)
    column_names = ['identificador', 'nome', 'periodo', 'rotulo']
    ids.columns = column_names[:num_columns]
    ids = ids.reindex(columns=column_names, fill_value='')  # Add new columns with empty strings
    ids.periodo.fillna('', inplace=True)
    return ids


def cli():
    arguments = docopt(__doc__, argv=None, help=True, version=scriptLattes.__version__, options_first=False)

    # configure root logger to print to STDERR
    if arguments['--verbose']:
        configure_stream(level='DEBUG')
    elif arguments['--quiet']:
        configure_stream(level='WARNING')
    else:
        configure_stream(level='INFO')

    # launch the command line interface
    logger.info("Executando '{}'".format(' '.join(sys.argv)))

    config_file_path = Path(arguments['CONFIG_FILE'])
    if not config_file_path.exists():
        logger.error("Arquivo de configuração '{}' não existe.".format(config_file_path))
        return -1
    config = load_config(str(config_file_path))

    # configure cache
    if config['geral'].get('diretorio_de_armazenamento_de_cvs'):
        cache_path = util.resolve_file_path(config['geral']['diretorio_de_armazenamento_de_cvs'], config_file_path)
        cache.set_directory(cache_path)
        # FIXME: colocar store como configuração
        store_path = util.resolve_file_path("store.h5", config_file_path)
        store = Store(store_path)

    # configure output directory (for report and some steps in processing)
    output_directory = None
    if config['geral'].get('diretorio_de_saida'):
        output_directory = util.resolve_file_path(config['geral'].get('diretorio_de_saida'), config_file_path)
        if output_directory.exists() and not output_directory.is_dir():
            logger.error("Configuração do diretório de saída não aponta para um diretório: '{}'.".format(output_directory))
        if not output_directory.exists():
            output_directory.mkdir(parents=True)

    ids_file_path = util.find_file(Path(config['geral'].get('arquivo_de_entrada')), config_file_path)
    if not ids_file_path:
        logger.error(
            "Configuração do arquivo de entrada inválida ou não informada: '{} = {}'".format('arquivo_de_entrada', config['geral'].get('arquivo_de_entrada')))
        return -1

    ids_df = read_list_file(ids_file_path)

    group = Grupo(name=config['geral'].get('nome_do_grupo'),
                  ids_df=ids_df,
                  desde_ano=config['geral'].get('itens_desde_o_ano'),
                  ate_ano=config['geral'].get('itens_ate_o_ano'))
    # group.imprimirListaDeParametros()
    # group.imprimirListaDeRotulos()

    use_xml = True if not arguments['--html'] else False  # FIXME: definir opção no arquivo de config?
    if not use_xml:
        logger.warning("Support for HTML CVs is no longer supported.")

    cvs_content = {'html': {}, 'xml': {}}
    if arguments['obtain'] or arguments['extract'] or arguments['process'] or arguments['report']:
        # obter/carregar
        if not arguments['--offline']:
            # download
            for id_lattes in ids_df['identificador']:
                if use_xml:
                    # TODO: tentar usar webservice do CNPq
                    raise "Download de CVs em XML ainda não implementado."
                    # cvs_content['xml'][id_lattes] = cv_xml
                else:  # use html
                    cv_html = download_html(id_lattes)
                    if cache.directory:
                        id_file = cache.new_file(id_lattes)
                        with id_file.open('w') as f:
                            f.write(cv_html)
                            logger.info("CV '{}' armazenado na cache.".format(id_lattes))
                    cvs_content['html'][id_lattes] = cv_html
        else:  # --offline
            # carregar
            if not cache.cache_directory:
                logger.error(
                    "Opção --offline exige que um diretório de cache válido seja usado; verifique seu arquivo de configuração.")
                return -1
            for id_lattes in ids_df['identificador']:
                if id_lattes == '0000000000000000':
                    # se o codigo for '0000000000000000' então serao considerados dados de pessoa estrangeira - sem Lattes.
                    # sera procurada a coautoria endogena com os outros membro.
                    # para isso é necessario indicar o nome abreviado no arquivo .list
                    # FIXME: verificar se ainda funciona
                    raise Exception("FIXME: membro sem lattes ainda não implementado")
                    continue
                try:
                    suffix = '.xml' if use_xml else ''
                    cv_path = (cache.directory / (id_lattes + suffix)).resolve()
                except OSError:
                    logger.warning("O CV {} não existe na cache ('{}'); ignorando.".format(id_lattes, cache.cache_directory))
                    continue

                with cv_path.open(encoding='latin1') as f:
                    cv_lattes_content = f.read()  # py2 dá erros difíceis de consertar # .decode(encoding)#.encode("utf-8")
                logger.debug("Utilizando CV armazenado na cache: {}.".format(cv_path))

                if use_xml:
                    # TODO: verificar se realmente isto é necessário
                    # extended_chars = u''.join(unichr(c) for c in range(127, 65536, 1))  # srange(r"[\0x80-\0x7FF]")
                    # special_chars = ' -'''
                    # cv_lattes_content = cv_lattes_content.decode('iso-8859-1', 'replace') + extended_chars + special_chars
                    cvs_content['xml'][id_lattes] = cv_lattes_content
                else:
                    cvs_content['html'][id_lattes] = cv_lattes_content

    if arguments['extract'] or arguments['process'] or arguments['report']:
        # extrair/carregar
        logger.info("[INICIANDO EXTRAÇÃO]")
        if use_xml:
            # group.extract_cvs_data(ParserLattesXML, cvs_content['xml'])  # obrigatorio
            group.extract_cvs_data(LattesXMLParser, cvs_content['xml'])  # obrigatorio
        else:
            group.extract_cvs_data(ParserLattesHTML, cvs_content['html'])  # obrigatorio

    if arguments['process'] or arguments['report'] or arguments['all']:
        logger.info("[INICIANDO PROCESSAMENTO]")
        # processar/carregar
        group.aggregate_data()
        # FIXME: uncomment group.create_colaboration_matrices()

        if config['geral'].get('identificar_publicacoes_com_qualis'):
            cache_file = None
            if config['geral']['usar_cache_qualis']:
                cache_file = cache.new_file('qualis.data')
            arquivo_qualis_de_periodicos = None
            if config['geral']['arquivo_qualis_de_periodicos']:
                arquivo_qualis_de_periodicos = util.find_file(Path(config['geral']['arquivo_qualis_de_periodicos']), config_file_path)
            arquivo_areas_qualis = None
            if config['geral']['arquivo_areas_qualis']:
                arquivo_areas_qualis = util.find_file(Path(config['geral']['arquivo_areas_qualis']), config_file_path)
            arquivo_qualis_de_congressos = None
            if config['geral']['arquivo_qualis_de_congressos']:
                arquivo_qualis_de_congressos = util.find_file(Path(config['geral']['arquivo_qualis_de_congressos']), config_file_path)
            area_qualis_de_congressos = None
            if config['geral'].get('area_qualis_de_congressos'):
                area_qualis_de_congressos = config['geral']['area_qualis_de_congressos']
            qualis_scoring_table_file = None
            if config['geral'].get('tabela_de_pontuacoes_qualis'):
                qualis_scoring_table_file = util.find_file(Path(config['geral']['tabela_de_pontuacoes_qualis']), config_file_path)
            # FIXME: atualizar extração do qualis (decidir se é melhor um pacote separado); de qualquer forma, é necessário agora extrair da plataforma sucupira
            qualis = Qualis(data_file_path=cache_file,
                            arquivo_qualis_de_periodicos=arquivo_qualis_de_periodicos,
                            arquivo_areas_qualis=arquivo_areas_qualis,
                            arquivo_qualis_de_congressos=arquivo_qualis_de_congressos,
                            area_qualis_de_congressos=area_qualis_de_congressos,
                            scoring_table_path=qualis_scoring_table_file)

            group.identify_publications_qualis(qualis)  # obrigatorio

        # TODO: decidir se é aqui ou em report
        if config['grafo'].get('mostrar_grafo_de_colaboracoes'):
            collaboration_graph = CollaborationGraph(group)
            collaboration_graph.create_all(output_directory,
                                           use_labels=config['grafo'].get('considerar_rotulos_dos_membros_do_grupo'),
                                           show_all_nodes=config['grafo'].get('mostrar_todos_os_nos_do_grafo'),
                                           weight_collaborations=config['grafo'].get('mostrar_aresta_proporcional_ao_numero_de_colaboracoes'))

    if arguments['report']:
        logger.info("[INICIANDO GERAÇÃO DE RELATÓRIO]")
        if config['geral'].get('criar_paginas_jsp'):
            raise Exception("Formato JSP não mais suportado (configuração geral.criar_paginas_jsp)")

        # if config['relatorio']['incluir_internacionalizacao']:
        #     lista_doi = group.calcularInternacionalizacao()  # obrigatorio
        #     if lista_doi and output_directory:
        #         prefix = config['geral']['prefixo'] if config['geral'].get('prefixo') else ''
        #         file_path = output_directory / (prefix + 'internacionalizacao.txt')
        #         save_list_txt(lista_doi, file_path)

        # group.imprimirMatrizesDeFrequencia()

        # # group.gerarGraficosDeBarras() # java charts
        # group.gerarMapaDeGeolocalizacao()  # obrigatorio

        pages = WebPagesGenerator(group, output_directory, admin_email=config['geral'].get('email_do_admin'))  # obrigatorio
        pages.generate()
        # report.file_generator.gerarArquivosTemporarios(group)  # obrigatorio
        util.copy_report_files(output_directory)

        # if config['geral'].get('diretorio_de_armazenamento_de_cvs'):
        #     cache_path = util.resolve_file_path(config['geral']['diretorio_de_armazenamento_de_cvs'], config_file_path)
        #     cache.set_directory(cache_path)
        #     # FIXME: colocar store como configuração
        #     store_path = util.resolve_file_path("store.h5", config_file_path)
        #     store = Store(store_path)
        #
        # ids_file_path = util.find_file(Path(config['geral']['arquivo_de_entrada']), config_file_path)

        # XXX: fluxo antigo; apenas para referência
        # if criarDiretorio('global-diretorio_de_saida')):
        # if 'diretorio_de_saida' in config['geral']:
        # extract
        # group.extract_cvs_data(parser)  # obrigatorio

        # process
        # group.compilarListasDeItems()  # obrigatorio
        # group.identify_publications_qualis()  # obrigatorio
        # group.calcularInternacionalizacao()  # obrigatorio
        # # group.imprimirMatrizesDeFrequencia()

        # report
        # group.gerarGrafosDeColaboracoes()  # obrigatorio
        # # group.gerarGraficosDeBarras() # java charts
        # group.gerarMapaDeGeolocalizacao()  # obrigatorio
        # group.gerarPaginasWeb()  # obrigatorio
        # group.gerarArquivosTemporarios()  # obrigatorio

        # copiar images, css e js
        # copy_report_files(config['global-diretorio_de_saida'])

    # finalizando o processo
    print('\n\n\n[PARA REFERENCIAR/CITAR ESTE SOFTWARE USE]')
    print('    Jesus P. Mena-Chalco & Roberto M. Cesar-Jr.')
    print('    scriptLattes: An open-source knowledge extraction system from the Lattes Platform.')
    print('    Journal of the Brazilian Computer Society, vol.15, n.4, páginas 31-39, 2009.')
    print('    http://dx.doi.org/10.1007/BF03194511')
    print('\n\nscriptLattes executado!')


if __name__ == '__main__':
    # exit using whatever exit code the CLI returned
    sys.exit(cli())
