# encoding: utf-8
import logging

import pandas as pd

from data_tables.bibliographical_production.basic_production import BasicProduction
from util.util import similaridade_entre_cadeias

logger = logging.getLogger(__name__)


class NewspaperTexts(BasicProduction):
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

    def is_similar(self, row1, row2):
        # TODO: testar outras similaridades (autores, issn, etc.)
        # TODO: ver se é preciso ignorar quando id_membro é o mesmo
        if similaridade_entre_cadeias(row1['titulo'], row2['titulo']):
            return True
        return False

    # @property
    # def all(self):
    #     return NewspaperTexts(self.id, initial_data_frame=self.data_frame)
