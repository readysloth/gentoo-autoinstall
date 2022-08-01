import os
import time
import logging
import hashlib
import subprocess as sp

from abc import ABC

import common
import install_logger


class Action:
    exec_counter = 0

    def __init__(self, cmd, name='-unnamed-', env=None, nondestructive=False):
        self.cmd = cmd
        self.env = env or {}
        self.name = name
        self.nondestructive = nondestructive
        self.proc = None
        self.succeded = False
        self.value = ''


    def __call__(self, *append):
        Action.exec_counter += 1

        if common.DRY_RUN and not self.nondestructive:
            self.succeded = True
            return self

        l = logging.getLogger(__name__)

        with open(f'{self.name}_{Action.exec_counter}.stdout', 'ab') as stdout_file, \
             open(f'{self.name}_{Action.exec_counter}.stderr', 'ab') as stderr_file:
            self.proc = sp.Popen(f'{self.cmd} {" ".join(append)}',
                                 shell=True,
                                 env={**os.environ, **self.env},
                                 stdout=stdout_file,
                                 stderr=stderr_file)
            print_len = 70
            while self.proc.poll() is None:
                cpu_utilization = sp.check_output(f'ps --no-headers -p {self.proc.pid} -o %cpu,%mem,etime,cmd',
                                                  shell=True).decode().strip()
                message = f'<cpu> <mem> <time> <cmd>: {" ".join(cpu_utilization.split())}'[0:print_len] + '...'
                print(message, end='\r')
            print(' '*(print_len+3), end='\r')
            self.proc.wait()
            self.succeded = self.proc.returncode == 0
        with open(f'{self.name}_{Action.exec_counter}.stdout', 'r') as stdout_file:
            self.value = stdout_file.read().strip()
            l.debug(f'[{self.name}] value = "{self.value}"')
        return self


    def __str__(self):
        begin = f"{self.env} [{self.name}]({self.cmd})"
        if self.proc:
            return f"{begin} = {self.proc.returncode}"
        return begin


    def __hash__(self):
        return int(hashlib.md5((self.name + self.cmd + str(Action.exec_counter)).encode()).hexdigest(), 16)


class Package(Action):
    def __init__(self, package, options='', use_flags=''):
        self.package = package
        if use_flags is not None:
            if type(use_flags) == list:
                use_flags = ' '.join(use_flags)
        self.use_flags = use_flags
        super().__init__(f'emerge {options} {package}',
                         name=f'{package.replace("/", "_")}',
                         nondestructive=False)


    def __call__(self, *append):
        l = logging.getLogger(__name__)
        use_file_name = self.package.replace('/', '.')
        with open(f'/etc/portage/package.use/{use_file_name}', 'a') as use_flags_file:
            use_flags_file.write(f'{self.package} {self.use_flags}')
        l.debug(f'Installing {self.package}, USE="{self.use_flags}"')
        if not self.succeded:
            l.warning(f'{self.package} install failed')
        super().__call__(*append)
        return self


class Executor(ABC):
    executed_actions_set = None
    executed_actions_file = None

    @staticmethod
    def init():
        Executor.executed_actions_file = open(common.EXECUTED_ACTIONS_FILENAME, 'a')
        with open(common.EXECUTED_ACTIONS_FILENAME, 'r') as f:
            Executor.executed_actions_set = set(map(int, map(str.strip, f.readlines())))


    @staticmethod
    def exec(action, *args, fallbacks=None, do_crash=False):
        l = logging.getLogger(__name__)
        if common.RESUME and hash(action) in Executor.executed_actions_set:
            l.info(f'Skipping "{action.name}"')
            Action.exec_counter += 1
            return

        l.info(f'Executing "{action.name}"')
        l.debug(f'Start of {action} + {list(args)}')
        ended_action = action(*args)
        l.debug(f'End of {ended_action}, successfully? {ended_action.succeded}')
        if not ended_action.succeded:
            if fallbacks:
                for fallback in fallbacks:
                    l.debug(f'Fallback start {fallback} do_crash={do_crash}')
                    ended_fallback = fallback()
                    l.debug(f'Fallback end {fallback}, successfully? {ended_fallback.succeded}')
                    if ended_fallback.succeded:
                        Executor.executed_actions_file.writeline(f'{hash(action)}\n')
                        Executor.executed_actions_file.flush()
                        return
            if do_crash:
                l.info(f'do_crash specified and fallback return code is not 0, crash attempt imminent')
                raise RuntimeError(f'For failed [{action}] every specified fallback failed too')
        else:
            Executor.executed_actions_file.write(f'{hash(action)}\n')
            Executor.executed_actions_file.flush()


    @staticmethod
    def close():
        Executor.executed_actions_file.close()


def init_executor():
    Executor.init()


def deinit_executor():
    Executor.close()
