#!/usr/bin/python
# -*- coding: utf-8 -*-
# filename: geradorDePaginasWeb

import datetime
import logging
import os
import re
import unicodedata
from collections import defaultdict, OrderedDict
from pathlib import Path

import dateutil
import pandas
from jinja2.environment import Environment
from jinja2.loaders import PackageLoader
from pandas.core.indexing import IndexingError

import membro
from report import file_generator
from report.charts.graficoDeInternacionalizacao import *
from report.charts.highcharts import highchart, chart_type

logger = logging.getLogger('scriptLattes')


class WebPagesGenerator:
    # arquivoRis = None

    def __init__(self, grupo, output_directory, version, admin_email=None, google_analytics_key=None):
        assert isinstance(output_directory, Path)

        self.grupo = grupo
        self.output_directory = output_directory
        self.jinja = Environment(loader=PackageLoader('scriptLattes', 'templates'))

        # # geracao de arquivo RIS com as publicacoes
        # # FIXME: mover para fora daqui
        # if self.grupo.obterParametro('relatorio-salvar_publicacoes_em_formato_ris'):
        #     prefix = self.grupo.obterParametro('global-prefixo') + '-' if not self.grupo.obterParametro(
        #         'global-prefixo') == '' else ''
        #     self.arquivoRis = open(self.dir + "/" + prefix + "publicacoes.ris", 'w')

        self.global_template_vars = {
            # "group": self.grupo,
            "group_name": self.grupo.name,
            "version": version,
            # "timestamp": datetime.datetime.isoformat(datetime.datetime.now(dateutil.tz.tzlocal())),
        }
        if admin_email:
            self.global_template_vars["admin_email"] = admin_email
        if google_analytics_key:
            self.global_template_vars["google_analytics_key"] = google_analytics_key

        # Format: (page, title, object, template)
        # template is a relative path; check self.jinja initialization
        self.bibliographical_productions_routes = [
            ("PB0-0.html", u"Artigos completos publicados em periódicos", self.grupo.journal_papers.published,
             "bibliographical_production/journal_papers_list.html"),
            ("PB7-0.html", u"Artigos aceitos para publicação", self.grupo.journal_papers.only_accepted, "bibliographical_production/journal_papers_list.html"),
            ("PB4-0.html", u"Trabalhos completos publicados em anais de congressos ", self.grupo.event_papers.complete,
             "bibliographical_production/event_papers_list.html"),
            ("PB5-0.html", u"Resumos expandidos publicados em anais de congressos ", self.grupo.event_papers.abstract,
             "bibliographical_production/event_papers_list.html"),
            ("PB6-0.html", u"Resumos publicados em anais de congressos ", self.grupo.event_papers.expanded_abstract,
             "bibliographical_production/event_papers_list.html"),
            ("PB1-0.html", u"Livros publicados/organizados ou edições", self.grupo.books.full, "bibliographical_production/books_list.html"),
            ("PB2-0.html", u"Capítulos de livros publicados ", self.grupo.books.only_chapter, "bibliographical_production/books_list.html"),
            ("PB3-0.html", u"Textos em jornais de notícias/revistas ", self.grupo.newspaper_texts, "bibliographical_production/newspaper_texts_list.html"),
            ("PB8-0.html", u"Apresentações de trabalho ", self.grupo.presentations, "bibliographical_production/presentations_list.html"),
            ("PB9-0.html", u"Demais tipos de produção bibliográfica ", self.grupo.others, "bibliographical_production/others_list.html"),
            ("PB-0.html", u"Produção bibliográfica total", self.grupo.bibliographical_productions,
             "bibliographical_production/bibliographical_productions_list.html"),
        ]

    def generate(self):
        self.gerar_pagina_de_membros()
        # self.gerar_pagina_de_producao_qualificado_por_membro()
        self.generate_bibliographical_production_pages(routes=self.bibliographical_productions_routes)
        # self.gerarPaginasDeProducoesTecnicas()
        # self.gerarPaginasDeProducoesArtisticas()
        # self.gerarPaginasDePatentes()
        #
        # if self.grupo.obterParametro('relatorio-mostrar_orientacoes'):
        #     self.gerarPaginasDeOrientacoes()
        #
        # if self.grupo.obterParametro('relatorio-incluir_projeto'):
        #     self.gerarPaginasDeProjetos()
        #
        # if self.grupo.obterParametro('relatorio-incluir_premio'):
        #     self.gerarPaginasDePremios()
        #
        # if self.grupo.obterParametro('relatorio-incluir_participacao_em_evento'):
        #     self.gerarPaginasDeParticipacaoEmEventos()
        #
        # if self.grupo.obterParametro('relatorio-incluir_organizacao_de_evento'):
        #     self.gerarPaginasDeOrganizacaoDeEventos()
        #
        # if self.grupo.obterParametro('grafo-mostrar_grafo_de_colaboracoes'):
        #     self.gerarPaginaDeGrafosDeColaboracoes()
        #
        # if self.grupo.obterParametro('relatorio-incluir_internacionalizacao'):
        #     self.gerarPaginasDeInternacionalizacao()

        # final do fim!
        self.generate_index_page()

    def generate_index_page(self):
        file_name = 'index.html'
        index_template = self.jinja.get_template(file_name)

        template_vars = self.global_template_vars
        template_vars.update({
            "mostrar_mapa_de_geolocalizacao": False,  # FIXME: self.grupo.obterParametro('mapa-mostrar_mapa_de_geolocalizacao')
            "group": self.grupo,
            "timestamp": datetime.datetime.isoformat(datetime.datetime.now(dateutil.tz.tzlocal())),
        })

        # Ou
        # if self.grupo.obterParametro('mapa-mostrar_mapa_de_geolocalizacao')
        # <body onload="initialize()" onunload="GUnload()"> # FIXME: initialize é do mapa

        bibliographical_productions_index = [
            (page, title, len(production)) for page, title, production, _ in self.bibliographical_productions_routes
            ]
        template_vars["bibliographical_productions_index"] = bibliographical_productions_index

        s = index_template.render(template_vars).encode("utf-8")
        file_path = self.output_directory / file_name
        file_generator.save_string_to_file(s, file_path)

        return

        s += '</ul>' \
             ' <h3 id="producaoTecnica">Produção técnica</h3> <ul>'.decode("utf8")
        if self.nPT0 > 0:
            s += '<li> <a href="PT0-0' + self.extensaoPagina + '">Programas de computador com registro de patente</a> '.decode(
                "utf8") + '(' + str(self.nPT0) + ')'
        if self.nPT1 > 0:
            s += '<li> <a href="PT1-0' + self.extensaoPagina + '">Programas de computador sem registro de patente</a> '.decode(
                "utf8") + '(' + str(self.nPT1) + ')'
        if self.nPT2 > 0:
            s += '<li> <a href="PT2-0' + self.extensaoPagina + '">Produtos tecnológicos</a> '.decode(
                "utf8") + '(' + str(self.nPT2) + ')'
        if self.nPT3 > 0:
            s += '<li> <a href="PT3-0' + self.extensaoPagina + '">Processos ou técnicas</a> '.decode(
                "utf8") + '(' + str(self.nPT3) + ')'
        if self.nPT4 > 0:
            s += '<li> <a href="PT4-0' + self.extensaoPagina + '">Trabalhos técnicos</a> '.decode("utf8") + '(' + str(
                self.nPT4) + ')'
        if self.nPT5 > 0:
            s += '<li> <a href="PT5-0' + self.extensaoPagina + '">Demais tipos de produção técnica</a> '.decode(
                "utf8") + '(' + str(self.nPT5) + ')'
        if self.nPT > 0:
            s += '<li> <a href="PT-0' + self.extensaoPagina + '">Total de produção técnica</a> '.decode(
                "utf8") + '(' + str(self.nPT) + ')'
        else:
            s += '<i>Nenhum item achado nos currículos Lattes</i>'.decode("utf8")


            # s+='</ul> <h3 id="patenteRegistro">Patente e Registro</h3> <ul>'.decode("utf8")
        # if self.nPR0>0:
        #	s+= '<li> <a href="PR0-0'+self.extensaoPagina+'">Patente</a> '.decode("utf8")+'('+str(self.nPR0)+')'
        # if self.nPR1>0:
        #	s+= '<li> <a href="PR1-0'+self.extensaoPagina+'">Programa de computador</a> '.decode("utf8")+'('+str(self.nPR1)+')'
        # if self.nPR2>0:
        #	s+= '<li> <a href="PR2-0'+self.extensaoPagina+'">Desenho industrial</a> '.decode("utf8")+'('+str(self.nPR2)+')'
        # if self.nPR0 == 0 and self.nPR1 == 0 and self.nPR2 == 0:
        #	s+= '<i>Nenhum item achado nos currículos Lattes</i>'.decode("utf8")


        s += '</ul>' \
             ' <h3 id="producaoArtistica">Produção artística</h3> <ul>'.decode("utf8")
        if self.nPA > 0:
            s += '<li> <a href="PA-0' + self.extensaoPagina + '">Total de produção artística</a> '.decode(
                "utf8") + '(' + str(self.nPA) + ')'
        else:
            s += '<i>Nenhum item achado nos currículos Lattes</i>'.decode("utf8")

        if self.grupo.obterParametro('relatorio-mostrar_orientacoes'):
            s += '</ul>' \
                 ' <h3 id="orientacoes">Orientações</h3> <ul>'.decode("utf8")
            s += '<li><b>Orientações em andamento</b>'.decode("utf8")
            s += '<ul>'
            if self.nOA0 > 0:
                s += '<li> <a href="OA0-0' + self.extensaoPagina + '">Supervisão de pós-doutorado</a> '.decode(
                    "utf8") + '(' + str(self.nOA0) + ')'
            if self.nOA1 > 0:
                s += '<li> <a href="OA1-0' + self.extensaoPagina + '">Tese de doutorado</a> '.decode(
                    "utf8") + '(' + str(self.nOA1) + ')'
            if self.nOA2 > 0:
                s += '<li> <a href="OA2-0' + self.extensaoPagina + '">Dissertação de mestrado</a> '.decode(
                    "utf8") + '(' + str(self.nOA2) + ')'
            if self.nOA3 > 0:
                s += '<li> <a href="OA3-0' + self.extensaoPagina + '">Monografia de conclusão de curso de aperfeiçoamento/especialização</a> '.decode(
                    "utf8") + '(' + str(self.nOA3) + ')'
            if self.nOA4 > 0:
                s += '<li> <a href="OA4-0' + self.extensaoPagina + '">Trabalho de conclusão de curso de graduação</a> '.decode(
                    "utf8") + '(' + str(self.nOA4) + ')'
            if self.nOA5 > 0:
                s += '<li> <a href="OA5-0' + self.extensaoPagina + '">Iniciação científica</a> '.decode(
                    "utf8") + '(' + str(self.nOA5) + ')'
            if self.nOA6 > 0:
                s += '<li> <a href="OA6-0' + self.extensaoPagina + '">Orientações de outra natureza</a> '.decode(
                    "utf8") + '(' + str(self.nOA6) + ')'
            if self.nOA > 0:
                s += '<li> <a href="OA-0' + self.extensaoPagina + '">Total de orientações em andamento</a> '.decode(
                    "utf8") + '(' + str(self.nOA) + ')'
            else:
                s += '<i>Nenhum item achado nos currículos Lattes</i>'.decode("utf8")
            s += '</ul>'

            s += '<li><b>Supervisões e orientações concluídas</b>'.decode("utf8")
            s += '<ul>'
            if self.nOC0 > 0:
                s += '<li> <a href="OC0-0' + self.extensaoPagina + '">Supervisão de pós-doutorado</a> '.decode(
                    "utf8") + '(' + str(self.nOC0) + ')'
            if self.nOC1 > 0:
                s += '<li> <a href="OC1-0' + self.extensaoPagina + '">Tese de doutorado</a> '.decode(
                    "utf8") + '(' + str(self.nOC1) + ')'
            if self.nOC2 > 0:
                s += '<li> <a href="OC2-0' + self.extensaoPagina + '">Dissertação de mestrado</a> '.decode(
                    "utf8") + '(' + str(self.nOC2) + ')'
            if self.nOC3 > 0:
                s += '<li> <a href="OC3-0' + self.extensaoPagina + '">Monografia de conclusão de curso de aperfeiçoamento/especialização</a> '.decode(
                    "utf8") + '(' + str(self.nOC3) + ')'
            if self.nOC4 > 0:
                s += '<li> <a href="OC4-0' + self.extensaoPagina + '">Trabalho de conclusão de curso de graduação</a> '.decode(
                    "utf8") + '(' + str(self.nOC4) + ')'
            if self.nOC5 > 0:
                s += '<li> <a href="OC5-0' + self.extensaoPagina + '">Iniciação científica</a> '.decode(
                    "utf8") + '(' + str(self.nOC5) + ')'
            if self.nOC6 > 0:
                s += '<li> <a href="OC6-0' + self.extensaoPagina + '">Orientações de outra natureza</a> '.decode(
                    "utf8") + '(' + str(self.nOC6) + ')'
            if self.nOC > 0:
                s += '<li> <a href="OC-0' + self.extensaoPagina + '">Total de orientações concluídas</a> '.decode(
                    "utf8") + '(' + str(self.nOC) + ')'
            else:
                s += '<i>Nenhum item achado nos currículos Lattes</i>'.decode("utf8")
            s += '</ul>'

        if self.grupo.obterParametro('relatorio-incluir_projeto'):
            s += '</ul> <h3 id="projetos">Projetos de pesquisa</h3> <ul>'.decode("utf8")
            if self.nPj > 0:
                s += '<li> <a href="Pj-0' + self.extensaoPagina + '">Total de projetos de pesquisa</a> '.decode(
                    "utf8") + '(' + str(self.nPj) + ')'
            else:
                s += '<i>Nenhum item achado nos currículos Lattes</i>'.decode("utf8")
            s += '</ul>'

        if self.grupo.obterParametro('relatorio-incluir_premio'):
            s += '</ul> <h3 id="premios">Prêmios e títulos</h3> <ul>'.decode("utf8")
            if self.nPm > 0:
                s += '<li> <a href="Pm-0' + self.extensaoPagina + '">Total de prêmios e títulos</a> '.decode(
                    "utf8") + '(' + str(self.nPm) + ')'
            else:
                s += '<i>Nenhum item achado nos currículos Lattes</i>'.decode("utf8")
            s += '</ul>'

        if self.grupo.obterParametro('relatorio-incluir_participacao_em_evento'):
            s += '</ul> <h3 id="eventos">Participação em eventos</h3> <ul>'.decode("utf8")
            if self.nEp > 0:
                s += '<li> <a href="Ep-0' + self.extensaoPagina + '">Total de participação em eventos</a> '.decode(
                    "utf8") + '(' + str(self.nEp) + ')'
            else:
                s += '<i>Nenhum item achado nos currículos Lattes</i>'.decode("utf8")
            s += '</ul>'

        if self.grupo.obterParametro('relatorio-incluir_organizacao_de_evento'):
            s += '</ul> <h3 id="eventos">Organização de eventos</h3> <ul>'.decode("utf8")
            if self.nEo > 0:
                s += '<li> <a href="Eo-0' + self.extensaoPagina + '">Total de organização de eventos</a> '.decode(
                    "utf8") + '(' + str(self.nEo) + ')'
            else:
                s += '<i>Nenhum item achado nos currículos Lattes</i>'.decode("utf8")
            s += '</ul>'

        if self.grupo.obterParametro('grafo-mostrar_grafo_de_colaboracoes'):
            s += '</ul> <h3 id="grafo">Grafo de colaborações</h3> <ul>'.decode("utf8")
            s += '<a href="grafoDeColaboracoes' + self.extensaoPagina + '"><img src="grafoDeColaboracoesSemPesos-t.png" border=1> </a>'
        s += '</ul>'

        if self.grupo.obterParametro('mapa-mostrar_mapa_de_geolocalizacao'):
            s += '<h3 id="mapa">Mapa de geolocaliza&ccedil;&atilde;o</h3> <br> <div id="map_canvas" style="width: 800px; height: 600px"></div> <br>'
            s += '<b>Legenda</b><table>'
            if self.grupo.obterParametro('mapa-incluir_membros_do_grupo'):
                s += '<tr><td> <img src=lattesPoint0.png></td> <td> Membro (orientador) </td></tr>'.decode("utf8")
            if self.grupo.obterParametro('mapa-incluir_alunos_de_pos_doutorado'):
                s += '<tr><td> <img src=lattesPoint1.png></td> <td>  Pesquisador com pós-doutorado concluído e ID Lattes cadastrado no currículo do supervisor </td></tr>'.decode(
                    "utf8")
            if self.grupo.obterParametro('mapa-incluir_alunos_de_doutorado'):
                s += '<tr><td> <img src=lattesPoint2.png></td> <td>  Aluno com doutorado concluído e ID Lattes cadastrado no currículo do orientador </td></tr>'.decode(
                    "utf8")
            if self.grupo.obterParametro('mapa-incluir_alunos_de_mestrado'):
                s += '<tr><td> <img src=lattesPoint3.png></td> <td>  Aluno com mestrado e ID Lattes cadastrado no currículo do orientador </td></tr>'.decode(
                    "utf8")
            s += '</table>'

        if self.grupo.obterParametro('relatorio-incluir_internacionalizacao'):
            s += '</ul> <h3 id="internacionalizacao">Internacionalização</h3> <ul>'.decode("utf8")
            if self.nIn0 > 0:
                s += '<li> <a href="In0-0' + self.extensaoPagina + '">Coautoria e internacionalização</a> '.decode(
                    "utf8") + '(' + str(self.nIn0) + ')'
            else:
                s += '<i>Nenhuma publicação com DOI disponível para análise</i>'.decode("utf8")
            s += '</ul>'

    def gerar_pagina_de_membros(self):
        file_name = 'membros.html'
        template = self.jinja.get_template(file_name)

        template_vars = dict(self.global_template_vars)
        template_vars.update({
            "timestamp": datetime.datetime.isoformat(datetime.datetime.now(dateutil.tz.tzlocal())),
            "members_list": self.grupo.members_list.values(),
        })

        s = template.render(template_vars).encode("utf-8")
        file_path = self.output_directory / file_name
        file_generator.save_string_to_file(s, file_path)

        # FIXME: em quais circunstâncias este '-grp' aparece no rótulo de um membro?
        # if "-grp[" in rotulo:
        #     multirotulos = rotulo.split("::")
        #     rotulo = ""
        #     for r in multirotulos:
        #         grupoURL = "http://dgp.cnpq.br/buscaoperacional/detalhegrupo.jsp?grupo=" + re.search('\[(.*)\]', r.strip()).group(1)
        #         rotulo = rotulo + "<a href=" + grupoURL + ">" + r.strip() + "</a><br>"
        #
        # nomeCompleto = unicodedata.normalize('NFKD', membro.nomeCompleto).encode('ASCII', 'ignore')

    def generate_production_page(self, productions, template_name, title, page, group_by='ano', ascending=True, ris=False):
        # template = self.jinja.get_template("list.html")
        template = self.jinja.get_template(template_name)
        file_name = page

        template_vars = self.global_template_vars.copy()
        template_vars.update({
            "timestamp": datetime.datetime.isoformat(datetime.datetime.now(dateutil.tz.tzlocal())),
            "subtitle": title,
            "numero_itens": len(productions),
            "totais_qualis": None,
            "indice_paginas": None,
        })

        # assert isinstance(productions, pandas.DataFrame)
        productions_by_year = productions.ordered_dict_by(key_by=group_by, ascending=ascending)
        template_vars["grouped_productions"] = productions_by_year
        chart = self.gerar_grafico_de_producoes(productions_by_year)
        # jsondata = json.dumps(chart)
        # jsondata = chart.json()
        template_vars["chart"] = chart  #{"jsondata": jsondata, "height": chart['chart']['height']}

        s = template.render(template_vars).encode("utf-8")
        file_path = self.output_directory / file_name
        file_generator.save_string_to_file(s, file_path)

        return
        ##############################
        # totais_qualis = ""
        # if self.grupo.obterParametro('global-identificar_publicacoes_com_qualis'):
        #     if self.grupo.obterParametro('global-arquivo_qualis_de_periodicos'):  # FIXME: nao está mais sendo usado agora que há qualis online
        #         if prefixo == 'PB0':
        #             totais_qualis = self.formatarTotaisQualis(self.grupo.qualis.qtdPB0)
        #     if self.grupo.obterParametro('global-arquivo_qualis_de_congressos'):
        #         if prefixo == 'PB4':
        #             totais_qualis = self.formatarTotaisQualis(self.grupo.qualis.qtdPB4)
        #         elif prefixo == 'PB5':
        #             totais_qualis = self.formatarTotaisQualis(self.grupo.qualis.qtdPB5)

        # total_producoes = sum(len(v) for v in lista_completa.values())
        #
        # keys = sorted(lista_completa.keys(), reverse=True)
        # if keys:  # apenas geramos páginas web para lista com pelo menos 1 elemento
        #     max_elementos = int(self.grupo.obterParametro('global-itens_por_pagina'))
        #     total_paginas = int(math.ceil(total_producoes / (max_elementos * 1.0)))  # dividimos os relatórios em grupos (e.g 1000 items)
        #
        #     grafico = self.gerar_grafico_de_producoes(lista_completa, titulo_pagina)  # FIXME: é o mesmo gráfico em todas as páginas
        #
        #     anos_indices_publicacoes = self.arranjar_publicacoes(lista_completa)
        #     itens_por_pagina = self.chunks(anos_indices_publicacoes, max_elementos)
        #     for numero_pagina, itens in enumerate(itens_por_pagina):
        #         producoes_html = ''
        #         for indice_na_pagina, (ano, indice_no_ano, publicacao) in enumerate(itens):
        #             # armazenamos uma copia da publicacao (formato RIS)
        #             if ris and self.grupo.obterParametro('relatorio-salvar_publicacoes_em_formato_ris'):
        #                 self.salvarPublicacaoEmFormatoRIS(publicacao)
        #
        #             if indice_na_pagina == 0 or indice_no_ano == 0:
        #                 if indice_na_pagina > 0:
        #                     producoes_html += '</table></div>'
        #                 producoes_html += '<div id="dv-year-{0}"><h3 class="year">{0}</h3> <table>'.format(
        #                     ano if ano else '*itens sem ano')
        #
        #             producao_html = self.template_producao()
        #             producao_html = producao_html.format(indice=indice_no_ano + 1,
        #                                                  publicacao=publicacao.html(self.grupo.members_list.values()))
        #             producoes_html += producao_html
        #         producoes_html += '</table></div>'
        #
        #         pagina_html = self.template_pagina_de_producoes()
        #         pagina_html = pagina_html.format(top=self.pagina_top(), bottom=self.paginaBottom(),
        #                                          grafico=grafico.html(), height=grafico['chart']['height'],
        #                                          titulo=titulo_pagina.decode("utf8"), numero_itens=str(total_producoes),
        #                                          totais_qualis=totais_qualis,
        #                                          indice_paginas=self.gerarIndiceDePaginas(total_paginas, numero_pagina,
        #                                                                                   prefixo),
        #                                          producoes=producoes_html)
        #         self.salvarPagina(prefixo + '-' + str(numero_pagina) + self.extensaoPagina, pagina_html)
        # return total_producoes

    def generate_bibliographical_production_pages(self, routes):

        for page, title, productions, template in routes:
            self.generate_production_page(productions, group_by='ano', ascending=False,
                                          template_name=template,  # self.grupo.compilador.listaCompletaPB,
                                          title=title, page=page)
        return
        #########################################
        # FIXME: refatorar

        # if self.grupo.obterParametro('relatorio-incluir_artigo_em_periodico'):
        if self.grupo.obterParametro('relatorio-incluir_livro_publicado'):
            self.nPB1 = self.generate_production_page(self.grupo.compilador.listaCompletaLivroPublicado,
                                                      "Livros publicados/organizados ou edições", "PB1", ris=True)
        if self.grupo.obterParametro('relatorio-incluir_capitulo_de_livro_publicado'):
            self.nPB2 = self.generate_production_page(self.grupo.compilador.listaCompletaCapituloDeLivroPublicado,
                                                      "Capítulos de livros publicados", "PB2", ris=True)
        if self.grupo.obterParametro('relatorio-incluir_texto_em_jornal_de_noticia'):
            self.nPB3 = self.generate_production_page(self.grupo.compilador.listaCompletaTextoEmJornalDeNoticia,
                                                      "Textos em jornais de notícias/revistas", "PB3", ris=True)
        # if self.grupo.obterParametro('relatorio-incluir_trabalho_completo_em_congresso'):
        # if self.grupo.obterParametro('relatorio-incluir_resumo_expandido_em_congresso'):
        # if self.grupo.obterParametro('relatorio-incluir_resumo_em_congresso'):
        if self.grupo.obterParametro('relatorio-incluir_artigo_aceito_para_publicacao'):
            self.nPB7 = self.generate_production_page(self.grupo.compilador.listaCompletaArtigoAceito,
                                                      "Artigos aceitos para publicação", "PB7")
        if self.grupo.obterParametro('relatorio-incluir_apresentacao_de_trabalho'):
            self.nPB8 = self.generate_production_page(self.grupo.compilador.listaCompletaApresentacaoDeTrabalho,
                                                      "Apresentações de trabalho", "PB8")
        if self.grupo.obterParametro('relatorio-incluir_outro_tipo_de_producao_bibliografica'):
            self.nPB9 = self.generate_production_page(
                self.grupo.compilador.listaCompletaOutroTipoDeProducaoBibliografica,
                "Demais tipos de produção bibliográfica", "PB9")

    @staticmethod
    def gerar_grafico_de_producoes(productions_by_year):
        # FIXME: remover método e gerar gráfico nos templates
        """
        :param productions_by_year:
        :return:
        """
        assert isinstance(productions_by_year, dict)

        categories = sorted(productions_by_year.keys())
        year_frequency = OrderedDict({year: len(productions_by_year[year]) for year in categories})

        areas_map = {'': 0}
        estrato_area_ano_freq = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        for ano, publicacoes in sorted(productions_by_year.items()):
            assert isinstance(publicacoes, pandas.DataFrame)
            for i, pub in publicacoes.iterrows():
                try:
                    if not pub.qualis:
                        logger.debug("qualis is None")
                        estrato_area_ano_freq[''][''][ano] += 1  # sem qualis
                    else:
                        if type(pub.qualis) is str:  # sem area
                            logger.debug("publicação com qualis string (sem área): '{}'".format(pub.qualis))
                        else:
                            for area, estrato in sorted(pub.qualis.items()):
                                estrato_area_ano_freq[estrato][area][ano] += 1
                                if area not in areas_map:
                                    areas_map[area] = len(areas_map)
                except AttributeError:
                    logger.debug(u"publicação sem atributo qualis")
                    estrato_area_ano_freq[''][''][ano] += 1  # producao que nao tem qualis

        return {'data': year_frequency, 'categories': categories, 'qualis_data': estrato_area_ano_freq}

        series = []
        if not estrato_area_ano_freq.keys():  # produções vazias
            logger.debug("Nenhuma produção: {}".format(type(productions_by_year.values())))
        elif not detect_chart_type or len(list(estrato_area_ano_freq.keys())) == 1 and None in estrato_area_ano_freq.keys():  # gráfico normal sem qualis

            # freq = [estrato_area_ano_freq[None][None][ano] for ano in categories]
            # series.append({'name': u'Total', 'data': freq})
            # chart.set_x_categories(categories)

            data = [[ano, estrato_area_ano_freq[None][None][ano]] for ano in categories]
            # for ano in categories:
            #     freq = estrato_area_ano_freq[None][None][ano]
            #     data.append([ano, freq])
            series.append({'name': u'Total', 'data': data})

        else:  # gráficos com informações sobre qualis
            drilldown_series = []
            for estrato, area_ano_freq in sorted(estrato_area_ano_freq.items(),
                                                 key=lambda x: (x[0] is not None, x[0])):  # Py3 raises error when sorting None values
                if not estrato:
                    estrato = 'Sem Qualis'
                data = []
                # for area, ano_freq in area_ano_freq.items():
                for area in sorted(areas_map.keys(), key=lambda x: (x is not None, x)):
                    ano_freq = area_ano_freq[area]
                    freq = [ano_freq[ano] for ano in categories]
                    if not area:
                        area = u'Sem área'
                    data.append({'name': area, 'y': sum(freq), 'drilldown': area + estrato})

                    drilldown_series.append({'id': area + estrato, 'name': estrato, 'data': [[ano, ano_freq[ano]] for ano in categories]})
                one_serie = {'name': estrato, 'data': data}  # , 'stack': area}
                series.append(one_serie)
            chart['drilldown'] = {'series': drilldown_series}

        # chart.set_series(series)
        # return chart
        return series

    def gerarPaginasDeProducoesTecnicas(self):
        self.nPT0 = 0
        self.nPT1 = 0
        self.nPT2 = 0
        self.nPT3 = 0
        self.nPT4 = 0
        self.nPT5 = 0
        self.nPT = 0

        if self.grupo.obterParametro('relatorio-incluir_software_com_patente'):
            self.nPT0 = self.generate_production_page(self.grupo.compilador.listaCompletaSoftwareComPatente,
                                                      "Softwares com registro de patente", "PT0")
        if self.grupo.obterParametro('relatorio-incluir_software_sem_patente'):
            self.nPT1 = self.generate_production_page(self.grupo.compilador.listaCompletaSoftwareSemPatente,
                                                      "Softwares sem registro de patente", "PT1")
        if self.grupo.obterParametro('relatorio-incluir_produto_tecnologico'):
            self.nPT2 = self.generate_production_page(self.grupo.compilador.listaCompletaProdutoTecnologico,
                                                      "Produtos tecnológicos", "PT2")
        if self.grupo.obterParametro('relatorio-incluir_processo_ou_tecnica'):
            self.nPT3 = self.generate_production_page(self.grupo.compilador.listaCompletaProcessoOuTecnica,
                                                      "Processos ou técnicas", "PT3")
        if self.grupo.obterParametro('relatorio-incluir_trabalho_tecnico'):
            self.nPT4 = self.generate_production_page(self.grupo.compilador.listaCompletaTrabalhoTecnico,
                                                      "Trabalhos técnicos", "PT4")
        if self.grupo.obterParametro('relatorio-incluir_outro_tipo_de_producao_tecnica'):
            self.nPT5 = self.generate_production_page(self.grupo.compilador.listaCompletaOutroTipoDeProducaoTecnica,
                                                      "Demais tipos de produção técnica", "PT5")
        # Total de produções técnicas
        self.nPT = self.generate_production_page(self.grupo.compilador.listaCompletaPT, "Total de produção técnica",
                                                 "PT")

    def gerarPaginasDeProducoesArtisticas(self):
        self.nPA0 = 0
        self.nPA = 0

        if self.grupo.obterParametro('relatorio-incluir_producao_artistica'):
            self.nPA0 = self.generate_production_page(self.grupo.compilador.listaCompletaProducaoArtistica,
                                                      "Produção artística/cultural", "PA0")
        # Total de produções técnicas
        self.nPA = self.generate_production_page(self.grupo.compilador.listaCompletaPA, "Total de produção artística",
                                                 "PA")

    def gerarPaginasDePatentes(self):
        self.nPR0 = 0
        self.nPR1 = 0
        self.nPR2 = 0
        self.nPR = 0

        # if self.grupo.obterParametro('relatorio-incluir_patente'):

        #	self.nPR0 = self.generate_production_page(self.grupo.compilador.listaCompletaPatente, "Patente", "PR0")
        #	self.nPR1 = self.generate_production_page(self.grupo.compilador.listaCompletaProgramaComputador, "Programa de computador", "PR1")
        #	self.nPR2 = self.generate_production_page(self.grupo.compilador.listaCompletaDesenhoIndustrial, "Desenho industrial", "PR2")

        # Total de produções técnicas

    # self.nPR = self.generate_production_page(self.grupo.compilador.listaCompletaPR, "Total de patentes e registros", "PR")


    def gerarPaginasDeOrientacoes(self):
        self.nOA0 = 0
        self.nOA1 = 0
        self.nOA2 = 0
        self.nOA3 = 0
        self.nOA4 = 0
        self.nOA5 = 0
        self.nOA6 = 0
        self.nOA = 0

        if self.grupo.obterParametro('relatorio-incluir_orientacao_em_andamento_pos_doutorado'):
            self.nOA0 = self.generate_production_page(self.grupo.compilador.listaCompletaOASupervisaoDePosDoutorado,
                                                      "Supervisão de pós-doutorado", "OA0")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_em_andamento_doutorado'):
            self.nOA1 = self.generate_production_page(self.grupo.compilador.listaCompletaOATeseDeDoutorado,
                                                      "Tese de doutorado", "OA1")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_em_andamento_mestrado'):
            self.nOA2 = self.generate_production_page(self.grupo.compilador.listaCompletaOADissertacaoDeMestrado,
                                                      "Dissertação de mestrado", "OA2")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_em_andamento_monografia_de_especializacao'):
            self.nOA3 = self.generate_production_page(self.grupo.compilador.listaCompletaOAMonografiaDeEspecializacao,
                                                      "Monografia de conclusão de curso de aperfeiçoamento/especialização",
                                                      "OA3")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_em_andamento_tcc'):
            self.nOA4 = self.generate_production_page(self.grupo.compilador.listaCompletaOATCC,
                                                      "Trabalho de conclusão de curso de graduação", "OA4")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_em_andamento_iniciacao_cientifica'):
            self.nOA5 = self.generate_production_page(self.grupo.compilador.listaCompletaOAIniciacaoCientifica,
                                                      "Iniciação científica", "OA5")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_em_andamento_outro_tipo'):
            self.nOA6 = self.generate_production_page(self.grupo.compilador.listaCompletaOAOutroTipoDeOrientacao,
                                                      "Orientações de outra natureza", "OA6")
        # Total de orientações em andamento
        self.nOA = self.generate_production_page(self.grupo.compilador.listaCompletaOA,
                                                 "Total de orientações em andamento", "OA")

        self.nOC0 = 0
        self.nOC1 = 0
        self.nOC2 = 0
        self.nOC3 = 0
        self.nOC4 = 0
        self.nOC5 = 0
        self.nOC6 = 0
        self.nOC = 0

        if self.grupo.obterParametro('relatorio-incluir_orientacao_concluida_pos_doutorado'):
            self.nOC0 = self.generate_production_page(self.grupo.compilador.listaCompletaOCSupervisaoDePosDoutorado,
                                                      "Supervisão de pós-doutorado", "OC0")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_concluida_doutorado'):
            self.nOC1 = self.generate_production_page(self.grupo.compilador.listaCompletaOCTeseDeDoutorado,
                                                      "Tese de doutorado", "OC1")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_concluida_mestrado'):
            self.nOC2 = self.generate_production_page(self.grupo.compilador.listaCompletaOCDissertacaoDeMestrado,
                                                      "Dissertação de mestrado", "OC2")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_concluida_monografia_de_especializacao'):
            self.nOC3 = self.generate_production_page(self.grupo.compilador.listaCompletaOCMonografiaDeEspecializacao,
                                                      "Monografia de conclusão de curso de aperfeiçoamento/especialização",
                                                      "OC3")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_concluida_tcc'):
            self.nOC4 = self.generate_production_page(self.grupo.compilador.listaCompletaOCTCC,
                                                      "Trabalho de conclusão de curso de graduação", "OC4")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_concluida_iniciacao_cientifica'):
            self.nOC5 = self.generate_production_page(self.grupo.compilador.listaCompletaOCIniciacaoCientifica,
                                                      "Iniciação científica", "OC5")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_concluida_outro_tipo'):
            self.nOC6 = self.generate_production_page(self.grupo.compilador.listaCompletaOCOutroTipoDeOrientacao,
                                                      "Orientações de outra natureza", "OC6")
        # Total de orientações concluídas
        self.nOC = self.generate_production_page(self.grupo.compilador.listaCompletaOC,
                                                 "Total de orientações concluídas", "OC")

    def gerarPaginasDeProjetos(self):
        self.nPj = 0
        self.nPj = self.generate_production_page(self.grupo.compilador.listaCompletaProjetoDePesquisa,
                                                 "Total de projetos de pesquisa", "Pj")

    def gerarPaginasDePremios(self):
        self.nPm = 0
        self.nPm = self.generate_production_page(self.grupo.compilador.listaCompletaPremioOuTitulo,
                                                 "Total de prêmios e títulos", "Pm")

    def gerarPaginasDeParticipacaoEmEventos(self):
        self.nEp = 0
        self.nEp = self.generate_production_page(self.grupo.compilador.listaCompletaParticipacaoEmEvento,
                                                 "Total de participação em eventos", "Ep")

    def gerarPaginasDeOrganizacaoDeEventos(self):
        self.nEo = 0
        self.nEo = self.generate_production_page(self.grupo.compilador.listaCompletaOrganizacaoDeEvento,
                                                 "Total de organização de eventos", "Eo")

    def gerarPaginasDeInternacionalizacao(self):
        self.nIn0 = 0
        self.nIn0 = self.gerarPaginaDeInternacionalizacao(self.grupo.listaDePublicacoesEinternacionalizacao,
                                                          "Coautoria e internacionalização", "In0")

    @staticmethod
    def arranjar_publicacoes(listaCompleta):
        l = []
        for ano in sorted(listaCompleta.keys(), reverse=True):
            publicacoes = sorted(listaCompleta[ano], key=lambda x: x.chave.lower())
            for indice, publicacao in enumerate(publicacoes):
                l.append((ano, indice, publicacao))
        return l

    @staticmethod
    def chunks(lista, tamanho):
        """ Retorna sucessivos chunks de 'tamanho' a partir da 'lista'
        """
        for i in range(0, len(lista), tamanho):
            yield lista[i:i + tamanho]

    @staticmethod
    def template_pagina_de_producoes():
        raise "deprecated"
        # st = u'''
        #         {top}
        #         {grafico}
        #         <h3>{titulo}</h3> <br>
        #             <div id="container" style="min-width: 310px; max-width: 1920px; height: {height}; margin: 0"></div>
        #             Número total de itens: {numero_itens}<br>
        #             {totais_qualis}
        #             {indice_paginas}
        #             {producoes}
        #             </table>
        #         {bottom}
        #       '''
        # return st

    @staticmethod
    def template_producao():
        s = u'''
            <tr valign="top"><td>{indice}. &nbsp;</td> <td>{publicacao}</td></tr>
            '''
        return s

    def gerarIndiceDePaginas(self, numeroDePaginas, numeroDePaginaAtual, prefixo):
        if numeroDePaginas == 1:
            return ''
        else:
            s = 'Página: '.decode("utf8")
            for i in range(0, numeroDePaginas):
                if i == numeroDePaginaAtual:
                    s += '<b>' + str(i + 1) + '</b> &nbsp;'
                else:
                    s += '<a href="' + prefixo + '-' + str(i) + self.extensaoPagina + '">' + str(i + 1) + '</a> &nbsp;'
            return '<center>' + s + '</center>'

    def gerarPaginaDeInternacionalizacao(self, listaCompleta, tituloPagina, prefixo):
        numeroTotalDeProducoes = 0
        gInternacionalizacao = GraficoDeInternacionalizacao(listaCompleta)
        htmlCharts = gInternacionalizacao.criarGraficoDeBarrasDeOcorrencias()

        keys = listaCompleta.keys()
        keys.sort(reverse=True)
        if len(keys) > 0:  # apenas geramos páginas web para lista com pelo menos 1 elemento
            for ano in keys:
                numeroTotalDeProducoes += len(listaCompleta[ano])

            maxElementos = int(self.grupo.obterParametro('global-itens_por_pagina'))
            numeroDePaginas = int(math.ceil(
                numeroTotalDeProducoes / (maxElementos * 1.0)))  # dividimos os relatórios em grupos (e.g 1000 items)

            numeroDeItem = 1
            numeroDePaginaAtual = 0
            s = ''

            for ano in keys:
                anoRotulo = str(ano) if not ano == 0 else '*itens sem ano'

                s += '<h3 class="year">' + anoRotulo + '</h3> <table>'

                elementos = listaCompleta[ano]
                elementos.sort(
                    key=lambda x: x.chave.lower())  # Ordenamos a lista em forma ascendente (hard to explain!)

                for index in range(0, len(elementos)):
                    pub = elementos[index]
                    s += '<tr valign="top"><td>' + str(index + 1) + '. &nbsp;</td> <td>' + pub.html() + '</td></tr>'

                    if numeroDeItem % maxElementos == 0 or numeroDeItem == numeroTotalDeProducoes:
                        st = self.pagina_top(cabecalho=htmlCharts)
                        st += '\n<h3>' + tituloPagina.decode(
                            "utf8") + '</h3> <br> <center> <table> <tr> <td valign="top"><div id="barchart_div"></div> </td> <td valign="top"><div id="geochart_div"></div> </td> </tr> </table> </center>'
                        st += '<table>'
                        st += '<tr><td>Número total de publicações realizadas SEM parceria com estrangeiros:</td><td>'.decode(
                            "utf8") + str(
                            gInternacionalizacao.numeroDePublicacoesRealizadasSemParceirasComEstrangeiros()) + '</td><td><i>(publicações realizadas só por pesquisadores brasileiros)</i></td></tr>'.decode(
                            "utf8")
                        st += '<tr><td>Número total de publicações realizadas COM parceria com estrangeiros:</td><td>'.decode(
                            "utf8") + str(
                            gInternacionalizacao.numeroDePublicacoesRealizadasComParceirasComEstrangeiros()) + '</td><td></td></tr>'
                        st += '<tr><td>Número total de publicações com parcerias NÂO identificadas:</td><td>'.decode(
                            "utf8") + str(
                            gInternacionalizacao.numeroDePublicacoesComParceriasNaoIdentificadas()) + '</td><td></td></tr>'
                        st += '<tr><td>Número total de publicações com DOI cadastrado:</td><td><b>'.decode(
                            "utf8") + str(numeroTotalDeProducoes) + '</b></td><td></td></tr>'
                        st += '</table>'
                        st += '<br> <font color="red">(*) A estimativa de "coautoria e internacionalização" é baseada na análise automática dos DOIs das publicações cadastradas nos CVs Lattes. A identificação de países, para cada publicação, é feita através de buscas simples de nomes de países.</font><br><p>'.decode(
                            "utf8")

                        st += self.gerarIndiceDePaginas(numeroDePaginas, numeroDePaginaAtual, prefixo)
                        st += s  # .decode("utf8")
                        st += '</table>'
                        st += self.paginaBottom()

                        self.salvarPagina(prefixo + '-' + str(numeroDePaginaAtual) + self.extensaoPagina, st)
                        numeroDePaginaAtual += 1

                        if (index + 1) < len(elementos):
                            s = '<h3 class="year">' + anoRotulo + '</h3> <table>'
                        else:
                            s = ''
                    numeroDeItem += 1

                s += '</table>'
        return numeroTotalDeProducoes

    def gerarPaginaDeGrafosDeColaboracoes(self):
        lista = ''
        if self.grupo.obterParametro('grafo-incluir_artigo_em_periodico'):
            lista += 'Artigos completos publicados em periódicos, '.decode("utf8")
        if self.grupo.obterParametro('grafo-incluir_livro_publicado'):
            lista += 'Livros publicados/organizados ou edições, '.decode("utf8")
        if self.grupo.obterParametro('grafo-incluir_capitulo_de_livro_publicado'):
            lista += 'Capítulos de livros publicados, '.decode("utf8")
        if self.grupo.obterParametro('grafo-incluir_texto_em_jornal_de_noticia'):
            lista += 'Textos em jornais de notícias/revistas, '.decode("utf8")
        if self.grupo.obterParametro('grafo-incluir_trabalho_completo_em_congresso'):
            lista += 'Trabalhos completos publicados em anais de congressos, '.decode("utf8")
        if self.grupo.obterParametro('grafo-incluir_resumo_expandido_em_congresso'):
            lista += 'Resumos expandidos publicados em anais de congressos, '.decode("utf8")
        if self.grupo.obterParametro('grafo-incluir_resumo_em_congresso'):
            lista += 'Resumos publicados em anais de congressos, '.decode("utf8")
        if self.grupo.obterParametro('grafo-incluir_artigo_aceito_para_publicacao'):
            lista += 'Artigos aceitos para publicação, '.decode("utf8")
        if self.grupo.obterParametro('grafo-incluir_apresentacao_de_trabalho'):
            lista += 'Apresentações de trabalho, '.decode("utf8")
        if self.grupo.obterParametro('grafo-incluir_outro_tipo_de_producao_bibliografica'):
            lista += 'Demais tipos de produção bibliográfica, '.decode("utf8")

        lista = lista.strip().strip(",")

        s = self.pagina_top()
        s += '\n<h3>Grafo de colabora&ccedil;&otilde;es</h3> \
        <a href=membros' + self.extensaoPagina + '>' + str(len(self.grupo)) + ' curriculos Lattes</a> foram considerados, \
        gerando os seguintes grafos de colabora&ccedil;&otilde;es encontradas com base nas produ&ccedil;&otilde;es: <i>' + lista + '</i>. <br><p>'.decode(
            "utf8")

        prefix = self.grupo.obterParametro('global-prefixo') + '-' if not self.grupo.obterParametro(
            'global-prefixo') == '' else ''
        # s+='Veja <a href="grafoDeColaboracoesInterativo'+self.extensaoPagina+'?entradaScriptLattes=./'+prefix+'co_authorship_adjacency_matrix.xml">na seguinte página</a> uma versão interativa do grafo de colabora&ccedil;&otilde;es.<br><p><br><p>'.decode("utf8")

        s += '\nClique no nome dentro do vértice para visualizar o currículo Lattes. Para cada nó: o valor entre colchetes indica o número \
        de produ&ccedil;&otilde;es feitas em colabora&ccedil;&atilde;o apenas com os outros membros do próprio grupo. <br>'.decode(
            "utf8")

        if self.grupo.obterParametro('grafo-considerar_rotulos_dos_membros_do_grupo'):
            s += 'As cores representam os seguintes rótulos: '.decode("utf8")
            for i in range(0, len(self.grupo.listaDeRotulos)):
                rot = self.grupo.listaDeRotulos[i].decode("utf8", "ignore")
                cor = self.grupo.listaDeRotulosCores[i].decode("utf8")
                if rot == '':
                    rot = '[Sem rótulo]'.decode("utf8")
                s += '<span style="background-color:' + cor + '">&nbsp;&nbsp;&nbsp;&nbsp;</span>' + rot + ' '
        s += '\
        <ul> \
        <li><b>Grafo de colabora&ccedil;&otilde;es sem pesos</b><br> \
            <img src=grafoDeColaboracoesSemPesos.png border=1 ISMAP USEMAP="#grafo1"> <br><p> \
        <li><b>Grafo de colabora&ccedil;&otilde;es com pesos</b><br> \
            <img src=grafoDeColaboracoesComPesos.png border=1 ISMAP USEMAP="#grafo2"> <br><p> \
        <li><b>Grafo de colabora&ccedil;&otilde;es com pesos normalizados</b><br> \
            <img src=grafoDeColaboracoesNormalizado.png border=1 ISMAP USEMAP="#grafo3"> \
        </ul>'.decode("utf8")

        cmapx1 = self.grupo.grafosDeColaboracoes.grafoDeCoAutoriaSemPesosCMAPX
        cmapx2 = self.grupo.grafosDeColaboracoes.grafoDeCoAutoriaComPesosCMAPX
        cmapx3 = self.grupo.grafosDeColaboracoes.grafoDeCoAutoriaNormalizadoCMAPX
        s += '<map id="grafo1" name="grafo1">' + cmapx1.decode("utf8") + '\n</map>\n'
        s += '<map id="grafo2" name="grafo2">' + cmapx2.decode("utf8") + '\n</map>\n'
        s += '<map id="grafo3" name="grafo3">' + cmapx3.decode("utf8") + '\n</map>\n'

        if self.grupo.obterParametro('grafo-incluir_grau_de_colaboracao'):
            s += '<br><p><h3>Grau de colaboração</h3> \
                O grau de colaboração (<i>Collaboration Rank</i>) é um valor numérico que indica o impacto de um membro no grafo de colaborações.\
                <br>Esta medida é similar ao <i>PageRank</i> para grafos direcionais (com pesos).<br><p>'.decode("utf8")

            ranks, autores, rotulos = zip(
                *sorted(zip(self.grupo.author_rank_vector, self.grupo.nomes, self.grupo.rotulos), reverse=True))

            s += '<table border=1><tr> <td><i><b>Collaboration Rank</b></i></td> <td><b>Membro</b></td> </tr>'
            for i in range(0, len(ranks)):
                s += '<tr><td>' + str(round(ranks[i], 2)) + '</td><td>' + autores[i] + '</td></tr>'
            s += '</table> <br><p>'

            if self.grupo.obterParametro('grafo-considerar_rotulos_dos_membros_do_grupo'):
                for i in range(0, len(self.grupo.listaDeRotulos)):
                    somaAuthorRank = 0

                    rot = self.grupo.listaDeRotulos[i].decode("utf8", "ignore")
                    cor = self.grupo.listaDeRotulosCores[i].decode("utf8")
                    s += '<b><span style="background-color:' + cor + '">&nbsp;&nbsp;&nbsp;&nbsp;</span>' + rot + '</b><br>'

                    s += '<table border=1><tr> <td><i><b>AuthorRank</b></i></td> <td><b>Membro</b></td> </tr>'
                    for i in range(0, len(ranks)):
                        if rotulos[i] == rot:
                            s += '<tr><td>' + str(round(ranks[i], 2)) + '</td><td>' + autores[i] + '</td></tr>'
                            somaAuthorRank += ranks[i]
                    s += '</table> <br> Total: ' + str(round(somaAuthorRank, 2)) + '<br><p>'

        s += self.paginaBottom()
        self.salvarPagina("grafoDeColaboracoes" + self.extensaoPagina, s)

        # grafo interativo
        s = self.pagina_top()
        s += '<applet code=MyGraph.class width=1280 height=800 archive="http://www.vision.ime.usp.br/creativision/graphview/graphview.jar,http://www.vision.ime.usp.br/creativision/graphview/prefuse.jar"></applet></body></html>'
        s += self.paginaBottom()
        self.salvarPagina("grafoDeColaboracoesInterativo" + self.extensaoPagina, s)

    @staticmethod
    def producao_qualis(elemento, membro):
        raise Exception("Método parece não ser mais utilizado.")
        tabela_template = u"<table style=\"width: 100%; display: block; overflow-x: auto;\"><tbody>" \
                          u"<br><span style=\"font-size:14px;\"><b>Totais de publicações com Qualis:</b></span><br><br>" \
                          u"<div style=\"width:100%; overflow-x:scroll;\">{body}</div>" \
                          u"</tbody></table>"

        first_column_template = u'<div style="float:left; width:200px; height: auto; border: 1px solid black; border-collapse: collapse; margin-left:0px; margin-top:0px;' \
                                ' background:#CCC; vertical-align: middle; padding: 4px 0; {extra_style}"><b>{header}</b></div>'
        header_template = u'<div style="float:left; width:{width}px; height: auto; border-style: solid; border-color: black; border-width: 1 1 1 0; border-collapse: collapse; margin-left:0px; margin-top:0px;' \
                          ' background:#CCC; text-align: center; vertical-align: middle; padding: 4px 0;"><b>{header}</b></div>'
        line_template = u'<div style="float:left; width:{width}px; height: auto; border-style: solid; border-color: black; border-width: 1 1 1 0; border-collapse: collapse; margin-left:0px; margin-top:0px;' \
                        ' background:#EAEAEA; text-align: center; vertical-align: middle; padding: 4px 0;">{value}</div>'  # padding:4px 6px;

        cell_size = 40
        num_estratos = len(membro.tabela_qualis['estrato'].unique())

        header_ano = first_column_template.format(header='Ano', extra_style='text-align: center;')
        header_estrato = first_column_template.format(header=u'Área \\ Estrato', extra_style='text-align: center;')

        for ano in sorted(membro.tabela_qualis['ano'].unique()):
            header_ano += header_template.format(header=ano, width=num_estratos * (cell_size + 1) - 1)
            for estrato in sorted(membro.tabela_qualis['estrato'].unique()):
                header_estrato += header_template.format(header=estrato, width=cell_size)

        if membro.tabela_qualis and not membro.tabela_qualis.empty():
            pt = membro.tabela_qualis.pivot_table(columns=['area', 'ano', 'estrato'], values='freq')
        lines = ''
        for area in sorted(membro.tabela_qualis['area'].unique()):
            lines += first_column_template.format(header=area, extra_style='')
            for ano in sorted(membro.tabela_qualis['ano'].unique()):
                for estrato in sorted(membro.tabela_qualis['estrato'].unique()):
                    try:
                        lines += line_template.format(value=pt.ix[area, ano, estrato], width=cell_size)
                    except IndexingError:
                        lines += line_template.format(value='&nbsp;', width=cell_size)
            lines += '<div style="clear:both"></div>'

        tabela_body = header_ano
        tabela_body += '<div style="clear:both"></div>'
        tabela_body += header_estrato
        tabela_body += '<div style="clear:both"></div>'
        tabela_body += lines

        tabela = tabela_template.format(body=tabela_body)

        # first = True
        # # FIXME: considerar as áreas
        # for ano in sorted(membro.tabela_qualis['ano'].unique()):
        #     if first:
        #         first = False
        #         display = "block"
        #     else:
        #         display = "none"
        #
        #     # esquerda = '<a class="ano_esquerda" rel="{ano}" rev="{rev}" style="cursor:pointer; padding:2px; border:1px solid #C3FDB8;">«</a>'.format(
        #     #     ano=ano, rev=str(elemento))
        #     # direita = '<a class="ano_direita" rel="{ano}" rev="{rev}" style="cursor:pointer; padding:2px; border:1px solid #C3FDB8;">«</a>'.format(
        #     #     ano=ano, rev=str(elemento))
        #     # tabela += '<div id="ano_{ano}_{elemento}" style="display: {display}">{esquerda}<b>{ano}</b>{direita}<br/><br/>'.format(
        #     #           ano=ano, elemento=elemento, display=display, esquerda=esquerda, direita=direita)
        #     chaves = ''
        #     valores = ''
        #
        #     for tipo, frequencia in membro.tabelaQualisDosAnos[ano].items():
        #         # FIXME: terminar de refatorar
        #         if tipo == "Qualis nao identificado":
        #             tipo = '<span title="Qualis nao identificado">QNI</span>'
        #
        #         chaves += '<div style="float:left; width:70px; border:1px solid #000; margin-left:-1px; margin-top:-1px; background:#CCC; padding:4px 6px;"><b>' + str(
        #             tipo) + '</b></div>'
        #         valores += '<div style="float:left; width:70px; border:1px solid #000; margin-left:-1px; margin-top:-1px; background:#EAEAEA; padding:4px 6px;">' + str(
        #             frequencia) + '</div>'
        #
        #     tabela += '<div>' + chaves + '</div>'
        #     tabela += '<div style="clear:both"></div>'
        #     tabela += '<div>' + valores + '</div>'
        #     tabela += '<div style="clear:both"></div>'
        #     tabela += "<br><br></div>"
        # tabTipo += '<div>'
        # chaves = ''
        # valores = ''
        # for chave, valor in membro.tabelaQualisDosTipos.items():
        #
        #     if (chave == "Qualis nao identificado"):
        #         chave = "QNI"
        #
        #     chaves += '<div style="float:left; width:70px; border:1px solid #000; margin-left:-1px; margin-top:-1px; background:#CCC; padding:4px 6px;"><b>' + str(
        #         chave) + '</b></div>'
        #     valores += '<div style="float:left; width:70px; border:1px solid #000; margin-left:-1px; margin-top:-1px; background:#EAEAEA; padding:4px 6px;">' + str(
        #         valor) + '</div>'
        # tabTipo += '<div>' + chaves + '</div>'
        # tabTipo += '<div style="clear:both"></div>'
        # tabTipo += '<div>' + valores + '</div>'
        # tabTipo += '<div style="clear:both"></div>'
        # tabTipo += "<br><br></div><br><br>"
        return tabela

    @staticmethod
    def producao_qualis_por_membro(lista_de_membros):
        # FIXME: ver um local melhor para este método

        producao_por_membro = pandas.DataFrame(columns=list(membro.Membro.tabela_qualis.columns) + ['membro'])

        for m in lista_de_membros:
            nome_membro = unicodedata.normalize('NFKD', m.nomeCompleto).encode('ASCII', 'ignore')
            df = pandas.DataFrame({'membro': [nome_membro] * len(m.tabela_qualis)}, index=m.tabela_qualis.index)
            producao_por_membro = producao_por_membro.append(m.tabela_qualis.join(df), ignore_index=True)

        if producao_por_membro.empty:
            producao_por_membro_pivo = pandas.DataFrame()
        else:
            producao_por_membro_pivo = producao_por_membro.pivot_table(values='freq',
                                                                       columns=['ano', 'estrato'],
                                                                       index=['area', 'membro'],
                                                                       dropna=True, fill_value=0, margins=False,
                                                                       aggfunc=sum)
        return producao_por_membro_pivo

    def gerar_pagina_de_producao_qualificado_por_membro(self):
        html = self.pagina_top()
        html += u'<h3>Produção qualificado por área e membro</h3>'
        table_template = u'<table id="producao_por_membro" class="display nowrap">' \
                         u'  <thead>{head}</thead>' \
                         u'  <tfoot>{foot}</tfoot>' \
                         u'  <tbody>{body}</tbody>' \
                         u'</table>'
        table_line_template = u'<tr>{line}</tr>'

        first_column_template = u'<td style="{extra_style}">{header}</td>'
        header_template = u'<th colspan="{colspan}" {extra_pars}>{header}</th>'
        cell_template = u'<td class="dt-body-center">{value}</td>'
        # first_column_template = u'<td style="border: 1px solid black; border-collapse: collapse; background:#CCC;' \
        #                         u'vertical-align: middle; padding: 4px 0; {extra_style}">{header}</td>'
        # header_template = u'<th colspan="{colspan}" style="border-style: solid; border-color: black;' \
        #                   u'border-width: 1 1 1 0; border-collapse: collapse; margin-left:0px; margin-top:0px;' \
        #                   u'background:#CCC; text-align: center; vertical-align: middle; padding: 4px 0;">{header}</th>'
        # cell_template = u'<td style="border-style: solid; border-color: black;' \
        #                 u'border-width: 1 1 1 0; border-collapse: collapse; margin-left:0px; margin-top:0px;' \
        #                 u'background:#EAEAEA; text-align: center; vertical-align: middle; padding: 4px 0;">{value}</td>'

        header_area = header_template.format(header=u'Área', colspan=1, extra_pars='rowspan="2"')
        # header_membro = header_template.format(header=u'Membro', colspan=1)
        header_anos = header_template.format(header='Ano', colspan=1, extra_pars='')
        header_estratos = header_template.format(header=u'Membro \\ Estrato', colspan=1, extra_pars='')

        footer = u'<th>Área</th><th>Membro</th>'

        producao_por_membro = self.producao_qualis_por_membro(self.grupo.members_list.values())

        if producao_por_membro.empty:
            html += self.paginaBottom()
            self.salvarPagina("producao_membros" + self.extensaoPagina, html)
            return

        anos = sorted(producao_por_membro.columns.get_level_values('ano').unique())
        estratos = sorted(producao_por_membro.columns.get_level_values('estrato').unique())

        for ano in anos:
            header_anos += header_template.format(header=int(ano), colspan=len(estratos), extra_pars='')
            for estrato in estratos:
                header_estratos += header_template.format(header=estrato, colspan=1, extra_pars='')
                footer += '<th style="display: ;"></th>'

        first_row_header = table_line_template.format(line=header_area + header_anos)
        second_row_header = table_line_template.format(line=header_estratos)
        # header = header_area + header_membro + header_estratos
        table_header = first_row_header + second_row_header

        table_footer = table_line_template.format(line=footer)

        areas = sorted(producao_por_membro.index.get_level_values('area').unique())
        membros = sorted(producao_por_membro.index.get_level_values('membro').unique())

        lines = u''
        for area in areas:
            line_area = first_column_template.format(header=area, extra_style='')
            for membro in membros:
                line = line_area
                line += cell_template.format(value=membro)
                for ano in anos:
                    for estrato in estratos:
                        try:
                            freq = producao_por_membro.ix[area, membro][ano, estrato]
                            line += cell_template.format(value=freq if freq else '&nbsp;')  # não mostrar zeros ou nulos
                        except KeyError:
                            line += cell_template.format(value='&nbsp;')
                lines += table_line_template.format(line=line)

        table = table_template.format(head=table_header, body=lines, foot=table_footer)

        html += table

        html += '''<script>
                  $(document).ready( function () {
                      var lastIdx = null;
                      var table = $("#producao_por_membro").DataTable({
                          "dom": 'C<"clear">lfrtip',
                          scrollX: true,
                          //scrollY: "400px",
                          //scrollCollapse: true,
                          paging: true,
                          stateSave: true,
                          initComplete: function () {
                              var api = this.api();
                              api.columns().indexes().flatten().each( function ( i ) {
                                  var column = api.column( i );
                                  var select = $('<select><option value=""></option></select>')
                                      .appendTo( $(column.footer()).empty() )
                                      .on( 'change', function () {
                                          var val = $.fn.dataTable.util.escapeRegex(
                                              $(this).val()
                                          );
                                          console.log(val);
                                          column
                                              .search( val ? '^'+val+'$' : '', true, false )
                                              .draw();
                                      } );
                                  column.data().unique().sort().each( function ( d, j ) {
                                      select.append( '<option value="'+d+'">'+d+'</option>' )
                                  } );
                              } );
                          },
                      });
                      $('#producao_por_membro tbody')
                              .on( 'mouseover', 'td', function () {
                                  var colIdx = table.cell(this).index().column;
                                  if ( colIdx !== lastIdx ) {
                                        $( table.cells().nodes() ).removeClass( 'highlight' );
                                        $( table.column( colIdx ).nodes() ).addClass( 'highlight' );
                                  }
                              } )
                              .on( 'mouseleave', function () {
                                  $( table.cells().nodes() ).removeClass( 'highlight' );
                              } );
                  });
                </script>'''
        # '      .rowGrouping({' \
        # '        iGroupingColumnIndex: 1,' \
        # '        sGroupingColumnSortDirection: "asc",' \
        # '        bExpandableGrouping: true,' \
        # '        bExpandSingleGroup: true,' \
        # '        });' \

        # Salvar em planilha
        xls_filename = os.path.join(self.dir, 'producao_membros.xls')
        producao_por_membro.to_excel(os.path.abspath(xls_filename))
        html += '<a href="{}">{}</a>'.format(os.path.abspath(xls_filename), 'Baixar planilha com os dados')

        html += self.paginaBottom()
        self.salvarPagina("producao_membros" + self.extensaoPagina, html)

    def pagina_top(self, cabecalho=''):
        raise Exception("Método inutilizado")
        nome_grupo = self.grupo.obterParametro('global-nome_do_grupo').decode("utf8")

        s = self.html1
        template = u'<head>' \
                   '<meta http-equiv="Content-Type" content="text/html; charset=utf8">' \
                   '<meta name="Generator" content="scriptLattes">' \
                   '<title>{nome_grupo}</title>' \
                   '<link rel="stylesheet" href="css/scriptLattes.css" type="text/css">' \
                   '<link rel="stylesheet" type="text/css" href="css/jquery.dataTables.css">' \
                   '<link rel="stylesheet" type="text/css" href="css/dataTables.colVis.min.css">' \
                   '<script type="text/javascript" charset="utf8" src="js/jquery.min.js"></script>' \
                   '<script type="text/javascript" charset="utf8" src="js/jquery.dataTables.min.js"></script>' \
                   '<script type="text/javascript" charset="utf8" src="js/dataTables.colVis.min.js"></script>' \
                   '{cabecalho}' \
                   '</head>' \
                   '<body><div id="header2"> <button onClick="history.go(-1)">Voltar</button>' \
                   '<h2>{nome_grupo}</h2></div>'
        # '<script type="text/javascript" charset="utf8" src="jquery.dataTables.rowGrouping.js"></script>' \
        s += template.format(nome_grupo=nome_grupo, cabecalho=cabecalho)
        return s

    def paginaBottom(self):
        raise "método inutilizado"

    def salvarPagina(self, nome, conteudo):
        raise "método inutilizado"
        file = open(os.path.join(self.dir, nome), 'w')
        file.write(conteudo.encode('utf8', 'replace'))
        file.close()

    def salvarPublicacaoEmFormatoRIS(self, pub):
        self.arquivoRis.write(pub.ris().encode('utf8'))

    def formatarTotaisQualis(self, qtd):
        """
        st = '(<b>A1</b>: '+str(qtd['A1'])+', <b>A2</b>: '+str(qtd['A2'])+', <b>B1</b>: '+str(qtd['B1'])+', <b>B2</b>: '+str(qtd['B2'])
        st+= ', <b>B3</b>: '+str(qtd['B3'])+', <b>B4</b>: '+str(qtd['B4'])+', <b>B5</b>: '+str(qtd['B5'])+', <b>C</b>: '+str(qtd['C'])
        st+= ', <b>Qualis n&atilde;o identificado</b>: '+str(qtd['Qualis nao identificado'])+')'
        st+= '<br><p><b>Legenda Qualis:</b><ul>'
        st+= '<li> Publica&ccedil;&atilde;o para a qual o nome exato do Qualis foi identificado: <font color="#336600"><b>Qualis &lt;estrato&gt;</b></font>'
        st+= '<li> Publica&ccedil;&atilde;o para a qual um nome similar (n&atilde;o exato) do Qualis foi identificado: <font color="#FF9933"><b>Qualis &lt;estrato&gt;</b></font> (nome similar)'
        st+= '<li> Publica&ccedil;&atilde;o para a qual nenhum nome do Qualis foi identificado: <font color="#8B0000"><b>Qualis n&atilde;o identificado</b></font> (nome usado na busca)'
        st+= '</ul>'
        return st
        """
        return 'Sem totais qualis ainda...'


