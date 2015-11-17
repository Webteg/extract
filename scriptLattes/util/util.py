#!/usr/bin/env python
# encoding: utf-8
import logging
import os
import pkgutil
import re
import shutil
import sys

import Levenshtein
from pathlib import Path
import pkg_resources

logger = logging.getLogger(__name__)


class OutputStream:
    def __init__(self, output, encoding):
        self.encoding = encoding
        self.output = output

    def write(self, text):
        try:
            text = text.decode(self.encoding)
        except:
            try:
                text = text.decode('utf8').encode('iso-8859-1')
            except:
                try:
                    text = text.encode('iso-8859-1')
                except:
                    pass
        try:
            self.output.write(text)
        except:
            try:
                self.output.write(unicode(text))
            except:
                self.output.write('ERRO na impressao')


def resolve_file_path(file_name, config_file_path):
    file_path = Path(file_name)
    if file_path.is_absolute():
        return file_path
    return config_file_path.parent.joinpath(file_path)


def find_file(file_name, config_file_path):
    file_path = Path(file_name)
    if not file_path.exists():
        # Path(config_file_path).parent / file_path
        # file_path = Path(config_file_path).with_name(file_path.name)
        file_path = config_file_path.parent.joinpath(file_path)
        if not file_path.exists():
            logger.error(u"Arquivo de lista de IDs não existe: '{}'".format(file_path))
            return None
    if not file_path.is_file():
        logger.error(u"Caminho para arquivo da lista de IDs '{}' não é um arquivo".format(file_path))
        return None
    return file_path.resolve()


# def buscarArquivo(filepath, arquivoConfiguracao=None):
#     if not arquivoConfiguracao:
#         arquivoConfiguracao = sys.argv[1]
#     curdir = os.path.abspath(os.path.curdir)
#     if not os.path.isfile(filepath) and arquivoConfiguracao:
#         # vamos tentar mudar o diretorio pro atual do arquivo
#         os.chdir(os.path.abspath(os.path.join(arquivoConfiguracao, os.pardir)))
#     if not os.path.isfile(filepath):
#         # se ainda nao existe, tentemos ver se o arquivo não está junto com o config
#         filepath = os.path.abspath(os.path.basename(filepath))
#     else:
#         # se encontramos, definimos então caminho absoluto
#         filepath = os.path.abspath(filepath)
#     os.chdir(curdir)
#     return filepath
#
#
def copiarArquivos(dir):
    base = os.path.abspath('.') + os.path.sep

    try:
        destination = os.path.join(dir, 'css')
        if os.path.exists(destination):
            shutil.rmtree(destination)
        source = pkg_resources.resource_filename('scriptLattes', 'static/css')
        shutil.copytree(source, destination)
    except OSError, e:
        pass  # provavelmente diretório já existe
        logging.warning(e)

    # shutil.copy2(os.path.join(base, 'css', 'scriptLattes.css'), dir)
    # shutil.copy2(os.path.join(base, 'css', 'jquery.dataTables.css'), dir)

    shutil.copy2(os.path.join(base, 'static/images', 'lattesPoint0.png'), dir)
    shutil.copy2(os.path.join(base, 'static/images', 'lattesPoint1.png'), dir)
    shutil.copy2(os.path.join(base, 'static/images', 'lattesPoint2.png'), dir)
    shutil.copy2(os.path.join(base, 'static/images', 'lattesPoint3.png'), dir)
    shutil.copy2(os.path.join(base, 'static/images', 'lattesPoint_shadow.png'), dir)
    shutil.copy2(os.path.join(base, 'static/images', 'doi.png'), dir)

    try:
        destination = os.path.join(dir, 'images')
        if os.path.exists(destination):
            shutil.rmtree(destination)
        shutil.copytree(os.path.join(base, 'static/images'), destination)
    except OSError, e:
        pass  # provavelmente diretório já existe
        logging.warning(e)

    try:
        destination = os.path.join(dir, 'js')
        if os.path.exists(destination):
            shutil.rmtree(destination)
        shutil.copytree(os.path.join(base, 'static/js'), destination)
    except OSError, e:
        pass  # provavelmente diretório já existe
        logging.warning(e)

    # shutil.copy2(os.path.join(base, 'js', 'jquery.min.js'), dir)
    # shutil.copy2(os.path.join(base, 'js', 'highcharts.js'), dir)
    # shutil.copy2(os.path.join(base, 'js', 'exporting.js'), dir)
    # shutil.copy2(os.path.join(base, 'js', 'drilldown.js'), dir)
    # shutil.copy2(os.path.join(base, 'js', 'jquery.dataTables.min.js'), dir)
    # shutil.copy2(os.path.join(base, 'js', 'jquery.dataTables.rowGrouping.js'), dir)

    print "Arquivos salvos em: >>'%s'<<" % os.path.abspath(dir)


# ---------------------------------------------------------------------------- #
def similaridade_entre_cadeias(str1, str2, qualis=False):
    '''
    Compara duas cadeias de caracteres e retorna a medida de similaridade entre elas, entre 0 e 1, onde 1 significa que as cadeias são idênticas ou uma é contida na outra.
    :param str1:
    :param str2:
    :param qualis:
    :return: A medida de similaridade entre as cadeias, de 0 a 1.
    '''
    str1 = str1.strip().lower()
    str2 = str2.strip().lower()

    if len(str1) == 0 or len(str2) == 0:
        return 0

    if len(str1) >= 20 and len(str2) >= 20 and (str1 in str2 or str2 in str1):
        return 1

    if qualis:
        dist = Levenshtein.ratio(str1, str2)
        if len(str1) >= 10 and len(str2) >= 10 and dist >= 0.80:
            # return 1
            return dist

    else:
        if len(str1) >= 10 and len(str2) >= 10 and Levenshtein.distance(str1, str2) <= 5:
            return 1
    return 0


def criarDiretorio(dir):
    if not os.path.exists(dir):
        try:
            os.makedirs(dir)
        ### except OSError as exc:
        except:
            print "\n[ERRO] Não foi possível criar ou atualizar o diretório: " + dir.encode('utf8')
            print "[ERRO] Você conta com as permissões de escrita? \n"
            return 0
    return 1


def get_lattes_url(lattes_id):
    p = re.compile('[a-zA-Z]+')
    if p.match(str(lattes_id)):
        return 'http://buscatextual.cnpq.br/buscatextual/visualizacv.do?id={}'.format(lattes_id)
    else:
        return 'http://lattes.cnpq.br/{}'.format(lattes_id)
