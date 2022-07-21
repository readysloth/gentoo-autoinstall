import logging
import functools as ft

import common
from common import Colors

class InstallLogger(logging.Logger):
    def __init__(self, *args, **kwargs):
        logging.basicConfig(level=common.LOGGER_LEVEL,
                            format='%(asctime)s :: %(name)-10s :: %(levelname)-10s :: %(message)s',
                            datefmt=f'%d.%m.%Y {Colors.MAGENTA}%H:%M:%S{Colors.ENDC}')
        super().__init__(*args, **kwargs)


    def add_color(self, func, color, msg):
        return ft.partial(func, f'{color}{msg}{Colors.ENDC}')


    def debug(self, msg, *args, **kwargs):
        self.add_color(super().debug, Colors.CYAN, msg)(*args, **kwargs)


    def info(self, msg, *args, **kwargs):
        self.add_color(super().info, Colors.BOLD, msg)(*args, **kwargs)


    def checkpoint(self, msg, *args, **kwargs):
        self.add_color(super().info, Colors.BLUE, msg)(*args, **kwargs)


    def warning(self, msg, *args, **kwargs):
        self.add_color(super().warning, Colors.WARNING, msg)(*args, **kwargs)


    def error(self, msg, *args, **kwargs):
        self.add_color(super().error, Colors.FAIL, msg)(*args, **kwargs)


logging.setLoggerClass(InstallLogger)
