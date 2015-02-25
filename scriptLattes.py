#!/usr/bin/env python 
# encoding: utf-8
#
#
#  scriptLattes V8
# Copyright 2005-2014: Jesús P. Mena-Chalco e Roberto M. Cesar-Jr.
#  http://scriptlattes.sourceforge.net/
#
#
#  Este programa é um software livre; você pode redistribui-lo e/ou 
#  modifica-lo dentro dos termos da Licença Pública Geral GNU como 
#  publicada pela Fundação do Software Livre (FSF); na versão 2 da 
#  Licença, ou (na sua opinião) qualquer versão.
#
#  Este programa é distribuído na esperança que possa ser util, 
#  mas SEM NENHUMA GARANTIA; sem uma garantia implicita de ADEQUAÇÂO a qualquer
#  MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
#  Licença Pública Geral GNU para maiores detalhes.
#
#  Você deve ter recebido uma cópia da Licença Pública Geral GNU
#  junto com este programa, se não, escreva para a Fundação do Software
#  Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
import logging

import warnings
warnings.filterwarnings('ignore')

from scriptLattes.grupo import *

from scriptLattes.util import *

if 'win' in sys.platform.lower():
    os.environ['PATH'] += ";" + os.path.abspath(os.curdir + '\\Graphviz2.36\\bin')
sys.stdout = OutputStream(sys.stdout, sys.stdout.encoding)
sys.stderr = OutputStream(sys.stderr, sys.stdout.encoding)

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(format='%(asctime)s - %(levelname)s (%(name)s) - %(message)s')
    # logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
    # logging.root.setLevel(level=logging.INFO)
    logging.root.setLevel(level=logging.DEBUG)
    logger.info("Executando '{}'".format(' '.join(sys.argv)))

    arquivoConfiguracao = sys.argv[1]
    # os.chdir( os.path.abspath(os.path.join(arquivoConfiguracao, os.pardir)))
    novoGrupo = Grupo(arquivoConfiguracao)
    # novoGrupo.imprimirListaDeParametros()
    novoGrupo.imprimirListaDeRotulos()

    if criarDiretorio(novoGrupo.obterParametro('global-diretorio_de_saida')):
        novoGrupo.carregarDadosCVLattes() #obrigatorio
        novoGrupo.compilarListasDeItems() # obrigatorio
        novoGrupo.identificarQualisEmPublicacoes() # obrigatorio
        novoGrupo.calcularInternacionalizacao() # obrigatorio
        #novoGrupo.imprimirMatrizesDeFrequencia()

        novoGrupo.gerarGrafosDeColaboracoes() # obrigatorio
        #novoGrupo.gerarGraficosDeBarras() # java charts
        novoGrupo.gerarMapaDeGeolocalizacao() # obrigatorio
        novoGrupo.gerarPaginasWeb() # obrigatorio
        novoGrupo.gerarArquivosTemporarios() # obrigatorio

        # copiar imagens e css
        copiarArquivos(novoGrupo.obterParametro('global-diretorio_de_saida'))

        # finalizando o processo
        #print '[AVISO] Quem vê \'Lattes\', não vê coração! B-)'
        #print '[AVISO] Por favor, cadastre-se na página: http://scriptlattes.sourceforge.net\n'
        print '\n\n\n[PARA REFERENCIAR/CITAR ESTE SOFTWARE USE]'
        print '    Jesus P. Mena-Chalco & Roberto M. Cesar-Jr.'
        print '    scriptLattes: An open-source knowledge extraction system from the Lattes Platform.'
        print '    Journal of the Brazilian Computer Society, vol.15, n.4, páginas 31-39, 2009.'
        print '    http://dx.doi.org/10.1007/BF03194511'
        print '\n\nscriptLattes executado!'

# ---------------------------------------------------------------------------- #
def compararCadeias(str1, str2, qualis=False):
    str1 = str1.strip().lower()
    str2 = str2.strip().lower()

    if len(str1)==0 or len(str2)==0:
        return 0

    if len(str1)>=20 and len(str2)>=20 and (str1 in str2 or str2 in str1):
        return 1

    if qualis:
        dist = Levenshtein.ratio(str1, str2)
        if len(str1) >= 10 and len(str2) >= 10 and dist >= 0.90:
            #return 1
            return dist

    else:
        if len(str1)>=10 and len(str2)>=10 and Levenshtein.distance(str1, str2)<=5:
            return 1
    return 0

def criarDiretorio(dir):
    if not os.path.exists(dir):
        try:
            os.makedirs(dir)
        ### except OSError as exc:
        except:
            print "\n[ERRO] Não foi possível criar ou atualizar o diretório: "+dir.encode('utf8')
            print "[ERRO] Você conta com as permissões de escrita? \n"
            return 0
    return 1

