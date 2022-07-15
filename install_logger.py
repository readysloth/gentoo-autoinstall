import os
import logging
import functools as ft

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


class InstallLogger(logging.Logger):
    def __init__(self, *args, **kwargs):
        logging.basicConfig(level=logging.DEBUG)
        super().__init__(*args, **kwargs)


    def add_color(self, func, color, msg):
        return ft.partial(func, f'{color}{msg}{Colors.ENDC}')


    def debug(self, msg, *args, **kwargs):
        self.add_color(super().debug, Colors.CYAN, msg)(*args, **kwargs)


    def info(self, msg, *args, **kwargs):
        self.add_color(super().info, Colors.BOLD, msg)(*args, **kwargs)


    def warning(self, msg, *args, **kwargs):
        self.add_color(super().warning, Colors.WARNING, msg)(*args, **kwargs)


    def error(self, msg, *args, **kwargs):
        self.add_color(super().error, Colors.FAIL, msg)(*args, **kwargs)


logging.setLoggerClass(InstallLogger)
