# *-* coding: utf-8 *-*
__author__ = 'kepler'


class BibliographicalProductions:

    def __init__(self, journal_papers, event_papers):
        # assert isinstance(journal_papers, pd.DataFrame)
        # assert isinstance(event_papers, pd.DataFrame)

        data = {
            'journal': journal_papers,
            'event': event_papers
        }
        # XXX: não serve; deixa todos data frames com o mesmo tamanho, cheio de NaNs
        # self.productions = pd.Panel(data)
        self.productions = data

    def __len__(self):
        return sum(len(production) for production in self.productions.values())
