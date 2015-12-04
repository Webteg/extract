#!/usr/bin/python
# encoding: utf-8
# filename: grafoDeColaboracoes.py
# filename: collaboration_graph.py
#
# scriptLattes V8
# Copyright 2005-2013: Jesús P. Mena-Chalco e Roberto M. Cesar-Jr.
# http://scriptlattes.sourceforge.net/
#
# scriptLattes 9.0.0
# Copyright 2015: Fabio Kepler <fabio@kepler.pro.br>
# http://bitbucket.org/scriptlattes/scriptlattes
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

# FIXME: uncomment pygraphviz or replace it
# import pygraphviz  # TODO: replace with graph_tool
# import Image
from PIL import Image
from pathlib import Path
from grupo import Grupo
from util.util import get_lattes_url

logger = logging.getLogger(__name__)


def abbreviate_name(name):
    # No grafo de colaboracoes nomes cumpridos não ajudam na visualização da co-autoria.
    # para tal, precisamos abreviar os nomes.
    # Ex.
    #     'Jesus Pascual Mena Chalco'         -> 'Jesus P. Mena Chalco'
    #     'Aaaaaa BBBBBB da CCCCCCC e DDDDDD' -> 'Aaaaaa B. da CCCCCCC e DDDDDD'

    names = name.split(' ')
    if len(names) >= 4:
        index = 2 if len(names[-2]) > 3 else 3

        abbreviated_name = names[0]
        for i in range(1, len(names) - index):
            if len(names[i]) >= 3:
                abbreviated_name += " " + names[i][0] + "."
            else:
                abbreviated_name += " " + names[i]
        for i in range(len(names) - index, len(names)):
            abbreviated_name += " " + names[i]
    else:
        abbreviated_name = name

    return abbreviated_name


