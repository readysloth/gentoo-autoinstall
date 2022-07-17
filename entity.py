import logging
import subprocess as sp

from abc import ABC

import common
import install_logger


class Action:
    def __init__(self, cmd, name='', env=None):
        self.cmd = cmd
        self.env = env or {}
        self.name = name
        self.proc = None
        self.succeded = False
        self.value = ''


    def __call__(self, *append):
        if common.DRY_RUN:
            self.succeded = True
            return self

        self.proc = sp.Popen(self.cmd.split() + list(append),
                             shell=True,
                             env=self.env,
                             stdout=sp.PIPE,
                             stderr=sp.PIPE)
        self.proc.wait()
        self.succeded = self.proc.returncode == 0
        self.value = self.proc.stdout.read().decode()
        return self


    def report(self):
        if self.proc:
            with open(self.name, 'wb'):
                fd.write(str(self).encode())
                fd.write(b'-----BEGIN STDOUT-----')
                fd.write(finished_process.stdout)
                fd.write(b'-----END STDOUT-----')
                fd.write(b'-----BEGIN STDERR-----')
                fd.write(finished_process.stderr)
                fd.write(b'-----END STDERR-----')


    def __str__(self):
        begin = f"{self.env} [{self.name}]({self.cmd})"
        if self.proc:
            return f"{begin} = {self.proc.returncode}"
        return begin


class Executor(ABC):
    @staticmethod
    def exec(action, *args, fallbacks=None, do_crash=False):
        l = logging.getLogger(__name__)
        l.info(f'Executing {action.name}')
        l.debug(f'Start of {action}')
        ended_action = action(*args)
        l.debug(f'End of {ended_action}, successfully? {ended_action.succeded}')
        ended_action.report()
        if not ended_action.succeded:
            if fallbacks:
                for fallback in fallbacks:
                    l.debug(f'Fallback start {fallback} do_crash={do_crash}')
                    ended_fallback = fallback()
                    l.debug(f'Fallback end {fallback}, successfully? {ended_fallback.succeded}')
                    ended_fallback.report()
                    if ended_fallback.succeded:
                        return
            if do_crash:
                l.info(f'do_crash specified and fallbock return code is not 0, crash attempt imminent')
                raise RuntimeError(f'For failed [{action}] every specified fallback failed too')
