#!/usr/bin/python
# encoding: utf-8
# filename: authorRank.py
#
#  scriptLattes V8
#  Copyright 2005-2013: Jesús P. Mena-Chalco e Roberto M. Cesar-Jr.
#  http://scriptlattes.sourceforge.net/
#
#
#  Este programa é um software livre; você pode redistribui-lo e/ou
#  modifica-lo dentro dos termos da Licença Pública Geral GNU como
#  publicada pela Fundação do Software Livre (FSF); na versão 2 da
#  Licença, ou (na sua opinião) qualquer versão.
#
#  Este programa é distribuído na esperança que possa ser util,
#  mas SEM NENHUMA GARANTIA; sem uma garantia implicita de ADEQUAÇÂO a qualquer
#  MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
#  Licença Pública Geral GNU para maiores detalhes.
#
#  Você deve ter recebido uma cópia da Licença Pública Geral GNU
#  junto com este programa, se não, escreva para a Fundação do Software
#  Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import logging

import numpy

logger = logging.getLogger(__name__)


class AuthorRank:
    def __init__(self, matrix, iterations):
        # self.matrix = matrix
        self.rank_vector = numpy.ones(matrix.shape[0], dtype=numpy.float32)

        logger.info("[CALCULANDO AUTHOR-RANK (PROCESSO ITERATIVO)]")
        d = 0.85  # dumping factor (fator de amortecimento)
        for iteration in range(iterations):
            # self.author_rank_vector = self.calculate_ranks(self.author_rank_vector)
            self.rank_vector = (1 - d) + d * (self.rank_vector * matrix)
            logger.debug("{}/{} iterations".format(iteration + 1, iterations))

    # def calculate_ranks(self, author_rank_vector):
        # d = 0.85  # dumping factor (fator de amortecimento)
        # new_rank_vector = numpy.zeros(len(author_rank_vector), dtype=numpy.float32)
        # for i in range(len(author_rank_vector)):
        #     soma = 0
        #     for j in range(len(author_rank_vector)):
        #         soma += author_rank_vector[j] * self.matrix[j, i]
        #     new_rank_vector[i] = (1 - d) + d * soma

        # return new_rank_vector
