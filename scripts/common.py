import os
import re
import logging
import subprocess as sp

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

LOGGER_LEVEL = logging.INFO
if 'LOGLEVEL' in os.environ:
    LOGGER_LEVEL = getattr(logging,
                           os.environ['LOGLEVEL'],
                           LOGGER_LEVEL)


DRY_RUN = False
MAKE_CONF_PATH = '/etc/portage/make.conf'
BIN_CONF_PATH = '/etc/portage/binrepos.conf'
DEFAULT_GENTOO_PROFILE = 6
RESUME = False
EXECUTED_ACTIONS_FILENAME = 'executed.actions'
QUIRKS = [('delay-performance', 'Delay portage performance tweaks to after install stage'),
          ('linker-tradeoff', 'GNU linker can use less memory at the expense of IO')]


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


def remove_variable_value(filename, variable_name, value='', quot='"', delim=' ', full=False):
    variable_name_re = re.compile(fr'^\s*{variable_name}=')
    changed_lines = []
    with open(filename, 'r') as file:
        for l in file:
            if variable_name_re.match(l):
                if full:
                    continue
                changed_lines.append(l.replace(value, ''))
            else:
                changed_lines.append(l)

    with open(filename, 'w') as file:
        file.writelines(changed_lines)


def add_variable_to_file(filename, variable_name, value, quot='"'):
    with open(filename, 'a') as file:
        file.write(f'{variable_name}={quot}{value}{quot}\n')


def source(file):
    command = shlex.split(f"env -i bash -c 'source {file} && env'")
    proc = sp.Popen(command, stdout = sp.PIPE)
    for line in proc.stdout:
        variable = line.decode().strip()
        (key, _, value) = formatted_line.partition('=')
        os.environ[key] = value
