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

    def __init__(self, cmd, name='-unnamed-', env=None, nondestructive=False, pre=None):
        self.cmd = cmd
        self.env = env or {}
        self.name = name
        self.nondestructive = nondestructive
        self.proc = None
        self.succeded = False
        self.value = ''
        self.pre = pre


    def __call__(self, *append):
        Action.exec_counter += 1

        if common.DRY_RUN and not self.nondestructive:
            self.succeded = True
            return self

        l = logging.getLogger(__name__)

        if self.pre:
            l.debug('Executing pre-function')
            self.pre()
        with open(f'{self.name}_{Action.exec_counter}.stdout', 'ab') as stdout_file, \
             open(f'{self.name}_{Action.exec_counter}.stderr', 'ab') as stderr_file:
            self.proc = sp.Popen(f'{self.cmd} {" ".join(append)}',
                                 shell=True,
                                 env={**os.environ, **self.env},
                                 stdout=stdout_file,
                                 stderr=stderr_file)
            print_len = 70
            while self.proc.poll() is None:
                try:
                    cpu_utilization = sp.check_output(f'ps --no-headers -p {self.proc.pid} -o %cpu,%mem,etime,cmd',
                                                      shell=True).decode().strip()
                    message = f'<cpu> <mem> <time> <cmd>: {" ".join(cpu_utilization.split())}'[0:print_len] + '...'
                    print(message, end='\r')
                except Exception:
                    # diagnostic message could not be fetched and it's okay
                    pass
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
    def __init__(self,
                 package,
                 options='',
                 use_flags='',
                 possible_quirks=None,
                 **kwargs):
        self.package = package
        if use_flags is not None:
            if type(use_flags) == list:
                use_flags = ' '.join(use_flags)
        self.use_flags = use_flags
        self.options = options
        self.possible_quirks = possible_quirks if possible_quirks else []
        self.cmd = f'emerge --autounmask-write {self.options} {package} || (echo -5 | etc-update && emerge {self.options} {package})'
        super().__init__(self.cmd,
                         name=f'{package.replace("/", "_")}',
                         nondestructive=False,
                         **kwargs)


    def __call__(self, *append):
        l = logging.getLogger(__name__)
        use_file_name = self.package.replace('/', '.')
        if self.use_flags:
            with open(f'/etc/portage/package.use/{use_file_name}', 'a') as use_flags_file:
                use_flags_file.write(f'{self.package} {self.use_flags}')

        l.debug(f'Possible quirks: [{self.possible_quirks}]')
        for q in self.possible_quirks:
            if q not in common.ENABLED_QUIRKS:
                continue
            l.debug(f'Quirk {q} enabled for {self.package}')
            with open('/etc/portage/package.env', 'a') as f:
                f.write(f'{self.package} {q}.conf\n')

        l.debug(f'Installing {self.package}, USE="{self.use_flags}"')
        super().__call__(*append)
        if not self.succeded:
            l.warning(f'{self.package} install failed')
        return self


class MetaAction(Action):
    def __init__(self, cmds, name='-unnamed-meta-action-',  env=None, nondestructive=False, pre=None):
        self.actions = [Action(cmd,
                               f'{name}-{i}',
                               env,
                               nondestructive,
                               pre) for i, cmd in enumerate(cmds)]
        self.succeded = True
        self.name = name


    def __call__(self, *append):
        for a in self.actions:
            Executor.exec(a, *append)
            if not a.succeded:
                self.succeded = False
        return self


    def __str__(self):
        return f"{self.name} -> {self.actions}"


    def __hash__(self):
        return int(hashlib.md5((str(self) + str(Action.exec_counter)).encode()).hexdigest(), 16)


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
