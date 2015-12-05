#!/usr/bin/python
# encoding: utf-8
# filename: membro.py
#
# scriptLattes V8
#  Copyright 2005-2013: Jesús P. Mena-Chalco e Roberto M. Cesar-Jr.
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
from data_tables.bibliographical_production.books import Books
from data_tables.bibliographical_production.event_papers import EventPapers
from data_tables.bibliographical_production.journal_papers import JournalPapers
from data_tables.bibliographical_production.newspaper_texts import NewspaperTexts
from data_tables.bibliographical_production.others import Others
from data_tables.bibliographical_production.presentations import Presentations
from extract.parserLattesXML import *
from report.charts.geolocalizador import *
from util.util import get_lattes_url


class Membro:
    sexo = ''
    nomeEmCitacoesBibliograficas = ''
    bolsaProdutividade = ''
    enderecoProfissional = ''
    enderecoProfissionalLat = ''
    enderecoProfissionalLon = ''

    identificador10 = ''

    atualizacaoCV = ''
    foto = ''
    textoResumo = ''
    # xml = None

    listaFormacaoAcademica = []
    listaProjetoDePesquisa = []
    listaAreaDeAtuacao = []
    listaIdioma = []
    listaPremioOuTitulo = []

    listaIDLattesColaboradores = []
    listaIDLattesColaboradoresUnica = []

    # Produção bibliográfica
    listaArtigoEmPeriodico = []
    listaLivroPublicado = []
    listaCapituloDeLivroPublicado = []
    listaTextoEmJornalDeNoticia = []
    listaTrabalhoCompletoEmCongresso = []
    listaResumoExpandidoEmCongresso = []
    listaResumoEmCongresso = []
    listaArtigoAceito = []
    listaApresentacaoDeTrabalho = []
    listaOutroTipoDeProducaoBibliografica = []

    # Produção técnica
    listaSoftwareComPatente = []
    listaSoftwareSemPatente = []
    listaProdutoTecnologico = []
    listaProcessoOuTecnica = []
    listaTrabalhoTecnico = []
    listaOutroTipoDeProducaoTecnica = []

    # Patentes e registros
    listaPatente = []
    listaProgramaComputador = []
    listaDesenhoIndustrial = []

    # Produção artística/cultural
    listaProducaoArtistica = []

    # Orientações em andamento
    listaOASupervisaoDePosDoutorado = []
    listaOATeseDeDoutorado = []
    listaOADissertacaoDeMestrado = []
    listaOAMonografiaDeEspecializacao = []
    listaOATCC = []
    listaOAIniciacaoCientifica = []
    listaOAOutroTipoDeOrientacao = []

    # Orientações concluídas
    listaOCSupervisaoDePosDoutorado = []
    listaOCTeseDeDoutorado = []
    listaOCDissertacaoDeMestrado = []
    listaOCMonografiaDeEspecializacao = []
    listaOCTCC = []
    listaOCIniciacaoCientifica = []
    listaOCOutroTipoDeOrientacao = []

    # Qualis
    # tabelaQualisDosAnos = [{}]
    # tabelaQualisDosTipos = {}
    # tabelaQualisDasCategorias = [{}]

    # Eventos
    listaParticipacaoEmEvento = []
    listaOrganizacaoDeEvento = []

    tabela_qualis = pandas.DataFrame(columns=['ano', 'area', 'estrato', 'freq'])

    # def __init__(self, idMembro, identificador, nome, periodo, rotulo, items_desde_ano, items_ate_ano, xml=''):

    def __init__(self, identificador, nome, periodo, rotulo, items_desde_ano, items_ate_ano):
        self.id_lattes = str(identificador)
        self.nome_completo = nome  # nome.split(";")[0].strip().decode('utf8', 'replace')
        self.periodo = periodo
        self.rotulo = rotulo

        self.items_desde_ano = items_desde_ano
        self.items_ate_ano = items_ate_ano
        self.member_timespans = self.parse_timespans_list(self.periodo)

        self.journal_papers = JournalPapers(self.id_lattes, timespan=self.member_timespans)
        self.event_papers = EventPapers(self.id_lattes, timespan=self.member_timespans)
        self.books = Books(self.id_lattes, timespan=self.member_timespans)
        self.newspaper_texts = NewspaperTexts(self.id_lattes, timespan=self.member_timespans)
        self.presentations = Presentations(self.id_lattes, timespan=self.member_timespans)
        self.others = Others(self.id_lattes, timespan=self.member_timespans)

        # replaced by util.get_lattes_url
        # p = re.compile('[a-zA-Z]+')
        # if p.match(str(identificador)):
        #     self.url = 'http://buscatextual.cnpq.br/buscatextual/visualizacv.do?id={}'.format(identificador)
        # else:
        #     self.url = 'http://lattes.cnpq.br/{}'.format(identificador)
        self.url = get_lattes_url(self.id_lattes)


    def __lt__(self, other):
        return self.nome_completo < other.nome_completo

    def parse_timespans_list(self, timespans_string):
        timespans = []
        timespans_string = re.sub('\s+', '', timespans_string)

        # TODO: ver se não é possível reajustar isso
        if timespans_string:  # se nao especificado o periodo, entao aceitamos todos os items do CV Lattes
            lista = timespans_string.split("&")
            for periodo in lista:
                ano1, _, ano2 = periodo.partition("-")

                if ano1.lower() == 'hoje':
                    ano1 = str(datetime.datetime.now().year)
                if ano2.lower() == 'hoje' or ano2 == '':
                    ano2 = str(datetime.datetime.now().year)

                if ano1.isdigit() and ano2.isdigit():
                    timespans.append([int(ano1), int(ano2)])
                else:
                    logger.warning("[AVISO IMPORTANTE] Período não válido: {}. (período desconsiderado na lista)".format(periodo))
                    logger.warning("[AVISO IMPORTANTE] CV Lattes: {}. Membro: {}".format(self.id_lattes, self.nome_completo.encode('utf8')))
        return timespans

    def carregar_dados_cv_lattes(self, parser):
        # Obtemos todos os dados do CV Lattes
        self.nome_completo = parser.nomeCompleto
        self.bolsaProdutividade = parser.bolsaProdutividade
        self.enderecoProfissional = parser.enderecoProfissional
        self.sexo = parser.sexo
        self.nomeEmCitacoesBibliograficas = parser.nomeEmCitacoesBibliograficas
        self.atualizacaoCV = parser.atualizacaoCV
        self.textoResumo = parser.textoResumo
        self.foto = parser.foto

        self.listaIDLattesColaboradores = parser.listaIDLattesColaboradores
        self.listaFormacaoAcademica = parser.listaFormacaoAcademica
        self.listaProjetoDePesquisa = parser.listaProjetoDePesquisa
        self.listaAreaDeAtuacao = parser.listaAreaDeAtuacao
        self.listaIdioma = parser.listaIdioma
        self.listaPremioOuTitulo = parser.listaPremioOuTitulo
        self.listaIDLattesColaboradoresUnica = set(self.listaIDLattesColaboradores)

        # Produção bibliográfica
        self.journal_papers.add_from_parser(parser.listaArtigoEmPeriodico)
        self.journal_papers.add_from_parser(parser.listaArtigoAceito, only_accepted=True)

        self.event_papers.add_from_parser(parser.listaTrabalhoCompletoEmCongresso, type=EventPapers.Types.complete)
        self.event_papers.add_from_parser(parser.listaResumoExpandidoEmCongresso, type=EventPapers.Types.expanded_abstract)
        self.event_papers.add_from_parser(parser.listaResumoEmCongresso, type=EventPapers.Types.abstract)

        self.books.add_from_parser(parser.listaLivroPublicado)
        self.books.add_from_parser(parser.listaCapituloDeLivroPublicado, only_chapter=True)

        self.newspaper_texts.add_from_parser(parser.listaTextoEmJornalDeNoticia)
        self.presentations.add_from_parser(parser.listaApresentacaoDeTrabalho)
        self.others.add_from_parser(parser.listaOutroTipoDeProducaoBibliografica)

        # TODO: testando refatoracao até acima
        # Produção técnica
        self.listaSoftwareComPatente = parser.listaSoftwareComPatente
        self.listaSoftwareSemPatente = parser.listaSoftwareSemPatente
        self.listaProdutoTecnologico = parser.listaProdutoTecnologico
        self.listaProcessoOuTecnica = parser.listaProcessoOuTecnica
        self.listaTrabalhoTecnico = parser.listaTrabalhoTecnico
        self.listaOutroTipoDeProducaoTecnica = parser.listaOutroTipoDeProducaoTecnica

        # Patentes e registros
        self.listaPatente = parser.listaPatente
        self.listaProgramaComputador = parser.listaProgramaComputador
        self.listaDesenhoIndustrial = parser.listaDesenhoIndustrial

        # Produção artística
        self.listaProducaoArtistica = parser.listaProducaoArtistica

        # Orientações em andamento
        self.listaOASupervisaoDePosDoutorado = parser.listaOASupervisaoDePosDoutorado
        self.listaOATeseDeDoutorado = parser.listaOATeseDeDoutorado
        self.listaOADissertacaoDeMestrado = parser.listaOADissertacaoDeMestrado
        self.listaOAMonografiaDeEspecializacao = parser.listaOAMonografiaDeEspecializacao
        self.listaOATCC = parser.listaOATCC
        self.listaOAIniciacaoCientifica = parser.listaOAIniciacaoCientifica
        self.listaOAOutroTipoDeOrientacao = parser.listaOAOutroTipoDeOrientacao

        # Orientações concluídas
        self.listaOCSupervisaoDePosDoutorado = parser.listaOCSupervisaoDePosDoutorado
        self.listaOCTeseDeDoutorado = parser.listaOCTeseDeDoutorado
        self.listaOCDissertacaoDeMestrado = parser.listaOCDissertacaoDeMestrado
        self.listaOCMonografiaDeEspecializacao = parser.listaOCMonografiaDeEspecializacao
        self.listaOCTCC = parser.listaOCTCC
        self.listaOCIniciacaoCientifica = parser.listaOCIniciacaoCientifica
        self.listaOCOutroTipoDeOrientacao = parser.listaOCOutroTipoDeOrientacao

        # Eventos
        self.listaParticipacaoEmEvento = parser.listaParticipacaoEmEvento
        self.listaOrganizacaoDeEvento = parser.listaOrganizacaoDeEvento

        # -----------------------------------------------------------------------------------------

    def filtrarItemsPorPeriodo(self):
        self.listaArtigoEmPeriodico = self.filtrarItems(self.listaArtigoEmPeriodico)
        self.listaLivroPublicado = self.filtrarItems(self.listaLivroPublicado)
        self.listaCapituloDeLivroPublicado = self.filtrarItems(self.listaCapituloDeLivroPublicado)
        self.listaTextoEmJornalDeNoticia = self.filtrarItems(self.listaTextoEmJornalDeNoticia)
        self.listaTrabalhoCompletoEmCongresso = self.filtrarItems(self.listaTrabalhoCompletoEmCongresso)
        self.listaResumoExpandidoEmCongresso = self.filtrarItems(self.listaResumoExpandidoEmCongresso)
        self.listaResumoEmCongresso = self.filtrarItems(self.listaResumoEmCongresso)
        self.listaArtigoAceito = self.filtrarItems(self.listaArtigoAceito)
        self.listaApresentacaoDeTrabalho = self.filtrarItems(self.listaApresentacaoDeTrabalho)
        self.listaOutroTipoDeProducaoBibliografica = self.filtrarItems(self.listaOutroTipoDeProducaoBibliografica)

        self.listaSoftwareComPatente = self.filtrarItems(self.listaSoftwareComPatente)
        self.listaSoftwareSemPatente = self.filtrarItems(self.listaSoftwareSemPatente)
        self.listaProdutoTecnologico = self.filtrarItems(self.listaProdutoTecnologico)
        self.listaProcessoOuTecnica = self.filtrarItems(self.listaProcessoOuTecnica)
        self.listaTrabalhoTecnico = self.filtrarItems(self.listaTrabalhoTecnico)
        self.listaOutroTipoDeProducaoTecnica = self.filtrarItems(self.listaOutroTipoDeProducaoTecnica)

        self.listaPatente = self.filtrarItems(self.listaPatente)
        self.listaProgramaComputador = self.filtrarItems(self.listaProgramaComputador)
        self.listaDesenhoIndustrial = self.filtrarItems(self.listaDesenhoIndustrial)

        self.listaProducaoArtistica = self.filtrarItems(self.listaProducaoArtistica)

        self.listaOASupervisaoDePosDoutorado = self.filtrarItems(self.listaOASupervisaoDePosDoutorado)
        self.listaOATeseDeDoutorado = self.filtrarItems(self.listaOATeseDeDoutorado)
        self.listaOADissertacaoDeMestrado = self.filtrarItems(self.listaOADissertacaoDeMestrado)
        self.listaOAMonografiaDeEspecializacao = self.filtrarItems(self.listaOAMonografiaDeEspecializacao)
        self.listaOATCC = self.filtrarItems(self.listaOATCC)
        self.listaOAIniciacaoCientifica = self.filtrarItems(self.listaOAIniciacaoCientifica)
        self.listaOAOutroTipoDeOrientacao = self.filtrarItems(self.listaOAOutroTipoDeOrientacao)

        self.listaOCSupervisaoDePosDoutorado = self.filtrarItems(self.listaOCSupervisaoDePosDoutorado)
        self.listaOCTeseDeDoutorado = self.filtrarItems(self.listaOCTeseDeDoutorado)
        self.listaOCDissertacaoDeMestrado = self.filtrarItems(self.listaOCDissertacaoDeMestrado)
        self.listaOCMonografiaDeEspecializacao = self.filtrarItems(self.listaOCMonografiaDeEspecializacao)
        self.listaOCTCC = self.filtrarItems(self.listaOCTCC)
        self.listaOCIniciacaoCientifica = self.filtrarItems(self.listaOCIniciacaoCientifica)
        self.listaOCOutroTipoDeOrientacao = self.filtrarItems(self.listaOCOutroTipoDeOrientacao)

        self.listaPremioOuTitulo = self.filtrarItems(self.listaPremioOuTitulo)
        self.listaProjetoDePesquisa = self.filtrarItems(self.listaProjetoDePesquisa)

        self.listaParticipacaoEmEvento = self.filtrarItems(self.listaParticipacaoEmEvento)
        self.listaOrganizacaoDeEvento = self.filtrarItems(self.listaOrganizacaoDeEvento)

    def filtrarItems(self, lista):
        # FIXME: refactor
        return list(filter(self.estaDentroDoPeriodo, lista))

        # Not pythonic
        # for i in range(0, len(lista)):
        #     if not self.estaDentroDoPeriodo(lista[i]):
        #         lista[i] = None
        # lista = [l for l in lista if l is not None] # Eliminamos os elementos' None'
        #
        # # ORDENAR A LISTA POR ANO? QUE TAL? rpta. Nao necessário!
        # return lista

    def estaDentroDoPeriodo(self, objeto):
        # FIXME: refactor
        if objeto.__module__ == 'orientacaoEmAndamento':
            objeto.ano = int(objeto.ano) if objeto.ano else 0  # Caso
            if objeto.ano > self.items_ate_ano:
                return 0
            else:
                return 1

        elif objeto.__module__ == 'projetoDePesquisa':
            if objeto.anoConclusao.lower() == 'atual':
                objeto.anoConclusao = str(datetime.datetime.now().year)

            if objeto.anoInicio == '':  # Para projetos de pesquisa sem anos! (sim... tem gente que não coloca os anos!)
                objeto.anoInicio = '0'
            if objeto.anoConclusao == '':
                objeto.anoConclusao = '0'

            objeto.anoInicio = int(objeto.anoInicio)
            objeto.anoConclusao = int(objeto.anoConclusao)
            objeto.ano = objeto.anoInicio  # Para comparação entre projetos

            if objeto.anoInicio > self.items_ate_ano and objeto.anoConclusao > self.items_ate_ano \
                or objeto.anoInicio < self.items_desde_ano and objeto.anoConclusao < self.items_desde_ano:
                return 0
            else:
                fora = 0
                for per in self.member_timespans:
                    if objeto.anoInicio > per[1] and objeto.anoConclusao > per[1] or objeto.anoInicio < per[0] and objeto.anoConclusao < per[0]:
                        fora += 1
                if fora == len(self.member_timespans):
                    return 0
                else:
                    return 1

        else:
            if not objeto.ano:  # se nao for identificado o ano sempre o mostramos na lista
                objeto.ano = 0
                return 1
            else:
                objeto.ano = int(objeto.ano)
                if objeto.ano < self.items_desde_ano or objeto.ano > self.items_ate_ano:
                    return 0
                else:
                    retorno = 0
                    for per in self.member_timespans:
                        if per[0] <= objeto.ano <= per[1]:
                            retorno = 1
                            break
                    return retorno

    def obterCoordenadasDeGeolocalizacao(self):
        geo = Geolocalizador(self.enderecoProfissional)
        self.enderecoProfissionalLat = geo.lat
        self.enderecoProfissionalLon = geo.lon

    def ris(self):
        s = ''
        s += '\nTY  - MEMBRO'
        s += '\nNOME  - ' + self.nome_completo
        # s+= '\nSEXO  - '+self.sexo
        s += '\nCITA  - ' + self.nomeEmCitacoesBibliograficas
        s += '\nBOLS  - ' + self.bolsaProdutividade
        s += '\nENDE  - ' + self.enderecoProfissional
        s += '\nURLC  - ' + self.url
        s += '\nDATA  - ' + self.atualizacaoCV
        s += '\nRESU  - ' + self.textoResumo

        for i in range(0, len(self.listaFormacaoAcademica)):
            formacao = self.listaFormacaoAcademica[i]
            s += '\nFO' + str(i + 1) + 'a  - ' + formacao.anoInicio
            s += '\nFO' + str(i + 1) + 'b  - ' + formacao.anoConclusao
            s += '\nFO' + str(i + 1) + 'c  - ' + formacao.tipo
            s += '\nFO' + str(i + 1) + 'd  - ' + formacao.nomeInstituicao
            s += '\nFO' + str(i + 1) + 'e  - ' + formacao.descricao

        for i in range(0, len(self.listaAreaDeAtuacao)):
            area = self.listaAreaDeAtuacao[i]
            s += '\nARE' + str(i + 1) + '  - ' + area.descricao

        for i in range(0, len(self.listaIdioma)):
            idioma = self.listaIdioma[i]
            s += '\nID' + str(i + 1) + 'a  - ' + idioma.nome
            s += '\nID' + str(i + 1) + 'b  - ' + idioma.proficiencia

        return s

    def __str__(self):
        verbose = 0

        s = "+ ID-MEMBRO   : " + str(self.id_lattes) + "\n"
        s += "+ ROTULO      : " + self.rotulo + "\n"
        # s += "+ ALIAS       : " + self.nome.encode('utf8','replace') + "\n"
        s += "+ NOME REAL   : " + self.nome_completo + "\n"
        # s += "+ SEXO        : " + self.sexo.encode('utf8','replace') + "\n"
        # s += "+ NOME Cits.  : " + self.nomeEmCitacoesBibliograficas.encode('utf8','replace') + "\n"
        # s += "+ PERIODO     : " + self.periodo.encode('utf8','replace') + "\n"
        # s += "+ BOLSA Prod. : " + self.bolsaProdutividade.encode('utf8','replace') + "\n"
        # s += "+ ENDERECO    : " + self.enderecoProfissional.encode('utf8','replace') +"\n"
        # s += "+ URL         : " + self.url.encode('utf8','replace') +"\n"
        # s += "+ ATUALIZACAO : " + self.atualizacaoCV.encode('utf8','replace') +"\n"
        # s += "+ FOTO        : " + self.foto.encode('utf8','replace') +"\n"
        # s += "+ RESUMO      : " + self.textoResumo.encode('utf8','replace') + "\n"
        # s += "+ COLABORADs. : " + str(len(self.listaIDLattesColaboradoresUnica))

        if verbose:
            s += "\n[COLABORADORES]"
            for idColaborador in self.listaIDLattesColaboradoresUnica:
                s += "\n+ " + idColaborador.encode('utf8', 'replace')

            s += "\n"
            for formacao in self.listaFormacaoAcademica:
                s += formacao.__str__()

            s += "\n"
            for projeto in self.listaProjetoDePesquisa:
                s += projeto.__str__()

            s += "\n"
            for area in self.listaAreaDeAtuacao:
                s += area.__str__()

            s += "\n"
            for idioma in self.listaIdioma:
                s += idioma.__str__()

            s += "\n"
            for premio in self.listaPremioOuTitulo:
                s += premio.__str__()

            s += "\n"
            for pub in self.listaArtigoEmPeriodico:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaLivroPublicado:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaCapituloDeLivroPublicado:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaTextoEmJornalDeNoticia:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaTrabalhoCompletoEmCongresso:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaResumoExpandidoEmCongresso:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaResumoEmCongresso:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaArtigoAceito:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaApresentacaoDeTrabalho:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaOutroTipoDeProducaoBibliografica:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaSoftwareComPatente:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaSoftwareSemPatente:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaProdutoTecnologico:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaProcessoOuTecnica:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaTrabalhoTecnico:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaOutroTipoDeProducaoTecnica:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaPatente:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaProgramaComputador:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaDesenhoIndustrial:
                s += pub.__str__()

            s += "\n"
            for pub in self.listaProducaoArtistica:
                s += pub.__str__()

        else:
            totals = [
                (u'- Número de colaboradores (identificado)', len(self.listaIDLattesColaboradoresUnica)),
                (u'- Artigos completos publicados em periódicos', len(self.journal_papers)),
                (u'- Livros publicados/organizados ou edições', len(self.listaLivroPublicado)),
                (u'- Capítulos de livros publicados', len(self.listaCapituloDeLivroPublicado)),
                (u'- Textos em jornais de notícias/revistas', len(self.listaTextoEmJornalDeNoticia)),
                (u'- Trabalhos completos publicados em congressos', len(self.listaTrabalhoCompletoEmCongresso)),
                (u'- Resumos expandidos publicados em congressos', len(self.listaResumoExpandidoEmCongresso)),
                (u'- Resumos publicados em anais de congressos', len(self.listaResumoEmCongresso)),
                (u'- Artigos aceitos para publicação', len(self.listaArtigoAceito)),
                (u'- Apresentações de Trabalho', len(self.listaApresentacaoDeTrabalho)),
                (u'- Demais tipos de produção bibliográfica', len(self.listaOutroTipoDeProducaoBibliografica)),
                (u'- Softwares com registro de patente', len(self.listaSoftwareComPatente)),
                (u'- Softwares sem registro de patente', len(self.listaSoftwareSemPatente)),
                (u'- Produtos tecnológicos', len(self.listaProdutoTecnologico)),
                (u'- Processos ou técnicas', len(self.listaProcessoOuTecnica)),
                (u'- Trabalhos técnicos', len(self.listaTrabalhoTecnico)),
                (u'- Demais tipos de produção técnica', len(self.listaOutroTipoDeProducaoTecnica)),
                (u'- Patente', len(self.listaPatente)),
                (u'- Programa de computador', len(self.listaProgramaComputador)),
                (u'- Desenho industrial', len(self.listaDesenhoIndustrial)),
                (u'- Produção artística/cultural', len(self.listaProducaoArtistica)),
                (u'- Orientações em andamento', ''),
                (u'  . Supervições de pos doutorado', len(self.listaOASupervisaoDePosDoutorado)),
                (u'  . Tese de doutorado', len(self.listaOATeseDeDoutorado)),
                (u'  . Dissertações de mestrado', len(self.listaOADissertacaoDeMestrado)),
                (u'  . Monografías de especialização', len(self.listaOAMonografiaDeEspecializacao)),
                (u'  . TCC', len(self.listaOATCC)),
                (u'  . Iniciação científica', len(self.listaOAIniciacaoCientifica)),
                (u'  . Orientações de outra natureza', len(self.listaOAOutroTipoDeOrientacao)),
                (u'- Orientações concluídas', ''),
                (u'  . Supervições de pos doutorado', len(self.listaOCSupervisaoDePosDoutorado)),
                (u'  . Tese de doutorado', len(self.listaOCTeseDeDoutorado)),
                (u'  . Dissertações de mestrado', len(self.listaOCDissertacaoDeMestrado)),
                (u'  . Monografías de especialização', len(self.listaOCMonografiaDeEspecializacao)),
                (u'  . TCC', len(self.listaOCTCC)),
                (u'  . Iniciação científica', len(self.listaOCIniciacaoCientifica)),
                (u'  . Orientações de outra natureza', len(self.listaOCOutroTipoDeOrientacao)),
                (u'- Projetos de pesquisa', len(self.listaProjetoDePesquisa)),
                (u'- Prêmios e títulos', len(self.listaPremioOuTitulo)),
                (u'- Participação em eventos', len(self.listaParticipacaoEmEvento)),
                (u'- Organização de eventos', len(self.listaOrganizacaoDeEvento)),
            ]
            width = max(len(item[0]) for item in totals)
            s += '\n'.join([u'{} {}'.format(label.ljust(width), value) for label, value in totals])
            # s += tabulate(totals)
            s += "\n\n"

        return s


# ---------------------------------------------------------------------------- #
# http://wiki.python.org/moin/EscapingHtml
def htmlentitydecode(s):
    return re.sub('&(%s);' % '|'.join(name2codepoint),
                  lambda m: unichr(name2codepoint[m.group(1)]), s)
