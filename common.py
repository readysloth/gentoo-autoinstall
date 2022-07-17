import os
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
