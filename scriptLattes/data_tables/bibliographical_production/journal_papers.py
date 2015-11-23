# encoding: utf-8
import logging
from scipy import sparse

import pandas as pd

from util.util import similaridade_entre_cadeias

logger = logging.getLogger(__name__)


class JournalPapers:
    columns = ['id_membro',
               'titulo',
               'ano',
               'doi',
               'relevante',
               'revista',
               'issn',
               'volume',
               'numero',
               'paginas',
               'qualis',
               'autores']

    def __init__(self, id):
        self.id = id
        self.data_frame = pd.DataFrame(columns=self.columns)

    def add_from_parser(self, papers_list):
        # list of ArtigoEmPeriodico
        papers = []
        for paper in papers_list:
            papers.append([getattr(paper, attribute) for attribute in self.columns[1:]])  # skip id_membro
        papers_df = pd.DataFrame(papers, columns=self.columns[1:])
        papers_df['id_membro'] = self.id
        self.data_frame = self.data_frame.append(papers_df, ignore_index=True)

    def append(self, papers):
        assert isinstance(papers, JournalPapers)
        self.data_frame = self.data_frame.append(papers.data_frame, ignore_index=True)

    @staticmethod
    def is_similar(row1, row2):
        # TODO: testar outras similaridades (autores, issn, etc.)
        # TODO: ver se é preciso ignorar quando id_membro é o mesmo
        if similaridade_entre_cadeias(row1['titulo'], row2['titulo']):
            return True
        return False

    def group_similar(self):
        self.data_frame['similar'] = self.data_frame.index

        def set_similar(row, ref_row, ref_index):
            if self.is_similar(row, ref_row):
                row.similar = ref_index
            return row

        # FIXME: optimize (it's O(n^2))
        for i in self.data_frame.index:
            # self.data_frame.ix[:i-1][self.data_frame.ix[:i-1].apply(lambda x: self.is_similar(x, self.data_frame.ix[i]), axis=1)]
            self.data_frame = self.data_frame.apply(set_similar, axis=1, ref_row=self.data_frame.ix[i], ref_index=i)
        self.grouped = self.data_frame.groupby('similar')
        # grouped.aggregate({'id_membro': lambda x: frozenset(x)})
        # grouped.aggregate(list)

    def get_co_authorship_frequency_matrix(self):
        if 'similar' not in self.data_frame.columns:
            self.group_similar()  # TODO: não precisa sempre; verificar
        # self.grouped.filter(lambda x: len(x) > 1)
        co_authorships = [group for group in self.grouped.groups.values() if len(group) > 1]
        frequency_matrix = sparse.lil_matrix((self.grupo.numeroDeMembros(), self.grupo.numeroDeMembros()))
        # FIXME: retornar só a lista de co-autorias (com ids lattes); é o grupo que tem que usar os id_lattes para extrair o índice de cada membro e assim criar a matriz

        for k in sorted(listaCompleta.keys(), reverse=True):
            for pub in listaCompleta[k]:

                numeroDeCoAutores = len(pub.idMembro)
                if numeroDeCoAutores > 1:
                    # Para todos os co-autores da publicacao:
                    # (1) atualizamos o contador de colaboracao (adjacencia)
                    # (2) incrementamos a 'frequencia' de colaboracao
                    for c in itertools.combinations(pub.idMembro, 2):
                        # combinacoes 2 a 2 de todos os co-autores da publicação
                        # exemplo:
                        # lista = [0, 3, 1]
                        # combinacoes = [[0,3], [0,1], [3,1]]
                        adjacency_matrix[c[0], c[1]] += 1
                        adjacency_matrix[c[1], c[0]] += 1

                        frequency_matrix[c[0], c[1]] += 1.0 / (numeroDeCoAutores - 1)
                        frequency_matrix[c[1], c[0]] += 1.0 / (numeroDeCoAutores - 1)


    def __len__(self):
        return len(self.data_frame)
