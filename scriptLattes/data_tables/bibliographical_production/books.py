# encoding: utf-8
import logging

import pandas as pd

from data_tables.bibliographical_production.basic_production import BasicProduction
from util.util import similaridade_entre_cadeias

logger = logging.getLogger(__name__)


class Books(BasicProduction):
    columns = ['id_membro',
               'autores',
               'titulo',
               'livro',  # for chapters
               'relevante',
               'ano',
               'volume',
               'paginas',
               'edicao',
               'editora',
               'isbn',
               'only_chapter',
               ]

    # def __init__(self, id, initial_data_frame=None, group_similar=False):
    #     super().__init__(group_similar=group_similar)
    #     self.id = id
    #     self.data_frame = pd.DataFrame(columns=self.columns)
    #     if initial_data_frame is not None:
    #         self.data_frame = self.data_frame.append(initial_data_frame, ignore_index=True)

    def add_from_parser(self, books_list, only_chapter=False):
        """
        Add a list of papers extracted by a parser.
        :param books_list: list of books or chapters
        :param only_chapter: whether the books in the list are only book chapters and not full books
        :return:
        """
        super(Books, self).add_from_parser(books_list, only_chapter=only_chapter)
        # assert self.adjacency_matrix is None
        # books_df = self._df_from_parser(books_list)
        # books_df['id_membro'] = self.id
        # books_df['only_chapter'] = only_chapter
        # self.data_frame = self.data_frame.append(books_df, ignore_index=True)

    def is_similar(self, row1, row2):
        # TODO: testar outras similaridades (autores, issn, etc.)
        # TODO: ver se é preciso ignorar quando id_membro é o mesmo
        if similaridade_entre_cadeias(row1['titulo'], row2['titulo']) and row1.only_chapter == row2.only_chapter:
            return True
        return False

    @property
    def full(self):
        """
        By default, return only published papers (i.e., ignore only accepted papers).
        :return: data frame with only_accepted papers filtered out
        """
        return Books(self.id, initial_data_frame=self.data_frame[self.data_frame['only_chapter'] == False], group_similar=self.group_similar)

    @property
    def only_chapter(self):
        return Books(self.id, initial_data_frame=self.data_frame[self.data_frame['only_chapter'] == True], group_similar=self.group_similar)

