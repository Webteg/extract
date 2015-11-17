import logging

import pandas as pd

from util.util import similaridade_entre_cadeias

logger = logging.getLogger(__name__)


class EventPapers:
    mapping_attributes = {'evento': 'nomeDoEvento'}  # TODO: deve desaparecer quando parser for refatorado

    class Types:
        complete = 'completo'
        abstract = 'resumo'
        expanded_abstract = 'resumo expandido'

    columns = ['id_membro',
               'titulo',
               'autores',
               'ano',
               'doi',
               'relevante',
               'evento',
               'isbn',
               'volume',
               'paginas',
               'type',  # completo, resumo, resumo_expandido
               'qualis']

    def __init__(self, id):
        self.id = id
        self.data_frame = pd.DataFrame(columns=self.columns)

    def add_from_parser(self, papers_list, papers_type):
        # list of trabalhoEmCongresso
        papers = {}
        for column in self.columns[1:]:  # skip id_membro
            attribute = column
            if column in self.mapping_attributes:
                attribute = self.mapping_attributes[column]
            papers[column] = [getattr(paper, attribute, None) for paper in papers_list]
        papers_df = pd.DataFrame(papers)
        papers_df['id_membro'] = self.id
        papers_df['type'] = papers_type
        self.data_frame = self.data_frame.append(papers_df, ignore_index=True)

    def append(self, papers):
        assert isinstance(papers, EventPapers)
        self.data_frame = self.data_frame.append(papers.data_frame, ignore_index=True)

    @staticmethod
    def is_similar(row1, row2):
        # TODO: testar outras similaridades (autores, issn, etc.)
        if similaridade_entre_cadeias(row1['titulo'], row2['titulo']) and row1.type == row2.type:
            return True
        return False

    def group_similar(self):
        self.data_frame['similar'] = self.data_frame.index

        def set_similar(row, ref_row, ref_index):
            if self.is_similar(row, ref_row):
                row.similar = ref_index
            return row

        for i in self.data_frame.index:
            # self.data_frame.ix[:i-1][self.data_frame.ix[:i-1].apply(lambda x: self.is_similar(x, self.data_frame.ix[i]), axis=1)]
            self.data_frame = self.data_frame.apply(set_similar, axis=1, ref_row=self.data_frame.ix[i], ref_index=i)
        self.grouped = self.data_frame.groupby('similar')
        # grouped.aggregate({'id_membro': lambda x: frozenset(x)})
        # grouped.aggregate(list)
