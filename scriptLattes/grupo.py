#!/usr/bin/python
# -*- coding: utf-8 -*-
# filename: grupo.py
import datetime
import logging

from scipy import sparse

from data.internacionalizacao.analisadorDePublicacoes import AnalisadorDePublicacoes
from data_tables.bibliographical_production.event_papers import EventPapers
from data_tables.bibliographical_production.journal_papers import JournalPapers
from membro import Membro
from persist.cache import cache
from process.authorRank import AuthorRank
from process.compiladorDeListas import CompiladorDeListas
from qualis import qualis
from report.charts.graficoDeBarras import GraficoDeBarras
from report.charts.mapaDeGeolocalizacao import MapaDeGeolocalizacao
from report.geradorDeXML import GeradorDeXML

logger = logging.getLogger(__name__)


class Grupo:
    compilador = None
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

    _co_authorship_adjacency_matrix = None
    co_authorship_normalized_weighted_matrix = None
    co_authorship_vector = None
    author_rank_vector = None

    mapaDeGeolocalizacao = None

    nomes = None
    rotulos = None
    geolocalizacoes = None

    qualis = None

    def __init__(self, name, ids_df, group_id=1, desde_ano=0, ate_ano=None, qualis_de_congressos=None, areas_qualis=None):
        self.name = name
        self.group_id = group_id

        if desde_ano is None or type(desde_ano) is str and desde_ano.lower() == 'hoje':
            desde_ano = str(datetime.datetime.now().year)
        if ate_ano is None or type(ate_ano) is str and ate_ano.lower() == 'hoje':
            ate_ano = str(datetime.datetime.now().year)

        self.items_desde_ano = desde_ano
        self.items_ate_ano = ate_ano

        # FIXME: onde que isto é usado?
        # self.diretorioDoi = self.obterParametro('global-diretorio_de_armazenamento_de_doi')
        # if not self.diretorioDoi == '':
        # util.criarDiretorio(self.diretorioDoi)

        # carregamos a lista de membros

        self.members_list = {}
        for index, row in ids_df.iterrows():
            self.members_list[row.identificador] = Membro(row['identificador'], row['nome'], row['periodo'],
                                                          row['rotulo'], self.items_desde_ano, self.items_ate_ano)
        self.members_indices = {lattes_id: index for index, lattes_id in enumerate(self.members_list.keys())}

        self.ids_df = ids_df
        # XXX: following lines replaced by property method below
        # self.labels_set = ids_df['rotulo'].unique()
        # self.labels_set.sort()
        # self.listaDeRotulosCores = [''] * len(self.labels_set)

        self.journal_papers = JournalPapers(id=self.group_id)  # TODO: define a group id
        self.event_papers = EventPapers(id=self.group_id)  # TODO: define a group id
        self.productions_list = [self.journal_papers, self.event_papers]

        # FIXME: atualizar extração do qualis (decidir se é melhor um pacote separado); de qualquer forma, é necessário agora extrair da plataforma sucupira
        read_from_cache = True if cache.file('qualis.data') else False
        self.qualis = qualis.Qualis(read_from_cache=read_from_cache,
                                    data_file_path=cache.file('qualis.data'),
                                    arquivo_qualis_de_congressos=qualis_de_congressos,
                                    arquivo_areas_qualis=areas_qualis)

    @property
    def labels_set(self):
        return sorted(self.ids_df.rotulo.unique())

    def extract_cvs_data(self, parser, cvs_raw_data):
        for index, (id_lattes, cv_content) in enumerate(cvs_raw_data.items()):
            logger.info('[LENDO REGISTRO LATTES: {0}o. DA LISTA]'.format(index + 1))
            if id_lattes in self.members_list.keys():
                parsed_content = parser(id_lattes, cv_content)
                # TODO: FIXME: refatorar usando pandas para filtrar
                self.members_list[id_lattes].carregar_dados_cv_lattes(parsed_content)
                self.members_list[id_lattes].filtrarItemsPorPeriodo()
                logger.debug(u"{}".format(self.members_list[id_lattes]))

    def aggregate_data(self):
        for _, member in self.members_list.items():
            self.journal_papers.append(member.journal_papers)
            self.event_papers.append(member.event_papers)
            # self.journal_papers.group_similar()
            # self.event_papers.group_similar()

    # REFATORADO ATE AQUI *********************************************************************************************

    # FIXME: não usar config aqui; elas são no fundo filtros para os relatórios
    def compilarListasDeItems(self, config):
        raise "método inutilizado"
        self.compilador = CompiladorDeListas(self)  # compilamos todo e criamos 'listasCompletas'
        self.aggregate_data()

        self.create_colaboration_matrices()

        # XXX: não sei para que serve o trecho abaixo
        # listas de nomes, rotulos e IDs
        # self.nomes = list([])
        # self.rotulos = list([])
        # self.ids = list([])
        # for membro in self.members_list.values():
        #     self.nomes.append(membro.nomeCompleto)
        #     self.rotulos.append(membro.rotulo)
        #     self.ids.append(membro.idLattes)

    @property
    def co_authorship_adjacency_matrix(self):
        if self._co_authorship_adjacency_matrix is None:
            self._co_authorship_adjacency_matrix = sparse.lil_matrix((len(self.members_indices), len(self.members_indices)))
            for production in self.productions_list:
                self._co_authorship_adjacency_matrix += production.co_authorship_adjacency_matrix(self.members_indices)
        return self._co_authorship_adjacency_matrix

    def create_colaboration_matrices(self):
        # FIXME: depende do compilador ter sido instanciado no método compilarListasDeItems
        # Grafos de coautoria
        # self.compilador.criarMatrizesDeColaboracao()
        # self.matrizesArtigoEmPeriodico = self.journal_papers.co_authorship_adjacency_matrix(self.members_indices)
        # self.matrizesTrabalhoCompletoEmCongresso = self.event_papers.co_authorship_adjacency_matrix(self.members_indices)
        # [self.matrizDeAdjacencia, self.matrizDeFrequencia] = self.compilador.uniaoDeMatrizesDeColaboracao()

        weighted_matrix = sparse.lil_matrix((len(self.members_indices), len(self.members_indices)))
        for production in self.productions_list:
            weighted_matrix += production.co_authorship_weighted_matrix(self.members_indices)

        # soma das linhas = num. de items feitos em co-autoria (parceria) com outro membro do grupo
        total = weighted_matrix.sum(axis=1)
        total[total == 0] = 1  # for avoiding NaNs in empty rows
        self.co_authorship_normalized_weighted_matrix = sparse.lil_matrix(weighted_matrix / total)

        self.co_authorship_vector = weighted_matrix.sum(axis=1)
        # self.co_authorship_normalized_weighted_matrix = weighted_matrix.copy()
        # for i in range(len(self.members_list)):
        #     if not self.co_authorship_vector[i] == 0:
        #         self.co_authorship_normalized_weighted_matrix[i, :] /= float(self.co_authorship_vector[i])

        # AuthorRank
        self.author_rank_vector = AuthorRank(self.co_authorship_normalized_weighted_matrix, 100).rank_vector

    # FIXME: finish refactoring
    def gerarXMLdeGrupo(self):
        geradorDeXml = GeradorDeXML(self)
        xml, errors = geradorDeXml.gerarXmlParaGrupo()

        def salvarXML(self, nome, conteudo):
            prefix = self.grupo.obterParametro('global-prefixo') + '-' if not self.grupo.obterParametro('global-prefixo') == '' else ''
            file = open(self.dir + "/" + prefix + nome, 'w')
            file.write(conteudo.encode('utf8'))
            file.close()

        salvarXML("database.xml", xml)

        if errors:
            print "\n\n[AVISO] Erro ao gerar XML para os lattes abaixo:"
            for item in errors:
                print "- [ID Lattes: " + item + "]"

    def HTMLColorToRGB(self, colorstring):
        colorstring = colorstring.strip()
        if colorstring[0] == '#': colorstring = colorstring[1:]
        r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
        r, g, b = [int(n, 16) for n in (r, g, b)]
        # return (r, g, b)
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

    def gerarMapaDeGeolocalizacao(self):
        if self.obterParametro('mapa-mostrar_mapa_de_geolocalizacao'):
            self.mapaDeGeolocalizacao = MapaDeGeolocalizacao(self)

    def identificarQualisEmPublicacoes(self):
        print "\n[IDENTIFICANDO QUALIS EM PUBLICAÇÕES]"
        for membro in self.members_list.values():
            self.qualis.analisar_publicacoes(membro)  # Qualis - Adiciona Qualis as publicacoes dos membros

        # FIXME: save cache
        # if self.diretorioCache:
        # filename = (self.diretorioCache or '/tmp') + '/qualis.data'
        # self.qualis.qextractor.save_data(self.diretorioCache + '/' + filename)
        # self.qualis.qextractor.save_data(filename)

        # FIXME: calcular qualis de eventos (precisa ler do arquivo csv)
        # self.qualis.calcular_totais_dos_qualis(self.compilador.listaCompletaArtigoEmPeriodico,
        #                                        self.compilador.listaCompletaTrabalhoCompletoEmCongresso,
        #                                        self.compilador.listaCompletaResumoExpandidoEmCongresso)

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

    def gerarGraficoDeProporcoes(self):
        if self.obterParametro('relatorio-incluir_grafico_de_proporcoes_bibliograficas'):
            gProporcoes = GraficoDeProporcoes(self, self.obterParametro('global-diretorio_de_saida'))

    def calcularInternacionalizacao(self):
        print "\n[ANALISANDO INTERNACIONALIZACAO]"
        self.analisadorDePublicacoes = AnalisadorDePublicacoes(self)
        self.listaDePublicacoesEinternacionalizacao = self.analisadorDePublicacoes.analisarInternacionalizacaoNaCoautoria()
        return self.analisadorDePublicacoes.listaDoiValido

    def imprimirListasCompletas(self):
        self.compilador.imprimirListasCompletas()

    def imprimirMatrizesDeFrequencia(self):
        self.compilador.imprimirMatrizesDeFrequencia()
        print "\n[VETOR DE CO-AUTORIA]"
        print self.co_authorship_vector
        print "\n[MATRIZ DE FREQUENCIA NORMALIZADA]"
        print self.co_authorship_normalized_weighted_matrix

    # def numeroDeMembros(self):
    #     return len(self.members_list)
    def __len__(self):
        return len(self.members_list)

    def ordenarListaDeMembros(self, chave):
        self.members_list.values().sort(key=operator.attrgetter(chave))  # ordenamos por nome

    def imprimirListaDeParametros(self):
        for par in self.listaDeParametros:  # .keys():
            print "[PARAMETRO] ", par[0], " = ", par[1]
        print

    def imprimirListaDeMembros(self):
        for membro in self.members_list.values():
            print membro
        print

    def imprimirListaDeRotulos(self):
        for rotulo in self.labels_set:
            print "[ROTULO] ", rotulo

            # def obterParametro(self, parametro):
            #     for i in range(0, len(self.listaDeParametros)):
            #         if parametro == self.listaDeParametros[i][0]:
            #             if self.listaDeParametros[i][1].lower() == 'sim':
            #                 return 1
            #             if self.listaDeParametros[i][1].lower() == 'nao' or self.listaDeParametros[i][1].lower() == 'não':
            #                 return 0
            #
            #             return self.listaDeParametros[i][1]

            # def atribuirCoNoRotulo(self, indice, cor):
            #     self.listaDeRotulosCores[indice] = cor
