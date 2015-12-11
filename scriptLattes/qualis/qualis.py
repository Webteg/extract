#!/usr/bin/python
# encoding: utf-8
# filename: qualis.py
#
# scriptLattes V8
# Copyright 2005-2013: Jesús P. Mena-Chalco e Roberto M. Cesar-Jr.
# http://scriptlattes.sourceforge.net/
# Pacote desenvolvido por Helena Caseli
#
# Este programa é um software livre; você pode redistribui-lo e/ou
# modifica-lo dentro dos termos da Licença Pública Geral GNU como
# publicada pela Fundação do Software Livre (FSF); na versão 2 da
# Licença, ou (na sua opinião) qualquer versão.
#
# Este programa é distribuído na esperança que possa ser util,
# mas SEM NENHUMA GARANTIA; sem uma garantia implicita de ADEQUAÇÂO a qualquer
# MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
# Licença Pública Geral GNU para maiores detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa, se não, escreva para a Fundação do Software
# Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
from collections import defaultdict
import logging
import re
import fileinput

import pandas
from configobj import ConfigObj
from pathlib import Path

from data_tables.bibliographical_production.event_papers import EventPapers
from data_tables.bibliographical_production.journal_papers import JournalPapers
from qualis.qualisextractor import QualisExtractor
from scriptLattes.util.util import similaridade_entre_cadeias
from scriptLattes.util.util import find_file
from validate import Validator

logger = logging.getLogger(__name__)


scoring_table_spec = """
# Tabela de pontuação de produçao

[artigos em periódicos]
# 1. ARTIGOS PUBLICADOS EM PERIÓDICOS CIENTÍFICOS com  ISSN.
# Cada artigo será pontuado pelo Qualis OU pelo Fator de Impacto, o que for maior.
    [[qualis]]
        A1 = integer
        A2 = integer
        B1 = integer
        B2 = integer
        B3 = integer
        B4 = integer
        B5 = integer
        C  = integer
        sem qualis = integer

    [[fator de impacto]]
        # Especifique intervalos "x < F.I. <= y" no formato "x, y" (use '_' para -infinito e + infinito)
        3,0 <  _  = integer
        2,5 < 3,0 = integer
        2,0 < 2,5 = integer
        1,6 < 2,0 = integer
        1,2 < 1,6 = integer
        0,8 < 1,2 = integer
        0,5 < 0,8 = integer
         _  < 0,5 = integer

[artigos em eventos]
    A1 = integer
    A2 = integer
    B1 = integer
    B2 = integer
    B3 = integer
    B4 = integer
    B5 = integer
    C = integer
    Sem Qualis = integer
"""

