import os
import re
import logging

class Colors:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    MAGENTA = '\033[35;1m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

DRY_RUN = False

LOGGER_LEVEL = logging.INFO
if 'LOGLEVEL' in os.environ:
    LOGGER_LEVEL = getattr(logging,
                           os.environ['LOGLEVEL'],
                           LOGGER_LEVEL)


def add_value_to_string_variable(filename, variable_name, value, quot='"', delim=' '):
    variable_name_re = re.compile(fr'^\s*{variable_name}=')
    variable_value_re = re.compile(fr'{quot}([^{quot}]*){quot}')
    changed_lines = []
    with open(filename, 'r') as file:
        for l in file:
            if variable_name_re.match(l):
                changed_lines.append(variable_value_re.sub(fr'{quot}\1{delim}{value}{quot}', l))
            else:
                changed_lines.append(l)

    with open(filename, 'w') as file:
        file.writelines(changed_lines)


def add_variable_to_file(filename, variable_name, value, quot='"'):
    with open(filename, 'a') as file:
        file.write(f'{variable_name}={quot}{value}{quot}\n')