def menuHTMLdeBuscaPB(titulo):
    raise "deprecated"
    # titulo = re.sub('\s+', '+', titulo)
    #
    # s = '<br>\
    #      <font size=-1> \
    #      [ <a href="http://scholar.google.com/scholar?hl=en&lr=&q=' + titulo + '&btnG=Search">cita&ccedil;&otilde;es Google Scholar</a> | \
    #        <a href="http://academic.research.microsoft.com/Search?query=' + titulo + '">cita&ccedil;&otilde;es Microsoft Acad&ecirc;mico</a> | \
    #        <a href="http://www.google.com/search?btnG=Google+Search&q=' + titulo + '">busca Google</a> ] \
    #      </font><br>'
    # return s


def menuHTMLdeBuscaPT(titulo):
    titulo = re.sub('\s+', '+', titulo)

    s = '<br>\
         <font size=-1> \
         [ <a href="http://www.google.com/search?btnG=Google+Search&q=' + titulo + '">busca Google</a> | \
           <a href="http://www.bing.com/search?q=' + titulo + '">busca Bing</a> ] \
         </font><br>'
    return s


def menuHTMLdeBuscaPA(titulo):
    titulo = re.sub('\s+', '+', titulo)

    s = '<br>\
         <font size=-1> \
         [ <a href="http://www.google.com/search?btnG=Google+Search&q=' + titulo + '">busca Google</a> | \
           <a href="http://www.bing.com/search?q=' + titulo + '">busca Bing</a> ] \
         </font><br>'
    return s
