# -*- coding: utf-8 -*-

from abc import abstractmethod, ABCMeta
from collections import OrderedDict

import numpy
import pandas as pd
from theano.tensor.subtensor import as_index_variable

from data_tables.util import create_adjacency_matrix, create_weighted_matrix


class Papers:
    __metaclass__ = ABCMeta

    columns = ['id_membro']
    mapping_attributes = {}

    # id = None
    data_frame = pd.DataFrame()
    adjacency_matrix = None
    weighted_matrix = None

    def __init__(self, group_similar=False, since_year=None, until_year=None):
        self.group_similar = group_similar
        self.since_year = since_year
        self.until_year = until_year

    def add_from_parser(self, productions_list, **kwargs):
        """
        Add a list of productions extracted by a parser.
        :param productions_list: list of productions to add
        :param kwargs: extra columns to set a fixed value (key: value -> df[key] = value)
        :return:
        """
        assert self.adjacency_matrix is None
        productions_df = self._df_from_parser(productions_list)
        productions_df['id_membro'] = self.id
        for key, value in kwargs.items():
            productions_df[key] = value
        self.append(productions_df)

    def _df_from_parser(self, productions_list):
        productions = {}
        for column in self.columns:
            attribute = column
            if column in self.mapping_attributes:
                attribute = self.mapping_attributes[column]
            productions[column] = [getattr(production, attribute, None) for production in productions_list]
        # df = pd.DataFrame(productions, columns=self.columns)
        productions_df = pd.DataFrame(productions)
        return productions_df

    def append(self, productions):
        assert self.adjacency_matrix is None
        assert isinstance(productions, type(self)) or isinstance(productions, pd.DataFrame)
        if isinstance(productions, type(self)):
            # self.data_frame = self.data_frame.append(productions.data_frame, ignore_index=True)
            data_frame_to_append = productions.data_frame
        # elif isinstance(productions, pd.DataFrame):
        else:
            # self.data_frame = self.data_frame.append(productions, ignore_index=True)
            data_frame_to_append = productions

        # Filter by timespan
        if self.since_year:
            if isinstance(self.since_year, list):  # So this is an specific timespan (defined in the list, not the config)
                pass
            else:
                pass

        # Deal with duplicated entries
        if self.group_similar:
            duplicated = []
            for i, row in data_frame_to_append.iterrows():
                similar = self.data_frame.apply(lambda x: self.is_similar(x, row), axis=1)
                if similar.any().any():  # double any's because on empty similar any returns bool by column
                    duplicated.append(i)
                    self.data_frame.ix[similar, 'id_membro'] = self.data_frame.ix[similar, 'id_membro'].apply(lambda x: x | frozenset({row.id_membro}))
            data_frame_to_append['id_membro'] = data_frame_to_append['id_membro'].apply(lambda x: frozenset({x}))
            self.data_frame = self.data_frame.append(data_frame_to_append[~data_frame_to_append.index.isin(duplicated)], ignore_index=True)
        else:
            self.data_frame = self.data_frame.append(data_frame_to_append, ignore_index=True)

    @abstractmethod
    def is_similar(self, row1, row2):
        pass

    def mark_similar(self):
        self.data_frame['similar'] = self.data_frame.index

        def set_similar(row, ref_row, ref_index):
            if self.is_similar(row, ref_row):
                row.similar = ref_index
            return row

        # Might be better to search for similarity in append (though it'd remain O(n^2))
        for i in self.data_frame.index:
            # self.data_frame.ix[:i-1][self.data_frame.ix[:i-1].apply(lambda x: self.is_similar(x, self.data_frame.ix[i]), axis=1)]
            self.data_frame = self.data_frame.apply(set_similar, axis=1, ref_row=self.data_frame.ix[i], ref_index=i)

    def _get_similar_groups(self):
        if 'similar' not in self.data_frame.columns:
            self.mark_similar()
        grouped = self.data_frame.groupby('similar', as_index=False)
        # grouped.aggregate({'id_membro': lambda x: frozenset(x)})
        # grouped.aggregate(list)
        return grouped

    def _co_authors_list(self):
        # Code below is deprecated; was working when we were using a 'similar' column instead of a frozenset in 'id_membro'
        # grouped = self._get_similar_groups()
        # # self.grouped.filter(lambda x: len(x) > 1)
        # co_authorships = [group for group in grouped.groups.values() if len(group) > 1]
        # co_authors = [list(self.data_frame['id_membro'][co_authors_indexes]) for co_authors_indexes in co_authorships]

        co_authors = list(self.data_frame.ix[self.data_frame['id_membro'].apply(len) > 1, 'id_membro'])
        # FIXME: test method (enable collaboration graph)
        return co_authors

    def co_authorship_adjacency_matrix(self, members_indices):
        if self.adjacency_matrix is None:
            self.adjacency_matrix = create_adjacency_matrix(members_indices, self._co_authors_list())
        return self.adjacency_matrix

    def co_authorship_weighted_matrix(self, members_indices):
        if self.weighted_matrix is None:
            self.weighted_matrix = create_weighted_matrix(members_indices, self._co_authors_list())
        return self.weighted_matrix

    def __len__(self):
        return len(self.data_frame)

    def pivoted_by(self, column, ascending=True):
        return pd.pivot_table(self.data_frame, index=column).sort_index(ascending=ascending)

    def ordered_dict_by(self, key_by, ascending=True):
        group_dict = {
            key: self.data_frame[self.data_frame[key_by] == key] for key in self.data_frame[key_by].unique()
            }
        return OrderedDict(sorted(group_dict.items(), key=lambda t: t[0], reverse=not ascending))

    def filter_by_year(self):
        if not objeto.ano:  # se nao for identificado o ano sempre o mostramos na lista
            objeto.ano = 0
            return 1
        else:
            objeto.ano = int(objeto.ano)
            if objeto.ano < self.items_desde_ano or objeto.ano > self.items_ate_ano:
                return 0
            else:
                retorno = 0
                for per in self.member_timespans:
                    if per[0] <= objeto.ano <= per[1]:
                        retorno = 1
                        break
                return retorno
