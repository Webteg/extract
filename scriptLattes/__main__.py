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
import logging
import sys
from grupo import Grupo

from scriptLattes.log import configure_stream
from util import criarDiretorio, copiarArquivos

logger = logging.getLogger(__name__)


def cli():
    """Add some useful functionality here or import from a submodule."""
    # configure root logger to print to STDERR
    configure_stream(level='DEBUG')

    # launch the command line interface
    logger.info("Executando '{}'".format(' '.join(sys.argv)))

    config_file = sys.argv[1]
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
