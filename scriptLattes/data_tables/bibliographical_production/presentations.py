# encoding: utf-8
import logging

import pandas as pd

from data_tables.bibliographical_production.basic_production import BasicProduction
from util.util import similaridade_entre_cadeias

logger = logging.getLogger(__name__)


class Presentations(BasicProduction):
    columns = ['id_membro',
               'autores',
               'titulo',
               'ano',
               'relevante',
               'natureza',  # tipo de apresentacao
               ]

    def is_similar(self, row1, row2):
        # TODO: testar outras similaridades (autores, issn, etc.)
        # TODO: ver se é preciso ignorar quando id_membro é o mesmo
        if similaridade_entre_cadeias(row1['titulo'], row2['titulo']) and row1.natureza == row2.natureza:
            return True
        return False

    # @property
    # def all(self):
    #     return Presentations(self.id, initial_data_frame=self.data_frame)
