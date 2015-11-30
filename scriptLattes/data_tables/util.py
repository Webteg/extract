# encoding: utf-8
import itertools
from scipy import sparse


def create_adjacency_matrix(members_indices, co_authors_list):
    """
    Create and return matrix from the given co-authors list.

    :param members_indices:
    :param co_authors_list:
    :return:
    """
    adjacency_matrix = sparse.lil_matrix((len(members_indices), len(members_indices)))

    for co_authors in co_authors_list:
        # Para todos os co-autores da publicacao:
        # (1) atualizamos o contador de colaboracao (adjacencia)
        # (2) incrementamos a 'frequencia' de colaboracao
        co_authors_indices = [members_indices[lattes_id] for lattes_id in co_authors]
        for co_authors_pair in itertools.combinations(co_authors_indices, 2):
            # combinacoes 2 a 2 de todos os co-autores da publicação
            # exemplo:
            # lista = [0, 3, 1]
            # combinacoes = [[0,3], [0,1], [3,1]]
            adjacency_matrix[co_authors_pair[0], co_authors_pair[1]] += 1
            adjacency_matrix[co_authors_pair[1], co_authors_pair[0]] += 1

    return adjacency_matrix


def create_weighted_matrix(members_indices, co_authors_list):
    """
    Create and return matrices from the given co-authors list.

    :param members_indices:
    :param co_authors_list:
    :return:
    """
    weighted_matrix = sparse.lil_matrix((len(members_indices), len(members_indices)))

    for co_authors in co_authors_list:
        # Para todos os co-autores da publicacao:
        # (1) atualizamos o contador de colaboracao (adjacencia)
        # (2) incrementamos a 'frequencia' de colaboracao
        co_authors_indices = [members_indices[lattes_id] for lattes_id in co_authors]
        for co_authors_pair in itertools.combinations(co_authors_indices, 2):
            # combinacoes 2 a 2 de todos os co-autores da publicação
            # exemplo:
            # lista = [0, 3, 1]
            # combinacoes = [[0,3], [0,1], [3,1]]
            weighted_matrix[co_authors_pair[0], co_authors_pair[1]] += 1.0 / (len(co_authors) - 1)
            weighted_matrix[co_authors_pair[1], co_authors_pair[0]] += 1.0 / (len(co_authors) - 1)

    return weighted_matrix

