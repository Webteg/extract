#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
config_migrator
~~~~~~~~~~~~

Convert the obsolete config file format to the new format. A backup is created for the obsolete file format.

Invoke as ``python config_migrator`` (no install required).

Usage:
  config_migrator CONFIG_FILE
  config_migrator (-h | --help | --version)

Arguments:
  CONFIG_FILE  arquivo de configuração

Options:
  -h --help            show this help message and exit
  --version            show version and exit
  -v --verbose         log debug messages
  -q --quiet           log only warning and error messages

"""
import logging

from configobj import ConfigObj
from docopt import docopt
from pathlib import Path

logging.basicConfig(format="[%(asctime)s] %(name)-25s %(levelname)-8s %(message)s")
logger = logging.getLogger()

__version__ = '0.0.1'

rename_sections = {'global': 'geral'}
rename_keys = {'extrair_qualis_online': 'usar_cache_qualis'}

def is_last_version(config_file_path):
    config = ConfigObj(str(config_file_path))
    if config.sections:  # not empty
        return True
    return False


def migrate_config_file(file_path):
    if not isinstance(file_path, Path):
        file_path = Path(file_path)
    if not file_path.exists():
        logger.error("Arquivo de configuração '{}' não existe.".format(file_path))
        return False
    if not file_path.is_file():
        logger.error("Caminho '{}' não é um arquivo de configuração.".format(file_path))
        return False
    config = ConfigObj(str(file_path))
    if is_last_version(file_path):
        logger.error("Configurações em '{}' já estão no novo formato.".format(file_path))
        return True

    bak_file = '.old'
    i = 1
    while file_path.with_suffix(bak_file).exists():
        bak_file = '.old{}'.format(i)
        i += 1
    new_file_path = Path(file_path)
    file_path.rename(file_path.with_suffix(bak_file))

    new_config = ConfigObj(infile=str(new_file_path), create_empty=True, write_empty_values=True, default_encoding='utf-8', encoding='utf-8')
    new_config.initial_comment = config.initial_comment
    new_config.final_comment = config.final_comment

    for key, value in config.items():
        if not isinstance(value, dict):
            section, new_key = key.split('-', 1)
            if section in rename_sections.keys():
                section = rename_sections[section]
            if new_key in rename_keys.keys():
                new_key = rename_keys[new_key]
            if section not in new_config.sections:
                new_config[section] = {}
                new_config.comments[section] = config.comments[key]
            else:
                new_config[section].comments[new_key] = config.comments[key]
            new_config[section][new_key] = value
            new_config[section].inline_comments[new_key] = config.inline_comments[key]

    new_config.write()
    return True


if __name__ == "__main__":
    arguments = docopt(__doc__, argv=None, help=True, version=__version__, options_first=False)
    config_file_path = Path(arguments['CONFIG_FILE'])
    migrate_config_file(config_file_path)
