__author__ = 'kepler'

import pandas as pd


class BibliographicalProduction:

    def __init__(self, journal_papers, event_papers):
        assert isinstance(journal_papers, pd.DataFrame)
        assert isinstance(event_papers, pd.DataFrame)

        data = {
            'journal': journal_papers,
            'event': event_papers
        }
        self.productions = pd.Panel(data)
