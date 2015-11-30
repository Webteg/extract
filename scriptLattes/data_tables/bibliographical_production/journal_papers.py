# encoding: utf-8
import logging

import pandas as pd

from data_tables.bibliographical_production.papers import Papers
from util.util import similaridade_entre_cadeias

logger = logging.getLogger(__name__)


class JournalPapers(Papers):
    columns = ['id_membro',
               'titulo',
               'ano',
               'doi',
               'relevante',
               'revista',
               'issn',
               'volume',
               'numero',
               'paginas',
               'qualis',
               'autores']

    def __init__(self, id):
        self.id = id
        self.data_frame = pd.DataFrame(columns=self.columns)

    def add_from_parser(self, papers_list):
        assert self.adjacency_matrix is None
        # list of ArtigoEmPeriodico
        papers = []
        for paper in papers_list:
            papers.append([getattr(paper, attribute) for attribute in self.columns[1:]])  # skip id_membro
        papers_df = pd.DataFrame(papers, columns=self.columns[1:])
        papers_df['id_membro'] = self.id
        self.data_frame = self.data_frame.append(papers_df, ignore_index=True)

    def append(self, papers):
        assert isinstance(papers, JournalPapers)
        assert self.adjacency_matrix is None
        self.data_frame = self.data_frame.append(papers.data_frame, ignore_index=True)

    def is_similar(self, row1, row2):
        # TODO: testar outras similaridades (autores, issn, etc.)
        # TODO: ver se é preciso ignorar quando id_membro é o mesmo
        if similaridade_entre_cadeias(row1['titulo'], row2['titulo']):
            return True
        return False