class Qualis:
    # periodicos = {}
    # congressos = {}
    # qtdPB0 = {}  # Total de artigos em periodicos por Qualis
    # qtdPB4 = {}  # Total de trabalhos completos em congressos por Qualis
    # qtdPB5 = {}  # Total de resumos expandidos em congressos por Qualis

    def __init__(self, data_file_path=None,
                 arquivo_qualis_de_periodicos=None,
                 arquivo_areas_qualis=None,
                 arquivo_qualis_de_congressos=None,
                 area_qualis_de_congressos=None,
                 scoring_table_path=None):
        """
        arquivo_qualis_de_congressos: arquivo CSV de qualis de congressos # FIXME: só funciona para uma área
        data_file_path: arquivo cache de qualis extraídos anteriormente; é atualizado ao final da execução
        """
        self.arquivo_qualis_de_periodicos = arquivo_qualis_de_periodicos
        self.arquivo_areas_qualis = arquivo_areas_qualis
        self.arquivo_qualis_de_congressos = arquivo_qualis_de_congressos
        self.area_qualis_de_congressos = area_qualis_de_congressos

        # qualis extractor -> extrai qualis diretamente da busca online do qualis
        self.qextractor = QualisExtractor(data_file_path=data_file_path,
                                          arquivo_qualis_de_periodicos=arquivo_qualis_de_periodicos,
                                          arquivo_areas_qualis=arquivo_areas_qualis,
                                          arquivo_qualis_de_congressos=arquivo_qualis_de_congressos,
                                          area_qualis_de_congressos=area_qualis_de_congressos)

        self.scoring_table = None
        if scoring_table_path:
            self.load_scoring_table(scoring_table_path)

        # self.qextractor.extract_qualis()
        # self.qextractor.save_data(data_file_path)

    def analyse_journal_papers(self, papers):
        assert isinstance(papers, JournalPapers)
        if self.qextractor.journals_qualis_data_frame is None:
            logger.info("Tabela Qualis de periódicos não informada. Ignorando análise.")
            return
        if 'qualis' not in papers.data_frame.columns:
            papers.data_frame['qualis'] = None
        for index, paper in papers.data_frame.iterrows():
            if paper.issn:
                area_estrato_dict = self.qextractor.get_qualis_by_issn(paper.issn)
            else:
                area_estrato_dict = self.qextractor.get_qualis_by_title(paper.revista)
            if area_estrato_dict:
                papers.data_frame.set_value(index, 'qualis', area_estrato_dict)

    def analyse_event_papers(self, papers):
        assert isinstance(papers, EventPapers)
        if self.qextractor.events_qualis_data_frame is None:
            logger.info("Tabela Qualis de congressos não informada. Ignorando análise.")
            return
        if 'qualis' not in papers.data_frame.columns:
            papers.data_frame['qualis'] = None
        for index, paper in papers.data_frame.iterrows():
            area_estrato_dict = self.qextractor.get_qualis_by_event(paper.evento)
            if area_estrato_dict:
                papers.data_frame.ix[index, 'qualis'] = area_estrato_dict

    def load_scoring_table(self, file_path):
        assert isinstance(file_path, Path)
        spec = scoring_table_spec.split("\n")
        config = ConfigObj(infile=str(file_path), configspec=spec, file_error=False)
        validator = Validator()
        res = config.validate(validator, copy=True)
        return config


    def analisar_publicacoes(self, membro):
        raise Exception("Substituído por métodos específicos")
        # Percorrer lista de publicacoes buscando e contabilizando os qualis
        for index, publicacao in membro.journal_papers:
            # qualis, similar = self.buscaQualis('P', pub.revista)
            # pub.qualis = qualis
            if publicacao.issn:
                publicacao.qualis = self.qextractor.get_qualis_by_issn(publicacao.issn)

            # FIXME: utilizaria o comportamento antigo (ler qualis de um CSV), mas nao funciona se a configuracao global-arquivo_qualis_de_periodicos nao for definida
            # agora é usar_cache_qualis = sim
            # elif not self.extrair_qualis_online:
            # qualis, similar = self.buscaQualis('P', pub.revista)
            # pub.qualis = qualis
            # pub.qualissimilar = similar
            else:
                # tentar extrair online pelo titulo
                publicacao.qualis = self.qextractor.get_qualis_by_title(publicacao.revista)
                publicacao.qualis = None
                publicacao.qualissimilar = None

        # FIXME: trecho abaixo precisa ser usado para gerar a tabela de produção qualificada por membro
        agregacao = self.agregar_qualis(membro.journal_papers)
        if agregacao:
            membro.tabela_qualis = pandas.DataFrame(data=agregacao,
                                                    columns=['ano', 'area', 'estrato', 'freq'])
        else:
            membro.tabela_qualis = pandas.DataFrame(columns=['ano', 'area', 'estrato', 'freq'])

        # XXX: pensar em usar pivot_table
        # pd.pivot_table(h, values='freq', index=['area', 'estrato'], columns=['ano'])
        # p = pd.pivot_table(data=df, index='area', columns=['ano', 'estrato'], values='freq')
        # p.fillna(0)

        if self.congressos:
            for pub in membro.listaTrabalhoCompletoEmCongresso:
                qualis, similar = self.busca_qualis_congressos(pub.nomeDoEvento)
                if not qualis:
                    if self.congressos.get(pub.sigla):
                        qualis = self.congressos.get(pub.sigla)  # Retorna Qualis da sigla com nome do evento
                        similar = pub.sigla
                    else:
                        qualis = u"Qualis não identificado"  # FIXME: conferir se não deve ser None (ver na geração de gráfico)
                        similar = pub.nomeDoEvento
                pub.qualis = qualis
                pub.qualissimilar = similar

            for pub in membro.listaResumoExpandidoEmCongresso:
                qualis, similar = self.busca_qualis_congressos(pub.nomeDoEvento)
                pub.qualis = qualis if qualis else u"Qualis não identificado"
                pub.qualissimilar = similar

    def calcular_totais_dos_qualis(self, artigo_em_periodico, trabalho_completo_em_congresso,
                                   resumo_expandido_em_congresso):
        # FIXME: publicacao.qualis tem tipo diferente (dict) do que antes (lista)
        # self.qtdPB0 = self.totais_dos_qualis_por_tipo(artigo_em_periodico)
        self.qtdPB4 = self.totais_dos_qualis_por_tipo(trabalho_completo_em_congresso)
        self.qtdPB5 = self.totais_dos_qualis_por_tipo(resumo_expandido_em_congresso)

    def busca_qualis_periodicos(self, nome):
        # FIXME: não usado; antigo método buscaQualis(tipo, nome)
        dist = 0
        indice = 0
        # Percorrer lista de periodicos tentando casar com nome usando funcao similaridade_entre_cadeias(str1, str2) de scriptLattes.py
        if self.periodicos.get(nome):
            return self.periodicos.get(nome), ''  # Retorna Qualis do nome exato encontrado - Casamento perfeito
        else:
            chaves = self.periodicos.keys()
            for i in range(0, len(chaves)):
                distI = similaridade_entre_cadeias(nome, chaves[i], qualis=True)
                if distI > dist:  # comparamos: nome com cada nome de periodico
                    indice = i
                    dist = distI
            if indice > 0:
                return self.periodicos.get(chaves[indice]), chaves[indice]  # Retorna Qualis de nome similar
        return None, None

    def busca_qualis_congressos(self, nome):
        # Percorrer lista de periodicos tentando casar com nome usando funcao similaridade_entre_cadeias(str1, str2)
        if self.congressos.get(nome):
            return self.congressos.get(nome), ''  # Retorna Qualis do nome exato encontrado - Casamento perfeito
        else:
            similaridade, nome_congresso, qualis = max(
                (similaridade_entre_cadeias(nome, key, qualis=True), key, value) for key, value in
                self.congressos.items())
            if similaridade > 0:
                return qualis, nome_congresso
            return None, nome

    @staticmethod
    def totais_dos_qualis_por_tipo(lista_completa):  # FIXME: remover
        qtd = defaultdict(int)
        for ano, publicacoes in lista_completa.items():
            for publicacao in publicacoes:
                qtd[publicacao.qualis] += 1
        return qtd

    @staticmethod
    def agregar_qualis(publicacoes):
        assert isinstance(publicacoes, JournalPapers)
        ano_area_estrato_freq = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        for index, publicacao in publicacoes:
            if publicacao.qualis:
                for area, estrato in publicacao.qualis.items():
                    ano_area_estrato_freq[publicacao.ano][area][estrato] += 1
        agregacao = []
        for ano, aef in ano_area_estrato_freq.items():
            for area, ef in aef.items():
                for estrato, freq in ef.items():
                    agregacao.append((ano, area, estrato, freq))
        return agregacao


