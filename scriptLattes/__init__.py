# -*- coding: utf-8 -*-
"""
scriptlattes
~~~~~~~~~~~~~~~~~~~

Processador de currículos da Plataforma Lattes

:copyright: (c) 2015 by Jesús P. Mena-Chalco, Fábio N. Kepler
:licence: GPLv3, see LICENSE for more details
"""
from __future__ import absolute_import, unicode_literals
import logging

# Generate your own AsciiArt at:
# http://patorjk.com/software/taag/#p=display&f=Calvin%20S&t=scriptLattes
__banner__ = r"""
┌─┐┌─┐┬─┐┬┌─┐┌┬┐╦  ┌─┐┌┬┐┌┬┐┌─┐┌─┐
└─┐│  ├┬┘│├─┘ │ ║  ├─┤ │  │ ├┤ └─┐
└─┘└─┘┴└─┴┴   ┴ ╩═╝┴ ┴ ┴  ┴ └─┘└─┘
"""

__title__ = 'scriptLattes'
__summary__ = 'Processador de currículos da Plataforma Lattes'
__uri__ = 'https://bitbucket.org/scriptlattes/scriptlattes'

__version__ = '9.0.0'

__author__ = 'Jesús P. Mena-Chalco, Fabio N. Kepler'
__email__ = 'jesus.mena@ufabc.edu.br, kepler@unipampa.edu.br'

__license__ = 'GPLv3'
__copyright__ = 'Copyright 2015 Jesús P. Mena-Chalco, Fabio N. Kepler'

# the user should dictate what happens when a logging event occurs
logging.getLogger(__name__).addHandler(logging.NullHandler())
