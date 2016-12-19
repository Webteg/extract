# encoding: utf-8

import logging
import xml.etree.ElementTree as et
from lxml import etree
from scriptLattes.data.producoesBibliograficas.artigoEmPeriodico import ArtigoEmPeriodico
from scriptLattes.data.producoesBibliograficas.capituloDeLivroPublicado import CapituloDeLivroPublicado
from scriptLattes.data.producoesBibliograficas.livroPublicado import LivroPublicado
from scriptLattes.data.producoesBibliograficas.outroTipoDeProducaoBibliografica import OutroTipoDeProducaoBibliografica
from scriptLattes.data.producoesBibliograficas.resumoEmCongresso import ResumoEmCongresso
from scriptLattes.data.producoesBibliograficas.resumoExpandidoEmCongresso import ResumoExpandidoEmCongresso
from scriptLattes.data.producoesBibliograficas.textoEmJornalDeNoticia import TextoEmJornalDeNoticia
from scriptLattes.data.producoesBibliograficas.trabalhoCompletoEmCongresso import TrabalhoCompletoEmCongresso
from scriptLattes.data_tables.technical_production.basic_production import BasicProduction
from scriptLattes.data_tables.technical_production.softwares import Softwares

logger = logging.getLogger(__name__)


class LattesXMLParser:
    def __init__(self, id_lattes, cv_content):
        self.id_lattes = id_lattes

        self.atualizacaoCV = None

        # DADOS-GERAIS
        self.nomeCompleto = None
        self.nomeEmCitacoesBibliograficas = None
        self.sexo = None

        ## RESUMO-CV
        self.textoResumo = None

        ## ENDERECO
        self.enderecoProfissional = None

        ## ?
        self.foto = None
        self.bolsaProdutividade = None
        self.listaIDLattesColaboradores = None

        ## FORMACAO-ACADEMICA-TITULACAO
        self.listaFormacaoAcademica = None
        ## ATUACOES-PROFISSIONAIS
        self.listaProjetoDePesquisa = []
        ## AREAS-DE-ATUACAO
        self.listaAreaDeAtuacao = None
        ## IDIOMAS
        self.listaIdioma = None
        ## PREMIOS-TITULOS
        self.listaPremioOuTitulo = []

        self.listaIDLattesColaboradores = []

        # PRODUCAO-BIBLIOGRAFICA
        ## ARTIGOS-PUBLICADOS
        self.listaArtigoEmPeriodico = []
        self.listaArtigoAceito = []
        ## TRABALHOS-EM-EVENTOS
        self.listaTrabalhoCompletoEmCongresso = []
        self.listaResumoExpandidoEmCongresso = []
        self.listaResumoEmCongresso = []
        ## LIVROS-E-CAPITULOS
        self.listaLivroPublicado = []
        self.listaCapituloDeLivroPublicado = []
        ## FIXME: ver estrutura
        self.listaTextoEmJornalDeNoticia = []
        self.listaApresentacaoDeTrabalho = []
        self.listaOutroTipoDeProducaoBibliografica = []

        # Produção técnica
        self.softwares = []
        self.produtos_tecnologicos = []
        self.processos_ou_tecnicas = []
        self.trabalhos_tecnicos = []
        self.demais_tipos_de_producao_tecnica = []

        # Outras produções
        self.artistic_productions = []

        # Reading and parsing
        root = et.fromstring(cv_content)
        cv = etree.fromstring(cv_content.encode('utf-8'))

        self.atualizacaoCV = root.get('DATA-ATUALIZACAO')

        self.set_general_data(root.find('DADOS-GERAIS'))

        if root.find('PRODUCAO-BIBLIOGRAFICA'):
            self.set_bibliographical_productions(root.find('PRODUCAO-BIBLIOGRAFICA'))

        if cv.xpath('PRODUCAO-TECNICA'):
            self.set_technical_productions(cv.xpath('PRODUCAO-TECNICA')[0])

        if cv.xpath('OUTRA-PRODUCAO/PRODUCAO-ARTISTICA-CULTURAL'):
            self.set_artistic_productions(cv.xpath('OUTRA-PRODUCAO/PRODUCAO-ARTISTICA-CULTURAL')[0])

    def set_general_data(self, general_data_element):
        self.nomeCompleto = general_data_element.get('NOME-COMPLETO')
        self.nomeEmCitacoesBibliograficas = general_data_element.get('NOME-EM-CITACOES-BIBLIOGRAFICAS')
        self.sexo = general_data_element.get('SEXO')
        # FIXME: recuperar foto de alguma forma (aparentemente só é possível acessando o HTML)
        # self.foto = 'usuaria.png' if self.sexo and self.sexo[0] == 'F' else 'usuario.png'

        # RESUMO-CV
        if general_data_element.find('RESUMO-CV'):
            self.textoResumo = general_data_element.find('RESUMO-CV').get('TEXTO-RESUMO-CV-RH')

        # ENDERECO
        address = general_data_element.find('ENDERECO/ENDERECO-PROFISSIONAL[@NOME-INSTITUICAO-EMPRESA]')
        if address:
            self.enderecoProfissional = address.get('NOME-INSTITUICAO-EMPRESA')

        # FORMACAO-ACADEMICA-TITULACAO
        # ATUACOES-PROFISSIONAIS
        # AREAS-DE-ATUACAO
        # IDIOMAS
        # PREMIOS-TITULOS

    def set_bibliographical_productions(self, element):
        """
        :param element: XML element corresponding to ./PRODUCAO-BIBLIOGRAFICA
        :return:
        """
        ## ARTIGOS-PUBLICADOS
        try:
            self.listaArtigoEmPeriodico = self.get_journal_papers_list(element.findall('./ARTIGOS-PUBLICADOS/ARTIGO-PUBLICADO'))
            self.listaArtigoAceito = self.get_journal_papers_list(element.findall('./ARTIGOS-ACEITOS-PARA-PUBLICACAO/ARTIGO-ACEITO-PARA-PUBLICACAO'))
            ## TRABALHOS-EM-EVENTOS
            self.listaTrabalhoCompletoEmCongresso = self.get_event_papers_list(element.find('./TRABALHOS-EM-EVENTOS'), natureza='COMPLETO')
            self.listaResumoExpandidoEmCongresso = self.get_event_papers_list(element.find('./TRABALHOS-EM-EVENTOS'), natureza='RESUMO_EXPANDIDO')
            self.listaResumoEmCongresso = self.get_event_papers_list(element.find('./TRABALHOS-EM-EVENTOS'), natureza='RESUMO')
            ## LIVROS-E-CAPITULOS
            self.listaLivroPublicado = self.get_books_list(element.findall('./LIVROS-E-CAPITULOS/LIVROS-PUBLICADOS-OU-ORGANIZADOS/LIVRO-PUBLICADO-OU-ORGANIZADO'))
            self.listaCapituloDeLivroPublicado = self.get_book_chapters_list(
                element.findall('./LIVROS-E-CAPITULOS/CAPITULOS-DE-LIVROS-PUBLICADOS/CAPITULO-DE-LIVRO-PUBLICADO'))

            self.listaTextoEmJornalDeNoticia = self.get_newspaper_texts_list(element.findall('./TEXTOS-EM-JORNAIS-OU-REVISTAS/TEXTO-EM-JORNAL-OU-REVISTA'))
            self.listaApresentacaoDeTrabalho = []  # FIXME: é produção técnica, não bibliográfica
            self.listaOutroTipoDeProducaoBibliografica = self.get_other_productions_list(
                element.findall('./DEMAIS-TIPOS-DE-PRODUCAO-BIBLIOGRAFICA/OUTRA-PRODUCAO-BIBLIOGRAFICA'))
        except AttributeError as e:
            logger.error("Error processing CV with id '{}'".format(self.id_lattes), exc_info=True)

    def get_journal_papers_list(self, papers):
        productions = []
        for paper in papers:
            production = ArtigoEmPeriodico(self.id_lattes)
            production.autores = '; '.join(author.get('NOME-PARA-CITACAO') for author in paper.findall('./AUTORES'))  # FIXME: perdendo informação ao concatenar

            basic_data = paper.find('./DADOS-BASICOS-DO-ARTIGO')
            production.titulo = basic_data.get('TITULO-DO-ARTIGO')
            production.ano = basic_data.get('ANO-DO-ARTIGO')
            doi = basic_data.get('DOI')
            production.doi = 'http://dx.doi.org/' + doi if doi else ''
            relevante = basic_data.get('FLAG-RELEVANCIA')
            production.relevante = True if relevante == 'SIM' else False

            detailed_data = paper.find('./DETALHAMENTO-DO-ARTIGO')
            production.revista = detailed_data.get('TITULO-DO-PERIODICO-OU-REVISTA')
            production.issn = detailed_data.get('ISSN')
            production.volume = detailed_data.get('VOLUME')
            production.numero = detailed_data.get('FASCICULO')
            production.paginas = "{}-{}".format(detailed_data.get('PAGINA-INICIAL'), detailed_data.get('PAGINA-FINAL'))

            productions.append(production)
        return productions

    def get_event_papers_list(self, element, natureza):
        if not element:
            return []
        productions = []
        for paper in element.findall("TRABALHO-EM-EVENTOS/DADOS-BASICOS-DO-TRABALHO[@NATUREZA='{}']/..".format(natureza)):
            if natureza == 'COMPLETO':
                production = TrabalhoCompletoEmCongresso(self.id_lattes)
            elif natureza == 'RESUMO_EXPANDIDO':
                production = ResumoExpandidoEmCongresso(self.id_lattes)
            elif natureza == 'RESUMO':
                production = ResumoEmCongresso(self.id_lattes)
            else:
                logger.error("Natureza '{}' inválida.".format(natureza))
                return productions

            production.autores = '; '.join(author.get('NOME-PARA-CITACAO') for author in paper.findall('./AUTORES'))  # FIXME: perdendo informação ao concatenar

            basic_data = paper.find('./DADOS-BASICOS-DO-TRABALHO')
            production.titulo = basic_data.get('TITULO-DO-TRABALHO')
            production.ano = basic_data.get('ANO-DO-TRABALHO')
            doi = basic_data.get('DOI')
            production.doi = 'http://dx.doi.org/' + doi if doi else ''
            relevante = basic_data.get('FLAG-RELEVANCIA')
            production.relevante = True if relevante == 'SIM' else False

            detailed_data = paper.find('./DETALHAMENTO-DO-TRABALHO')
            production.nomeDoEvento = detailed_data.get('NOME-DO-EVENTO')
            production.isbn = detailed_data.get('ISBN')
            production.volume = detailed_data.get('VOLUME')
            # production.numero = paper.find('./DETALHAMENTO-DO-ARTIGO').get('FASCICULO')
            production.paginas = "{}-{}".format(detailed_data.get('PAGINA-INICIAL'), detailed_data.get('PAGINA-FINAL'))

            productions.append(production)
        return productions

    def get_books_list(self, books):
        productions = []
        for book in books:
            production = LivroPublicado(self.id_lattes)

            production.autores = '; '.join(author.get('NOME-PARA-CITACAO') for author in book.findall('./AUTORES'))  # FIXME: perdendo informação ao concatenar

            basic_data = book.find('./DADOS-BASICOS-DO-LIVRO')
            production.titulo = basic_data.get('TITULO-DO-LIVRO')
            production.ano = basic_data.get('ANO')
            doi = basic_data.get('DOI')
            production.doi = 'http://dx.doi.org/' + doi if doi else ''
            relevante = basic_data.get('FLAG-RELEVANCIA')
            production.relevante = True if relevante == 'SIM' else False

            detailed_data = book.find('./DETALHAMENTO-DO-LIVRO')
            production.isbn = detailed_data.get('ISBN')
            production.volume = detailed_data.get('NUMERO-DE-VOLUMES')
            production.edicao = detailed_data.get('NUMERO-DA-EDICAO-REVISAO')
            production.editora = detailed_data.get('NOME-DA-EDITORA')
            production.paginas = detailed_data.get('NUMERO-DE-PAGINAS')

            productions.append(production)
        return productions

    def get_book_chapters_list(self, books):
        productions = []
        for book in books:
            production = CapituloDeLivroPublicado(self.id_lattes)

            production.autores = '; '.join(author.get('NOME-PARA-CITACAO') for author in book.findall('./AUTORES'))  # FIXME: perdendo informação ao concatenar

            basic_data = book.find('./DADOS-BASICOS-DO-CAPITULO')
            production.titulo = basic_data.get('TITULO-DO-CAPITULO-DO-LIVRO')
            production.ano = basic_data.get('ANO')
            doi = basic_data.get('DOI')
            production.doi = 'http://dx.doi.org/' + doi if doi else ''
            relevante = basic_data.get('FLAG-RELEVANCIA')
            production.relevante = True if relevante == 'SIM' else False

            detailed_data = book.find('./DETALHAMENTO-DO-CAPITULO')
            production.livro = detailed_data.get('TITULO-DO-LIVRO')
            production.isbn = detailed_data.get('ISBN')
            production.volume = detailed_data.get('NUMERO-DE-VOLUMES')
            production.edicao = detailed_data.get('NUMERO-DA-EDICAO-REVISAO')
            production.editora = detailed_data.get('NOME-DA-EDITORA')
            production.paginas = "{}-{}".format(detailed_data.get('PAGINA-INICIAL'), detailed_data.get('PAGINA-FINAL'))

            productions.append(production)
        return productions

    def get_newspaper_texts_list(self, items):
        productions = []
        for item in items:
            production = TextoEmJornalDeNoticia(self.id_lattes)

            production.autores = '; '.join(author.get('NOME-PARA-CITACAO') for author in item.findall('./AUTORES'))  # FIXME: perdendo informação ao concatenar

            basic_data = item.find('./DADOS-BASICOS-DO-TEXTO')
            production.titulo = basic_data.get('TITULO-DO-TEXTO')
            production.ano = basic_data.get('ANO-DO-TEXTO')
            doi = basic_data.get('DOI')
            production.doi = 'http://dx.doi.org/' + doi if doi else ''
            relevante = basic_data.get('FLAG-RELEVANCIA')
            production.relevante = True if relevante == 'SIM' else False
            production.natureza = basic_data.get('NATUREZA')

            detailed_data = item.find('./DETALHAMENTO-DO-TEXTO')
            production.nomeJornal = detailed_data.get('TITULO-DO-JORNAL-OU-REVISTA')
            production.data = detailed_data.get('DATA-DE-PUBLICACAO')
            production.issn = detailed_data.get('ISSN')
            production.volume = detailed_data.get('VOLUME')
            production.paginas = "{}-{}".format(detailed_data.get('PAGINA-INICIAL'), detailed_data.get('PAGINA-FINAL'))

            productions.append(production)
        return productions

    def get_other_productions_list(self, items):
        productions = []
        for item in items:
            production = OutroTipoDeProducaoBibliografica(self.id_lattes)

            production.autores = '; '.join(author.get('NOME-PARA-CITACAO') for author in item.findall('./AUTORES'))  # FIXME: perdendo informação ao concatenar

            basic_data = item.find('./DADOS-BASICOS-DE-OUTRA-PRODUCAO')
            production.titulo = basic_data.get('TITULO')
            production.ano = basic_data.get('ANO')
            doi = basic_data.get('DOI')
            production.doi = 'http://dx.doi.org/' + doi if doi else ''
            relevante = basic_data.get('FLAG-RELEVANCIA')
            production.relevante = True if relevante == 'SIM' else False
            production.natureza = basic_data.get('NATUREZA')

            detailed_data = item.find('./DETALHAMENTO-DE-OUTRA-PRODUCAO')
            production.editora = detailed_data.get('EDITORA')
            production.issn = detailed_data.get('ISSN-ISBN')
            production.paginas = detailed_data.get('NUMERO-DE-PAGINAS')

            productions.append(production)
        return productions

    def set_technical_productions(self, element):
        # PRODUCAO-TECNICA (CULTIVAR-REGISTRADA*,SOFTWARE*, PATENTE*, CULTIVAR-PROTEGIDA*, DESENHO-INDUSTRIAL*, MARCA*, TOPOGRAFIA-DE-CIRCUITO-INTEGRADO*,
        #                   PRODUTO-TECNOLOGICO*, PROCESSOS-OU-TECNICAS*, TRABALHO-TECNICO*, DEMAIS-TIPOS-DE-PRODUCAO-TECNICA*)>
        # SOFTWARE (DADOS-BASICOS-DO-SOFTWARE?, DETALHAMENTO-DO-SOFTWARE?, AUTORES*
        self.softwares = BasicProduction(id=self.id_lattes).add_from_xml_elements(element.xpath('SOFTWARE'))
        self.produtos_tecnologicos = BasicProduction(id=self.id_lattes).add_from_xml_elements(element.xpath('PRODUTO-TECNOLOGICO'))
        self.processos_ou_tecnicas = BasicProduction(id=self.id_lattes).add_from_xml_elements(element.xpath('PROCESSOS-OU-TECNICAS'))
        self.trabalhos_tecnicos = BasicProduction(id=self.id_lattes).add_from_xml_elements(element.xpath('TRABALHO-TECNICO'))

        self.demais_tipos_de_producao_tecnica = BasicProduction(id=self.id_lattes)
        # APRESENTACAO-DE-TRABALHO*, CARTA-MAPA-OU-SIMILAR*, CURSO-DE-CURTA-DURACAO-MINISTRADO*, DESENVOLVIMENTO-DE-MATERIAL-DIDATICO-OU-INSTRUCIONAL*, EDITORACAO*, MANUTENCAO-DE-OBRA-ARTISTICA*, MAQUETE*, ORGANIZACAO-DE-EVENTO*, PROGRAMA-DE-RADIO-OU-TV*, RELATORIO-DE-PESQUISA*,MIDIA-SOCIAL-WEBSITE-BLOG*, OUTRA-PRODUCAO-TECNICA*
        self.demais_tipos_de_producao_tecnica.add_from_xml_elements(element.xpath('DEMAIS-TIPOS-DE-PRODUCAO-TECNICA/*'))
        # self.demais_tipos_de_producao_tecnica.add_from_xml_elements(element.xpath('DEMAIS-TIPOS-DE-PRODUCAO-TECNICA/OUTRA-PRODUCAO-TECNICA'))

    def set_artistic_productions(self, element):
        # OUTRA-PRODUCAO (PRODUCAO-ARTISTICA-CULTURAL*, ORIENTACOES-CONCLUIDAS*, DEMAIS-TRABALHOS*)
        # PRODUCAO-ARTISTICA-CULTURAL (APRESENTACAO-DE-OBRA-ARTISTICA*, APRESENTACAO-EM-RADIO-OU-TV*, ARRANJO-MUSICAL*, COMPOSICAO-MUSICAL*, CURSO-DE-CURTA-DURACAO*, OBRA-DE-ARTES-VISUAIS*, OUTRA-PRODUCAO-ARTISTICA-CULTURAL*, SONOPLASTIA*,ARTES-CENICAS*,ARTES-VISUAIS*,MUSICA*)
        self.artistic_productions = BasicProduction(id=self.id_lattes)
        self.artistic_productions.add_from_xml_elements(element.xpath('*'))
