# *-* coding: utf-8 *-*
from collections import OrderedDict, defaultdict
import pandas as pd

__author__ = 'kepler'


class TechnicalProductions:
    def __init__(self, softwares, produtos_tecnologicos, processos_ou_tecnicas, trabalhos_tecnicos, demais_tipos_de_producao_tecnica):

        data = {
            'softwares': softwares,
            'produtos_tecnologicos': produtos_tecnologicos,
            'processos_ou_tecnicas': processos_ou_tecnicas,
            'trabalhos_tecnicos': trabalhos_tecnicos,
            'demais_tipos_de_producao_tecnica': demais_tipos_de_producao_tecnica,
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
