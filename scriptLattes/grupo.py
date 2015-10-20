#!/usr/bin/python
# encoding: utf-8
# filename: grupo.py

import fileinput
import unicodedata
import pandas

from geradorDeXML import *
from qualis import qualis
from scriptLattes.util import *

import util
from membro import Membro
from compiladorDeListas import CompiladorDeListas
from authorRank import AuthorRank
from geradorDePaginasWeb import GeradorDePaginasWeb


class Grupo:
    compilador = None
    listaDeParametros = []
    listaDeMembros = []
    listaDeRotulos = []
    listaDeRotulosCores = []
    listaDePublicacoesEinternacionalizacao = []

    matrizArtigoEmPeriodico = None
    matrizLivroPublicado = None
    matrizCapituloDeLivroPublicado = None
    matrizTextoEmJornalDeNoticia = None
    matrizTrabalhoCompletoEmCongresso = None
    matrizResumoExpandidoEmCongresso = None
    matrizResumoEmCongresso = None
    matrizArtigoAceito = None
    matrizApresentacaoDeTrabalho = None
    matrizOutroTipoDeProducaoBibliografica = None
    matrizSoftwareComPatente = None
    matrizSoftwareSemPatente = None
    matrizProdutoTecnologico = None
    matrizProcessoOuTecnica = None
    matrizTrabalhoTecnico = None
    matrizOutroTipoDeProducaoTecnica = None
    matrizProducaoArtistica = None

    matrizPatente = None
    matrizProgramaComputador = None
    matrizDesenhoIndustrial = None

    matrizDeAdjacencia = None
    matrizDeFrequencia = None
    matrizDeFrequenciaNormalizada = None
    vetorDeCoAutoria = None
    grafosDeColaboracoes = None
    mapaDeGeolocalizacao = None
    geradorDeXml = None

    vectorRank = None
    nomes = None
    rotulos = None
    geolocalizacoes = None

    qualis = None

    def __init__(self, ids_file_path, desde_ano=0, ate_ano=None):

        if desde_ano is None or type(desde_ano) is str and desde_ano.lower() == 'hoje':
            desde_ano = str(datetime.datetime.now().year)
        if ate_ano is None or type(ate_ano) is str and ate_ano.lower() == 'hoje':
            ate_ano = str(datetime.datetime.now().year)

        self.items_desde_ano = desde_ano
        self.items_ate_ano = ate_ano

        # FIXME: onde que isto é usado?
        # self.diretorioDoi = self.obterParametro('global-diretorio_de_armazenamento_de_doi')
        # if not self.diretorioDoi == '':
        #     util.criarDiretorio(self.diretorioDoi)

        # carregamos a lista de membros
        ids = pandas.read_csv(ids_file_path, sep=None, comment='#', encoding='utf-8', skip_blank_lines=True)

        idSequencial = 0
        for linha in fileinput.input(ids_file_path.decode('utf8')):
            linha = linha.replace("\r", "")
            linha = linha.replace("\n", "")

            linhaPart = linha.partition("#")  # eliminamos os comentários
            linhaDiv = linhaPart[0].split(",")
            if ';' in linhaPart[0] and len(linhaDiv) < 2:
                linhaDiv = linhaPart[0].split(";")
            if '\t' in linhaPart[0] and len(linhaDiv) < 2:
                linhaDiv = linhaPart[0].split("\t")

            if linhaDiv[0].strip():
                identificador = linhaDiv[0].strip() if len(linhaDiv) > 0 else ''
                nome = linhaDiv[1].strip() if len(linhaDiv) > 1 else ''
                periodo = linhaDiv[2].strip() if len(linhaDiv) > 2 else ''
                rotulo = linhaDiv[3].strip() if len(linhaDiv) > 3 and linhaDiv[3].strip() else '[Sem rotulo]'
                # rotulo        = rotulo.capitalize()

                # atribuicao dos valores iniciais para cada membro
                ###if 'xml' in identificador.lower():
                ###### self.listaDeMembros.append(Membro(idSequencial, '', nome, periodo, rotulo, self.items_desde_ano, self.items_ate_ano, xml=identificador))
                ###	self.listaDeMembros.append(Membro(idSequencial, identificador, nome, periodo, rotulo, self.items_desde_ano, self.items_ate_ano, diretorioCache))
                ###else:
                self.listaDeMembros.append(
                    Membro(idSequencial, identificador, nome, periodo, rotulo, self.items_desde_ano, self.items_ate_ano))

                self.listaDeRotulos.append(rotulo)
                idSequencial += 1

        self.listaDeRotulos = list(set(self.listaDeRotulos))  # lista unica de rotulos
        self.listaDeRotulos.sort()
        self.listaDeRotulosCores = [''] * len(self.listaDeRotulos)

        if self.obterParametro('global-identificar_publicacoes_com_qualis'):
            read_from_cache = self.obterParametro('global-usar_cache_qualis')
            qualis_de_congressos = self.obterParametro('global-arquivo_qualis_de_congressos')
            areas_qualis = self.obterParametro('global-arquivo_areas_qualis')

            self.qualis = qualis.Qualis(read_from_cache=read_from_cache,
                                        data_file_path=self.diretorioCache + '/qualis.data',
                                        arquivo_qualis_de_congressos=qualis_de_congressos,
                                        arquivo_areas_qualis=areas_qualis)

    def gerarXMLdeGrupo(self):
        if self.obterParametro('global-salvar_informacoes_em_formato_xml'):
            self.geradorDeXml = GeradorDeXML(self)
            self.geradorDeXml.gerarXmlParaGrupo()

            if self.geradorDeXml.listaErroXml:
                print "\n\n[AVISO] Erro ao gerar XML para os lattes abaixo:"
                for item in self.geradorDeXml.listaErroXml:
                    print "- [ID Lattes: " + item + "]"

    def gerarCSVdeQualisdeGrupo(self):
        prefix = self.obterParametro('global-prefixo') + '-' if not self.obterParametro('global-prefixo') == '' else ''

        # Salvamos a lista individual
        s = ""
        for membro in self.listaDeMembros:
            s += self.imprimeCSVListaIndividual(membro.nomeCompleto, membro.listaArtigoEmPeriodico)
            s += self.imprimeCSVListaIndividual(membro.nomeCompleto, membro.listaTrabalhoCompletoEmCongresso)
            s += self.imprimeCSVListaIndividual(membro.nomeCompleto, membro.listaResumoExpandidoEmCongresso)
        self.salvarArquivoGenerico(s, prefix + 'publicacoesPorMembro.csv')

        # Salvamos a lista total (publicações do grupo)
        s = ""
        s += self.imprimeCSVListaGrupal(self.compilador.listaCompletaArtigoEmPeriodico)
        s += self.imprimeCSVListaGrupal(self.compilador.listaCompletaTrabalhoCompletoEmCongresso)
        s += self.imprimeCSVListaGrupal(self.compilador.listaCompletaResumoExpandidoEmCongresso)
        self.salvarArquivoGenerico(s, prefix + 'publicacoesDoGrupo.csv')

    def gerarCSVdeQualisdeGrupoOld(self):
        if self.obterParametro('global-identificar_publicacoes_com_qualis'):
            prefix = self.obterParametro('global-prefixo') + '-' if not self.obterParametro(
                'global-prefixo') == '' else ''

            # Salvamos a lista individual
            s = ""
            for membro in self.listaDeMembros:
                if (not self.obterParametro('global-arquivo_qualis_de_periodicos') == ''):
                    s += self.imprimeCSVListaIndividual(membro.nomeCompleto, membro.listaArtigoEmPeriodico)
                if (not self.obterParametro('global-arquivo_qualis_de_congressos') == ''):
                    s += self.imprimeCSVListaIndividual(membro.nomeCompleto, membro.listaTrabalhoCompletoEmCongresso)
                    s += self.imprimeCSVListaIndividual(membro.nomeCompleto, membro.listaResumoExpandidoEmCongresso)
            self.salvarArquivoGenerico(s, prefix + 'qualisPorMembro.csv')

            # Salvamos a lista total (publicações do grupo)
            s = ""
            if (not self.obterParametro('global-arquivo_qualis_de_periodicos') == ''):
                s += self.imprimeCSVListaGrupal(self.compilador.listaCompletaArtigoEmPeriodico)
            if (not self.obterParametro('global-arquivo_qualis_de_congressos') == ''):
                s += self.imprimeCSVListaGrupal(self.compilador.listaCompletaTrabalhoCompletoEmCongresso)
                s += self.imprimeCSVListaGrupal(self.compilador.listaCompletaResumoExpandidoEmCongresso)
            self.salvarArquivoGenerico(s, prefix + 'qualisGrupal.csv')

    def gerarArquivosTemporarios(self):
        print "\n[CRIANDO ARQUIVOS TEMPORARIOS: CSV, RIS, TXT, GDF]"

        self.gerarRISdeMembros()
        self.gerarCSVdeQualisdeGrupo()
        self.gerarXMLdeGrupo()

        # Salvamos alguns dados para análise posterior (com outras ferramentas)
        prefix = self.obterParametro('global-prefixo') + '-' if not self.obterParametro('global-prefixo') == '' else ''

        # (1) matrizes
        self.salvarMatrizTXT(self.matrizDeAdjacencia, prefix + "matrizDeAdjacencia.txt")
        self.salvarMatrizTXT(self.matrizDeFrequencia, prefix + "matrizDeFrequencia.txt")
        self.salvarMatrizTXT(self.matrizDeFrequenciaNormalizada, prefix + "matrizDeFrequenciaNormalizada.txt")
        # self.salvarMatrizXML(self.matrizDeAdjacencia, prefix+"matrizDeAdjacencia.xml")

        # (2) listas de nomes, rótulos, ids
        self.salvarListaTXT(self.nomes, prefix + "listaDeNomes.txt")
        self.salvarListaTXT(self.rotulos, prefix + "listaDeRotulos.txt")
        self.salvarListaTXT(self.ids, prefix + "listaDeIDs.txt")

        # (3) medidas de authorRanks
        self.salvarListaTXT(self.vectorRank, prefix + "authorRank.txt")

        # (4) lista unica de colaboradores (orientadores, ou qualquer outro tipo de parceiros...)
        rawColaboradores = list([])
        for membro in self.listaDeMembros:
            for idColaborador in membro.listaIDLattesColaboradoresUnica:
                rawColaboradores.append(idColaborador)
        rawColaboradores = list(set(rawColaboradores))
        self.salvarListaTXT(rawColaboradores, prefix + "colaboradores.txt")

        # (5) Geolocalizacoes
        self.geolocalizacoes = list([])
        for membro in self.listaDeMembros:
            self.geolocalizacoes.append(str(membro.enderecoProfissionalLat) + "," + str(membro.enderecoProfissionalLon))
        self.salvarListaTXT(self.geolocalizacoes, prefix + "listaDeGeolocalizacoes.txt")

        # (6) arquivo GDF
        self.gerarArquivoGDF(prefix + "rede.gdf")

    def gerarArquivoGDF(self, nomeArquivo):
        # Vêrtices
        N = len(self.listaDeMembros)
        string = "nodedef> name VARCHAR, idLattes VARCHAR, label VARCHAR, rotulo VARCHAR, lat DOUBLE, lon DOUBLE, collaborationRank DOUBLE, producaoBibliografica DOUBLE, artigoEmPeriodico DOUBLE, livro DOUBLE, capituloDeLivro DOUBLE, trabalhoEmCongresso DOUBLE, resumoExpandido DOUBLE, resumo DOUBLE, color VARCHAR"
        i = 0
        for membro in self.listaDeMembros:
            nomeCompleto = unicodedata.normalize('NFKD', membro.nomeCompleto).encode('ASCII', 'ignore')
            string += "\n" + str(
                i) + "," + membro.idLattes + "," + nomeCompleto + "," + membro.rotulo + "," + membro.enderecoProfissionalLat + "," + membro.enderecoProfissionalLon + ","
            string += str(self.vectorRank[i]) + ","
            string += str(len(membro.listaArtigoEmPeriodico) + len(membro.listaLivroPublicado) + len(
                membro.listaCapituloDeLivroPublicado) + len(membro.listaTrabalhoCompletoEmCongresso) + len(
                membro.listaResumoExpandidoEmCongresso) + len(membro.listaResumoEmCongresso)) + ","
            string += str(len(membro.listaArtigoEmPeriodico)) + ","
            string += str(len(membro.listaLivroPublicado)) + ","
            string += str(len(membro.listaCapituloDeLivroPublicado)) + ","
            string += str(len(membro.listaTrabalhoCompletoEmCongresso)) + ","
            string += str(len(membro.listaResumoExpandidoEmCongresso)) + ","
            string += str(len(membro.listaResumoEmCongresso)) + ","
            string += "'" + self.HTMLColorToRGB(membro.rotuloCorBG) + "'"
            i += 1

        # Arestas
        matriz = self.matrizDeAdjacencia

        string += "\nedgedef> node1 VARCHAR, node2 VARCHAR, weight DOUBLE"
        for i in range(0, N):
            for j in range(i + 1, N):
                if (i != j) and (matriz[i, j] > 0):
                    string += '\n' + str(i) + ',' + str(j) + ',' + str(matriz[i, j])


        # gerando o arquivo GDF
        dir = self.obterParametro('global-diretorio_de_saida')
        arquivo = open(dir + "/" + nomeArquivo, 'w')
        arquivo.write(string)  # .encode("utf8","ignore"))
        arquivo.close()

    def HTMLColorToRGB(self, colorstring):
        colorstring = colorstring.strip()
        if colorstring[0] == '#': colorstring = colorstring[1:]
        r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
        r, g, b = [int(n, 16) for n in (r, g, b)]
        #return (r, g, b)
        return str(r) + "," + str(g) + "," + str(b)

    def imprimeCSVListaIndividual(self, nomeCompleto, lista):
        s = ""
        for pub in lista:
            s += pub.csv(nomeCompleto).encode('utf8') + "\n"
        return s

    def imprimeCSVListaGrupal(self, listaCompleta):
        s = ""
        keys = listaCompleta.keys()
        keys.sort(reverse=True)

        if len(keys) > 0:
            for ano in keys:
                elementos = listaCompleta[ano]
                elementos.sort(key=lambda x: x.chave.lower())
                for index in range(0, len(elementos)):
                    pub = elementos[index]
                    s += pub.csv().encode('utf8') + "\n"
        return s

    def gerarRISdeMembros(self):
        prefix = self.obterParametro('global-prefixo') + '-' if not self.obterParametro('global-prefixo') == '' else ''
        s = ""
        for membro in self.listaDeMembros:
            s += membro.ris().encode('utf8') + "\n"
        self.salvarArquivoGenerico(s, prefix + 'membros.ris')

    def salvarArquivoGenerico(self, conteudo, nomeArquivo):
        dir = self.obterParametro('global-diretorio_de_saida')
        arquivo = open(dir + "/" + nomeArquivo, 'w')
        arquivo.write(conteudo)
        arquivo.close()

    def carregarDadosCVLattes(self):
        indice = 1
        for membro in self.listaDeMembros:
            print('\n[LENDO REGISTRO LATTES: {0}o. DA LISTA]'.format(indice))
            indice += 1
            membro.carregarDadosCVLattes()
            membro.filtrarItemsPorPeriodo()
            print membro

    def gerarMapaDeGeolocalizacao(self):
        if self.obterParametro('mapa-mostrar_mapa_de_geolocalizacao'):
            self.mapaDeGeolocalizacao = MapaDeGeolocalizacao(self)

    def gerarPaginasWeb(self):
        paginasWeb = GeradorDePaginasWeb(self)

    def compilarListasDeItems(self):
        self.compilador = CompiladorDeListas(self)  # compilamos todo e criamos 'listasCompletas'

        # Grafos de coautoria
        self.compilador.criarMatrizesDeColaboracao()

        [self.matrizDeAdjacencia, self.matrizDeFrequencia] = self.compilador.uniaoDeMatrizesDeColaboracao()
        self.vetorDeCoAutoria = self.matrizDeFrequencia.sum(
            axis=1)  # suma das linhas = num. de items feitos em co-autoria (parceria) com outro membro do grupo
        self.matrizDeFrequenciaNormalizada = self.matrizDeFrequencia.copy()

        for i in range(0, self.numeroDeMembros()):
            if not self.vetorDeCoAutoria[i] == 0:
                self.matrizDeFrequenciaNormalizada[i, :] /= float(self.vetorDeCoAutoria[i])

        # AuthorRank
        authorRank = AuthorRank(self.matrizDeFrequenciaNormalizada, 100)
        self.vectorRank = authorRank.vectorRank

        # listas de nomes, rotulos e IDs
        self.nomes = list([])
        self.rotulos = list([])
        self.ids = list([])
        for membro in self.listaDeMembros:
            self.nomes.append(membro.nomeCompleto)
            self.rotulos.append(membro.rotulo)
            self.ids.append(membro.idLattes)

    def identificarQualisEmPublicacoes(self):
        if self.obterParametro('global-identificar_publicacoes_com_qualis'):
            print "\n[IDENTIFICANDO QUALIS EM PUBLICAÇÕES]"
            for membro in self.listaDeMembros:
                self.qualis.analisar_publicacoes(membro)  # Qualis - Adiciona Qualis as publicacoes dos membros

            # if self.diretorioCache:
            filename = (self.diretorioCache or '/tmp') + '/qualis.data'
            # self.qualis.qextractor.save_data(self.diretorioCache + '/' + filename)
            self.qualis.qextractor.save_data(filename)

            self.qualis.calcular_totais_dos_qualis(self.compilador.listaCompletaArtigoEmPeriodico, self.compilador.listaCompletaTrabalhoCompletoEmCongresso,
                        self.compilador.listaCompletaResumoExpandidoEmCongresso)

    def salvarListaTXT(self, lista, nomeArquivo):
        dir = self.obterParametro('global-diretorio_de_saida')
        arquivo = open(dir + "/" + nomeArquivo, 'w')

        for i in range(0, len(lista)):
            elemento = lista[i]
            if type(elemento) == type(unicode()):
                elemento = elemento.encode("utf8")
            else:
                elemento = str(elemento)
            arquivo.write(elemento + '\n')
        arquivo.close()

    def salvarMatrizTXT(self, matriz, nomeArquivo):
        dir = self.obterParametro('global-diretorio_de_saida')
        arquivo = open(dir + "/" + nomeArquivo, 'w')
        N = matriz.shape[0]

        for i in range(0, N):
            for j in range(0, N):
                arquivo.write(str(matriz[i, j]) + ' ')
            arquivo.write('\n')
        arquivo.close()

    def salvarMatrizXML(self, matriz, nomeArquivo):
        dir = self.obterParametro('global-diretorio_de_saida')
        arquivo = open(dir + "/" + nomeArquivo, 'w')

        s = '<?xml version="1.0" encoding="UTF-8"?> \
            \n<!--  An excerpt of an egocentric social network  --> \
            \n<graphml xmlns="http://graphml.graphdrawing.org/xmlns"> \
            \n<graph edgedefault="undirected"> \
            \n<!-- data schema --> \
            \n<key id="name" for="node" attr.name="name" attr.type="string"/> \
            \n<key id="nickname" for="node" attr.name="nickname" attr.type="string"/> \
            \n<key id="gender" for="node" attr.name="gender" attr.type="string"/> \
            \n<key id="image" for="node" attr.name="image" attr.type="string"/> \
            \n<key id="link" for="node" attr.name="link" attr.type="string"/> \
            \n<key id="amount" for="edge" attr.name="amount" attr.type="int"/> \
            \n<key id="pubs" for="node" attr.name="pubs" attr.type="int"/>'

        for i in range(0, self.numeroDeMembros()):
            membro = self.listaDeMembros[i]
            s += '\n<!-- nodes --> \
                \n<node id="' + str(membro.idMembro) + '"> \
                \n<data key="name">' + membro.nomeCompleto + '</data> \
                \n<data key="nickname">' + membro.nomeEmCitacoesBibliograficas + '</data> \
                \n<data key="gender">' + membro.sexo[0].upper() + '</data> \
                \n<data key="image">' + membro.foto + '</data> \
                \n<data key="link">' + membro.url + '</data> \
                \n<data key="pubs">' + str(int(self.vetorDeCoAutoria[i])) + '</data> \
                \n</node>'

        N = matriz.shape[0]
        for i in range(0, N):
            for j in range(0, N):
                if matriz[i, j] > 0:
                    s += '\n<!-- edges --> \
                        \n<edge source="' + str(i) + '" target="' + str(j) + '"> \
                        \n<data key="amount">' + str(matriz[i, j]) + '</data> \
                        \n</edge>'

        s += '\n</graph>\
            \n</graphml>'

        arquivo.write(s.encode('utf8'))
        arquivo.close()

    def salvarVetorDeProducoes(self, vetor, nomeArquivo):
        dir = self.obterParametro('global-diretorio_de_saida')
        arquivo = open(dir + "/" + nomeArquivo, 'w')
        string = ''
        for i in range(0, len(vetor)):
            (prefixo, pAnos, pQuantidades) = vetor[i]
            string += "\n" + prefixo + ":"
            for j in range(0, len(pAnos)):
                string += str(pAnos[j]) + ',' + str(pQuantidades[j]) + ';'
        arquivo.write(string)
        arquivo.close()

    def salvarListaInternalizacaoTXT(self, listaDoiValido, nomeArquivo):
        dir = self.obterParametro('global-diretorio_de_saida')
        arquivo = open(dir + "/" + nomeArquivo, 'w')
        for i in range(0, len(listaDoiValido)):
            elemento = listaDoiValido[i]
            if type(elemento) == type(unicode()):
                elemento = elemento.encode("utf8")
            else:
                elemento = str(elemento)
            arquivo.write(elemento + '\n')
        arquivo.close()

    def gerarGraficosDeBarras(self):
        print "\n[CRIANDO GRAFICOS DE BARRAS]"
        gBarra = GraficoDeBarras(self.obterParametro('global-diretorio_de_saida'))

        gBarra.criarGrafico(self.compilador.listaCompletaArtigoEmPeriodico, 'PB0', 'Numero de publicacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaLivroPublicado, 'PB1', 'Numero de publicacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaCapituloDeLivroPublicado, 'PB2', 'Numero de publicacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaTextoEmJornalDeNoticia, 'PB3', 'Numero de publicacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaTrabalhoCompletoEmCongresso, 'PB4', 'Numero de publicacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaResumoExpandidoEmCongresso, 'PB5', 'Numero de publicacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaResumoEmCongresso, 'PB6', 'Numero de publicacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaArtigoAceito, 'PB7', 'Numero de publicacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaApresentacaoDeTrabalho, 'PB8', 'Numero de publicacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOutroTipoDeProducaoBibliografica, 'PB9',
                            'Numero de publicacoes')

        gBarra.criarGrafico(self.compilador.listaCompletaSoftwareComPatente, 'PT0', 'Numero de producoes tecnicas')
        gBarra.criarGrafico(self.compilador.listaCompletaSoftwareSemPatente, 'PT1', 'Numero de producoes tecnicas')
        gBarra.criarGrafico(self.compilador.listaCompletaProdutoTecnologico, 'PT2', u'Numero de producoes tecnicas')
        gBarra.criarGrafico(self.compilador.listaCompletaProcessoOuTecnica, 'PT3', 'Numero de producoes tecnicas')
        gBarra.criarGrafico(self.compilador.listaCompletaTrabalhoTecnico, 'PT4', 'Numero de producoes tecnicas')
        gBarra.criarGrafico(self.compilador.listaCompletaOutroTipoDeProducaoTecnica, 'PT5',
                            'Numero de producoes tecnicas')

        gBarra.criarGrafico(self.compilador.listaCompletaPatente, 'PR0', 'Numero de patentes')
        gBarra.criarGrafico(self.compilador.listaCompletaProgramaComputador, 'PR1', 'Numero de programa de computador')
        gBarra.criarGrafico(self.compilador.listaCompletaDesenhoIndustrial, 'PR2', 'Numero de desenho industrial')

        gBarra.criarGrafico(self.compilador.listaCompletaProducaoArtistica, 'PA0', 'Numero de producoes artisticas')

        gBarra.criarGrafico(self.compilador.listaCompletaOASupervisaoDePosDoutorado, 'OA0', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOATeseDeDoutorado, 'OA1', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOADissertacaoDeMestrado, 'OA2', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOAMonografiaDeEspecializacao, 'OA3', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOATCC, 'OA4', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOAIniciacaoCientifica, 'OA5', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOAOutroTipoDeOrientacao, 'OA6', 'Numero de orientacoes')

        gBarra.criarGrafico(self.compilador.listaCompletaOCSupervisaoDePosDoutorado, 'OC0', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOCTeseDeDoutorado, 'OC1', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOCDissertacaoDeMestrado, 'OC2', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOCMonografiaDeEspecializacao, 'OC3', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOCTCC, 'OC4', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOCIniciacaoCientifica, 'OC5', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOCOutroTipoDeOrientacao, 'OC6', 'Numero de orientacoes')

        gBarra.criarGrafico(self.compilador.listaCompletaPremioOuTitulo, 'Pm', 'Numero de premios')
        gBarra.criarGrafico(self.compilador.listaCompletaProjetoDePesquisa, 'Pj', 'Numero de projetos')

        gBarra.criarGrafico(self.compilador.listaCompletaPB, 'PB', 'Numero de producoes bibliograficas')
        gBarra.criarGrafico(self.compilador.listaCompletaPT, 'PT', 'Numero de producoes tecnicas')
        gBarra.criarGrafico(self.compilador.listaCompletaPA, 'PA', 'Numero de producoes artisticas')
        gBarra.criarGrafico(self.compilador.listaCompletaOA, 'OA', 'Numero de orientacoes em andamento')
        gBarra.criarGrafico(self.compilador.listaCompletaOC, 'OC', 'Numero de orientacoes concluidas')

        gBarra.criarGrafico(self.compilador.listaCompletaParticipacaoEmEvento, 'Ep', 'Numero de Eventos')
        gBarra.criarGrafico(self.compilador.listaCompletaOrganizacaoDeEvento, 'Eo', 'Numero de Eventos')

        prefix = self.obterParametro('global-prefixo') + '-' if not self.obterParametro('global-prefixo') == '' else ''
        self.salvarVetorDeProducoes(gBarra.obterVetorDeProducoes(), prefix + 'vetorDeProducoes.txt')

    def gerarGrafosDeColaboracoes(self):
        if self.obterParametro('grafo-mostrar_grafo_de_colaboracoes'):
            self.grafosDeColaboracoes = GrafoDeColaboracoes(self, self.obterParametro('global-diretorio_de_saida'))
        print "\n[ROTULOS]"
        print "- " + str(self.listaDeRotulos)
        print "- " + str(self.listaDeRotulosCores)

    def gerarGraficoDeProporcoes(self):
        if self.obterParametro('relatorio-incluir_grafico_de_proporcoes_bibliograficas'):
            gProporcoes = GraficoDeProporcoes(self, self.obterParametro('global-diretorio_de_saida'))

    def calcularInternacionalizacao(self):
        if self.obterParametro('relatorio-incluir_internacionalizacao'):
            print "\n[ANALISANDO INTERNACIONALIZACAO]"
            self.analisadorDePublicacoes = AnalisadorDePublicacoes(self)
            self.listaDePublicacoesEinternacionalizacao = self.analisadorDePublicacoes.analisarInternacionalizacaoNaCoautoria()
            if self.analisadorDePublicacoes.listaDoiValido is not None:
                prefix = self.obterParametro('global-prefixo') + '-' if not self.obterParametro(
                    'global-prefixo') == '' else ''
                self.salvarListaInternalizacaoTXT(self.analisadorDePublicacoes.listaDoiValido,
                                                  prefix + 'internacionalizacao.txt')

    def imprimirListasCompletas(self):
        self.compilador.imprimirListasCompletas()

    def imprimirMatrizesDeFrequencia(self):
        self.compilador.imprimirMatrizesDeFrequencia()
        print "\n[VETOR DE CO-AUTORIA]"
        print self.vetorDeCoAutoria
        print "\n[MATRIZ DE FREQUENCIA NORMALIZADA]"
        print self.matrizDeFrequenciaNormalizada

    def numeroDeMembros(self):
        return len(self.listaDeMembros)

    def ordenarListaDeMembros(self, chave):
        self.listaDeMembros.sort(key=operator.attrgetter(chave))  # ordenamos por nome

    def imprimirListaDeParametros(self):
        for par in self.listaDeParametros:  # .keys():
            print "[PARAMETRO] ", par[0], " = ", par[1]
        print

    def imprimirListaDeMembros(self):
        for membro in self.listaDeMembros:
            print membro
        print

    def imprimirListaDeRotulos(self):
        for rotulo in self.listaDeRotulos:
            print "[ROTULO] ", rotulo

    def obterParametro(self, parametro):
        for i in range(0, len(self.listaDeParametros)):
            if parametro == self.listaDeParametros[i][0]:
                if self.listaDeParametros[i][1].lower() == 'sim':
                    return 1
                if self.listaDeParametros[i][1].lower() == 'nao' or self.listaDeParametros[i][1].lower() == 'não':
                    return 0

                return self.listaDeParametros[i][1]

    def atribuirCoNoRotulo(self, indice, cor):
        self.listaDeRotulosCores[indice] = cor

