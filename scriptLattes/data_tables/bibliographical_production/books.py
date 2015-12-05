# encoding: utf-8
import logging

import pandas as pd

from data_tables.bibliographical_production.papers import Papers
from util.util import similaridade_entre_cadeias

logger = logging.getLogger(__name__)


class Books(Papers):
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

    def __init__(self, id, initial_data_frame=None, group_similar=False):
        super().__init__(group_similar=group_similar)
        self.id = id
        self.data_frame = pd.DataFrame(columns=self.columns)
        if initial_data_frame is not None:
            self.data_frame = self.data_frame.append(initial_data_frame, ignore_index=True)

    def add_from_parser(self, books_list, only_chapter=False):
        """
        Add a list of papers extracted by a parser.
        :param books_list: list of books or chapters
        :param only_chapter: whether the books in the list are only book chapters and not full books
        :return:
        """
        assert self.adjacency_matrix is None
        books = []
        for book in books_list:
            books.append([getattr(book, attribute, None) for attribute in self.columns])
        df = pd.DataFrame(books, columns=self.columns)
        df['id_membro'] = self.id
        df['only_chapter'] = only_chapter
        self.data_frame = self.data_frame.append(df, ignore_index=True)
        if self.group_similar:
            self.mark_similar()

    def append(self, books):
        assert isinstance(books, Books)
        assert self.adjacency_matrix is None
        self.data_frame = self.data_frame.append(books.data_frame, ignore_index=True)
        if self.group_similar:
            self.mark_similar()

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

