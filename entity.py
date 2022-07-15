import logging
import subprocess as sp

from abc import ABC, abstractmethod

import install_logger


class Action:
    def __init__(self, name, cmd, env):
        self.cmd = cmd
        self.env = env
        self.name = name
        self.proc = None
        self.succeded = False


    def __call__(self, *append):
        self.proc = sp.Popen(self.cmd.split() + append,
                             shell=True,
                             env=self.env,
                             stdout=sp.PIPE,
                             stderr=sp.PIPE)
        self.proc.wait()
        self.succeded = self.proc.returncode == 0
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
        begin = f"{self.env} {self.name}({self.cmd})"
        if self.proc:
            return f"{begin} = {self.proc.returncode}"
        return begin


class Executor(ABC):
    @abstractmethod
    def exec(self, action, fallbacks=None, do_crash=False):
        l = logger.getLogger('install_logger')
        l.debug(f'At the start of an action({action})')
        ended_action = action()
        l.debug(f'action({ended_action}) ended with [{ret}]')
        ended_action.report()
        if ended_action.succeded:
            if fallbacks:
                for fallback in fallbacks:
                    l.debug(f'At the start of fallback({fallback}) do_crash={do_crash}')
                    ended_fallback = fallback()
                    l.debug(f'fallback({fallback}) ended with [{fret}]')
                    ended_fallback.report()
                    if ended_fallback.succeded:
                        return
            if do_crash:
                l.info(f'do_crash specified and fallbock return code is not 0, crash attempt imminent')
                raise RuntimeError(f'For failed action [{action}] fallback [{fallback}] failed too')
