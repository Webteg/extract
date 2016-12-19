# encoding: utf-8
import logging

import pandas as pd

from data_tables.bibliographical_production.basic_production import BasicProduction
from util.util import similaridade_entre_cadeias

logger = logging.getLogger(__name__)


class JournalPapers(BasicProduction):
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
               'autores',
               'only_accepted']

    def add_from_parser(self, papers_list, only_accepted=False):
        """
        Add a list of papers extracted by a parser.
        :param papers_list:
        :param only_accepted: whether the papers in the list are only accepted for publication and not yet published
        :return:
        """
        super(JournalPapers, self).add_from_parser(papers_list, only_accepted=only_accepted)
        # papers_df = self._df_from_parser(papers_list)
        # papers_df['id_membro'] = self.id
        # papers_df['only_accepted'] = only_accepted
        # self.data_frame = self.data_frame.append(papers_df, ignore_index=True)

    def is_similar(self, row1, row2):
        # TODO: testar outras similaridades (autores, issn, etc.)
        # TODO: ver se é preciso ignorar quando id_membro é o mesmo
        if similaridade_entre_cadeias(row1['titulo'], row2['titulo']) and row1.only_accepted == row2.only_accepted:
            return True
        return False

    @property
    def published(self):
        """
        By default, return only published papers (i.e., ignore only accepted papers).
        :return: data frame with only_accepted papers filtered out
        """
        return JournalPapers(self.id, initial_data_frame=self.data_frame[self.data_frame['only_accepted'] == False], group_similar=self.group_similar)

    @property
    def only_accepted(self):
        return JournalPapers(self.id, initial_data_frame=self.data_frame[self.data_frame['only_accepted'] == True], group_similar=self.group_similar)

