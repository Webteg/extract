# encoding: utf-8
import logging

import pandas as pd

from data_tables.bibliographical_production.basic_production import BasicProduction
from util.util import similaridade_entre_cadeias

logger = logging.getLogger(__name__)


class EventPapers(BasicProduction):
    mapping_attributes = {'evento': 'nomeDoEvento'}  # TODO: deve desaparecer quando parser for refatorado

    class Types:
        complete = 'completo'
        abstract = 'resumo'
        expanded_abstract = 'resumo expandido'

    columns = ['id_membro',
               'titulo',
               'autores',
               'ano',
               'doi',
               'relevante',
               'evento',
               'isbn',
               'volume',
               'paginas',
               'type',  # completo, resumo, resumo_expandido
               'qualis']

    # def add_from_parser(self, papers_list, type):
    #     papers_df = self._df_from_parser(papers_list)
    #     papers_df['id_membro'] = self.id
    #     papers_df['type'] = type
    #     self.data_frame = self.data_frame.append(papers_df, ignore_index=True)
    #     # if self.group_similar:
    #     #     self.mark_similar()

    @staticmethod
    def is_similar(row1, row2):
        # TODO: testar outras similaridades (autores, issn, etc.)
        if similaridade_entre_cadeias(row1['titulo'], row2['titulo']) and row1.type == row2.type and row1.ano == row2.ano:
            return True
        return False

    @property
    def complete(self):
        return EventPapers(self.id, self.data_frame[self.data_frame['type'] == self.Types.complete], group_similar=self.group_similar)

    @property
    def abstract(self):
        return EventPapers(self.id, self.data_frame[self.data_frame['type'] == self.Types.abstract], group_similar=self.group_similar)

    @property
    def expanded_abstract(self):
        return EventPapers(self.id, self.data_frame[self.data_frame['type'] == self.Types.expanded_abstract], group_similar=self.group_similar)
