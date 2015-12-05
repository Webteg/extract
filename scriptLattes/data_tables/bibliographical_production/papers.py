# -*- coding: utf-8 -*-

from abc import abstractmethod, ABCMeta
from collections import OrderedDict
import pandas as pd
from data_tables.util import create_adjacency_matrix, create_weighted_matrix


class Papers:
    __metaclass__ = ABCMeta

    data_frame = pd.DataFrame()
    adjacency_matrix = None
    weighted_matrix = None

    def __init__(self, group_similar=False):
        self.group_similar = group_similar

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

    def get_similar_groups(self):
        if 'similar' not in self.data_frame.columns:
            self.mark_similar()
        grouped = self.data_frame.groupby('similar')
        # grouped.aggregate({'id_membro': lambda x: frozenset(x)})
        # grouped.aggregate(list)
        return grouped

    def co_authors_list(self):
        grouped = self.get_similar_groups()
        # self.grouped.filter(lambda x: len(x) > 1)
        co_authorships = [group for group in grouped.groups.values() if len(group) > 1]
        co_authors = [list(self.data_frame['id_membro'][co_authors_indexes]) for co_authors_indexes in co_authorships]
        return co_authors

    def co_authorship_adjacency_matrix(self, members_indices):
        if self.adjacency_matrix is None:
            self.adjacency_matrix = create_adjacency_matrix(members_indices, self.co_authors_list())
        return self.adjacency_matrix

    def co_authorship_weighted_matrix(self, members_indices):
        if self.weighted_matrix is None:
            self.weighted_matrix = create_weighted_matrix(members_indices, self.co_authors_list())
        return self.weighted_matrix

    def __len__(self):
        if self.group_similar:
            return len(self.get_similar_groups())
        return len(self.data_frame)

    def pivoted_by(self, column, ascending=True):
        return pd.pivot_table(self.data_frame, index=column).sort_index(ascending=ascending)

    def ordered_dict_by(self, key_by, ascending=True):
        if 'similar' not in self.data_frame.columns:
            self.mark_similar()

        if self.group_similar:
            # ignore rows marked as similar to another
            group_dict = {
                key: self.data_frame[(self.data_frame[key_by] == key) & (self.data_frame['similar'] == self.data_frame.index)] for key in self.data_frame[key_by].unique()
                }
        else:
            group_dict = {
                key: self.data_frame[self.data_frame[key_by] == key] for key in self.data_frame[key_by].unique()
                }
        return OrderedDict(sorted(group_dict.items(), key=lambda t: t[0], reverse=not ascending))