class CollaborationGraph:
    def __init__(self, group):
        assert isinstance(group, Grupo)
        self.group = group

    def create_all(self, output_directory, use_labels=False, show_all_nodes=False, weight_collaborations=False):
        assert isinstance(output_directory, Path)

        # atribuicao de cores nos vértices
        fg_node_color = '#FFFFFF'
        bg_node_color = '#17272B'
        members_color_map = {}
        for member_id, member in self.group.members_list.items():
            if use_labels:
                fg_node_color, bg_node_color = self.get_cool_color(self.group.labels_set.index(member.rotulo))
            members_color_map[member_id] = (fg_node_color, bg_node_color)
            # self.grupo.atribuirCoNoRotulo(indice, corDoNoBG)
            # membro.rotuloCorFG = fg_node_color
            # membro.rotuloCorBG = bg_node_color

        co_authorship_unweighted = self.create_co_authorship_unweighted_graph(members_color_map, show_all_nodes=show_all_nodes)
        co_authorship_unweighted.draw(path=str(output_directory / 'grafoDeColaboracoesSemPesos.png'), format='png')
        co_authorship_unweighted.draw(path=str(output_directory / 'grafoDeColaboracoesSemPesos.dot'), format='dot')
        co_authorship_unweighted_CMAPX = co_authorship_unweighted.draw(format='cmapx')

        co_authorship_weighted = self.create_co_authorship_weighted_graph(members_color_map, show_all_nodes=show_all_nodes)
        co_authorship_weighted.draw(path=str(output_directory / 'grafoDeColaboracoesComPesos.png'), format='png')
        co_authorship_weighted.draw(path=str(output_directory / 'grafoDeColaboracoesComPesos.dot'), format='dot')
        co_authorship_weighted_CMAPX = co_authorship_weighted.draw(format='cmapx')

        co_authorship_normalized = self.create_co_authorship_normalized_graph(members_color_map, show_all_nodes=show_all_nodes,
                                                                              weight_collaborations=weight_collaborations)
        co_authorship_normalized.draw(path=str(output_directory / 'grafoDeColaboracoesNormalizado.png'), format='png')
        co_authorship_normalized.draw(path=str(output_directory / 'grafoDeColaboracoesNormalizado.dot'), format='dot')
        co_authorship_normalized_CMAPX = co_authorship_normalized.draw(format='cmapx')

        # self.grafoDeCoAutoriaCompleta = self.criarGrafoDeCoAutoriaCompleta()
        # self.grafoDeCoAutoriaCompleta.draw(path='grafoDeColaboracoesCompleto.png', format='png')
        # self.grafoDeCoAutoriaCompleta.draw(path='grafoDeColaboracoesCompleto.dot', format='dot')
        # self.grafoDeCoAutoriaCompletaCMAPX = self.grafoDeCoAutoriaCompleta.draw(format='cmapx')

        # Criamos um thumbnail do grafo sem pesos
        im = Image.open(str(output_directory / 'grafoDeColaboracoesSemPesos.png'))
        im.thumbnail((400, 400))
        im.save(str(output_directory / 'grafoDeColaboracoesSemPesos-t.png'))

    def create_co_authorship_unweighted_graph(self, members_color_map, show_all_nodes=False):
        logger.info("[CRIANDO GRAFOS DE COLABORACOES SEM PESOS]")

        graph = pygraphviz.AGraph(directed=False, overlap="False", id="grafo1", name="grafo1")
        graph.node_attr['shape'] = 'rectangle'
        graph.node_attr['fontsize'] = '8'
        graph.node_attr['style'] = 'filled'

        # Inserimos os nos
        self.add_nodes(graph, show_all_nodes, members_color_map)

        # Inserimos as arestas
        for i in range(len(self.group.members_list) - 1):
            for j in range(i, len(self.group.members_list)):
                if self.group.co_authorship_adjacency_matrix[i, j] > 0:
                    graph.add_edge(i, j)

        graph.layout('dot')  # circo dot neato
        return graph

    def create_co_authorship_weighted_graph(self, members_color_map, show_all_nodes=False):
        logger.info("[CRIANDO GRAFOS DE COLABORACOES COM PESOS]")

        graph = pygraphviz.AGraph(directed=False, overlap="False", id="grafo2", name="grafo2")
        graph.node_attr['shape'] = 'rectangle'
        graph.node_attr['fontsize'] = '8'
        graph.node_attr['style'] = 'filled'

        # Inserimos os nos
        self.add_nodes(graph, show_all_nodes, members_color_map)

        # Inserimos as arestas
        for i in range(len(self.group.members_list) - 1):
            for j in range(i, len(self.group.members_list)):
                if self.group.co_authorship_adjacency_matrix[i, j] > 0:
                    graph.add_edge(i, j, label=str(self.group.co_authorship_adjacency_matrix[i, j]), fontsize='8')

        graph.layout('dot')  # circo dot neato
        return graph

    def create_co_authorship_normalized_graph(self, members_color_map, show_all_nodes=False, weight_collaborations=False):
        logger.info("[CRIANDO GRAFOS DE COLABORACOES NORMALIZADO]")

        graph = pygraphviz.AGraph(directed=True, overlap="False", id="grafo3", name="grafo3")
        graph.node_attr['shape'] = 'rectangle'
        graph.node_attr['fontsize'] = '8'
        graph.node_attr['style'] = 'filled'

        # Inserimos os nos: This is SPARTA!!!
        self.add_nodes(graph, show_all_nodes, members_color_map)

        # Inserimos as arestas
        for i in range(len(self.group.members_list)):
            for j in range(len(self.group.members_list)):
                normalized_freq = round(self.group.co_authorship_normalized_weighted_matrix[i, j], 2)
                if normalized_freq > 0:
                    if weight_collaborations:
                        width = str(0.5 + 3 * normalized_freq)
                    else:
                        width = '1'
                    graph.add_edge(i, j, label=str(normalized_freq), fontsize='8', penwidth=width, arrowhead='normal',
                                   arrowsize='0.75')

        graph.layout('dot')  # dot
        return graph

    # def criarGrafoDeCoAutoriaCompleta(self):
    #     print "\n[CRIANDO GRAFOS DE COLABORACOES SEM PESOS - COMPLETA]"
    #
    #     grafo = pygraphviz.AGraph(strict=False, directed=False, ratio="compress")
    #     grafo.node_attr['shape'] = 'rectangle'
    #     grafo.node_attr['fontsize'] = '8'
    #     grafo.node_attr['style'] = 'filled'
    #
    #     # Inserimos os nos
    #     for m in range(0, len(self.grupo)):
    #         membro = self.grupo.members_list.values()[m]
    #         nome = abbreviate_name(membro.nomeCompleto).encode('utf8') + " [" + str(
    #             int(self.grupo.co_authorship_vector[m])) + "]"
    #
    #         if self.grupo.obterParametro('grafo-considerar_rotulos_dos_membros_do_grupo'):
    #             indice = self.grupo.listaDeRotulos.index(membro.rotulo)
    #             cor = self.get_cool_color(indice)
    #             corDoNoFG = cor[0]
    #             corDoNoBG = cor[1]
    #             self.grupo.atribuirCoNoRotulo(indice, corDoNoBG)
    #         else:
    #             corDoNoFG = '#FFFFFF'
    #             corDoNoBG = '#003399'
    #
    #         if self.grupo.co_authorship_vector[m] > 0 or self.grupo.obterParametro('grafo-mostrar_todos_os_nos_do_grafo'):
    #             grafo.add_node(membro.idMembro, label=nome, fontcolor=corDoNoFG, color=corDoNoBG, height="0.2",
    #                            URL=membro.url, root='True')
    #
    #             for idColaborador in membro.listaIDLattesColaboradoresUnica:
    #                 inserir = 1
    #                 for mtmp in self.grupo.members_list.values():
    #                     if idColaborador == mtmp.idLattes:
    #                         inserir = 0
    #
    #                 if inserir:
    #                     grafo.add_node(idColaborador, fontcolor='white', color='black', height="0.2", shape="point")
    #                     grafo.add_edge(idColaborador, membro.idMembro)
    #
    #     # Inserimos as arestas
    #     for i in range(0, len(self.grupo) - 1):
    #         for j in range(i, len(self.grupo)):
    #             if self.grupo.co_authorship_normalized_weighted_matrix[i, j] > 0:
    #                 grafo.add_edge(i, j)
    #
    #     # grafo.layout('twopi')
    #     grafo.layout('circo')
    #     return grafo

    def add_nodes(self, graph, show_all_nodes, members_color_map):
        for m, (member_id, member) in enumerate(self.group.members_list.items()):
            name = abbreviate_name(member.nome) + " [" + str(int(self.group.co_authorship_vector[m])) + "]"
            if self.group.co_authorship_vector[m] > 0 or show_all_nodes:
                try:
                    graph.add_node(member_id, label=name, fontcolor=members_color_map[member_id][0], color=members_color_map[member_id][1],
                                   height="0.2", URL=get_lattes_url(member.id_lattes))
                except:
                    graph.add_node(member.idMembro, label=name.encode('utf8'), fontcolor=members_color_map[member_id][0],
                                   color=members_color_map[member_id][1], height="0.2", URL=get_lattes_url(member.id_lattes))

    @staticmethod
    def get_cool_color(index):
        colors = [
            ('#FFFFFF', '#000099'),  # azul
            ('#FFFFFF', '#006600'),  # verde
            ('#FFFFFF', '#990000'),  # vermelho
            ('#FFFFFF', '#FF3300'),  # laranja
            ('#FFFFFF', '#009999'),  # esmeralda legal
            ('#000000', '#FF33CC'),  # pink
            ('#FFFFFF', '#333333'),  # cinza
            ('#000000', '#FFFF00'),  # amarelo
            ('#FFFFFF', '#0033FF'),  # azul eletric
            ('#FFFFFF', '#330000'),  # marrom
            ('#FFFFFF', '#330099'),  # roxo
            ('#000000', '#CC9999'),
            ('#000000', '#FF99CC'),
            ('#000000', '#FFCCFF'),
            ('#000000', '#999933'),
            ('#FFFFFF', '#339966'),
            ('#FFFFFF', '#660033'),
            ('#000000', '#00CC99'),
            ('#000000', '#99FFCC'),  # esmeralda
            ('#FFFFFF', '#330033'),  # roxo escuro
            ('#000000', '#FFFFFF')]

        if index < len(colors):
            return colors[index]
        else:
            return colors[-1]
