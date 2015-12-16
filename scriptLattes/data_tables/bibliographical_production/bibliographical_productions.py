# *-* coding: utf-8 *-*
from collections import OrderedDict, defaultdict
import pandas as pd

__author__ = 'kepler'


class BibliographicalProductions:
    def __init__(self, journal_papers, event_papers, books, newspaper_texts, presentations, others):
        # assert isinstance(journal_papers, pd.DataFrame)
        # assert isinstance(event_papers, pd.DataFrame)

        data = {
            'journal': journal_papers,
            'event': event_papers,
            'book': books,
            'newspaper': newspaper_texts,
            'presentation': presentations,
            'other': others,
        }
        # self.productions = pd.Panel(data)  # XXX: não serve; deixa todos data frames com o mesmo tamanho, cheio de NaNs
        self.productions = data

    def __len__(self):
        return sum(len(production) for production in self.productions.values())

    def ordered_dict_by(self, key_by, ascending=True):
        group_dict = {}
        for production in self.productions.values():
            for key in production.data_frame[key_by].unique():
                if key not in group_dict.keys():
                    group_dict[key] = pd.DataFrame(columns=['autores', 'titulo', 'ano', 'natureza', 'evento', 'revista'])
                group_dict[key] = group_dict[key].append(production.data_frame.ix[production.data_frame[key_by] == key, ['autores', 'titulo', 'ano', 'natureza', 'evento', 'revista']]).fillna('')
        return OrderedDict(sorted(group_dict.items(), key=lambda t: t[0], reverse=not ascending))

    def have_qualis(self):
        return False
