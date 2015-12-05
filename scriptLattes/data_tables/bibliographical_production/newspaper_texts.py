# encoding: utf-8
import logging

import pandas as pd

from data_tables.bibliographical_production.papers import Papers
from util.util import similaridade_entre_cadeias

logger = logging.getLogger(__name__)


class NewspaperTexts(Papers):
    mapping_attributes = {'jornal': 'nomeJornal'}  # TODO: deve desaparecer quando parser for refatorado

    columns = ['id_membro',
               'autores',
               'titulo',
               'ano',
               'relevante',
               'volume',
               'paginas',
               'jornal',
               'data',
               ]

    def __init__(self, id, initial_data_frame=None, group_similar=False):
        super().__init__(group_similar=group_similar)
        self.id = id
        self.data_frame = pd.DataFrame(columns=self.columns)
        if initial_data_frame is not None:
            self.data_frame = self.data_frame.append(initial_data_frame, ignore_index=True)

    def is_similar(self, row1, row2):
        # TODO: testar outras similaridades (autores, issn, etc.)
        # TODO: ver se é preciso ignorar quando id_membro é o mesmo
        if similaridade_entre_cadeias(row1['titulo'], row2['titulo']):
            return True
        return False

    # @property
    # def all(self):
    #     return NewspaperTexts(self.id, initial_data_frame=self.data_frame)
