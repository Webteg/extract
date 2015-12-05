# encoding: utf-8
import logging

import pandas as pd

from data_tables.bibliographical_production.papers import Papers
from util.util import similaridade_entre_cadeias

logger = logging.getLogger(__name__)


class Others(Papers):
    columns = ['id_membro',
               'autores',
               'titulo',
               'ano',
               'relevante',
               'natureza',  # tipo de apresentacao
               ]

    def __init__(self, id, initial_data_frame=None, group_similar=False):
        super().__init__(group_similar=group_similar)
        self.id = id
        self.data_frame = pd.DataFrame(columns=self.columns)
        if initial_data_frame is not None:
            self.data_frame = self.data_frame.append(initial_data_frame, ignore_index=True)

    def add_from_parser(self, productions_list):
        """
        Add a list of productions extracted by a parser.
        :param productions_list: list of productions
        :return:
        """
        assert self.adjacency_matrix is None
        presentations = []
        for production in productions_list:
            presentations.append([getattr(production, attribute, None) for attribute in self.columns])
        df = pd.DataFrame(presentations, columns=self.columns)
        df['id_membro'] = self.id
        self.data_frame = self.data_frame.append(df, ignore_index=True)
        if self.group_similar:
            self.mark_similar()

    def append(self, productions):
        assert isinstance(productions, type(self))
        assert self.adjacency_matrix is None
        self.data_frame = self.data_frame.append(productions.data_frame, ignore_index=True)
        if self.group_similar:
            self.mark_similar()

    def is_similar(self, row1, row2):
        # TODO: testar outras similaridades (autores, issn, etc.)
        # TODO: ver se é preciso ignorar quando id_membro é o mesmo
        if similaridade_entre_cadeias(row1['titulo'], row2['titulo']) and row1.natureza == row2.natureza:
            return True
        return False

    # @property
    # def all(self):
    #     return Others(self.id, initial_data_frame=self.data_frame)
