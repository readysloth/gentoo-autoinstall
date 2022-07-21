import os
import logging
import subprocess as sp

from abc import ABC

import common
import install_logger


class Action:
    def __init__(self, cmd, name='-unnamed-', env=None, nondestructive=False):
        self.cmd = cmd
        self.env = env or {}
        self.name = name
        self.nondestructive = nondestructive
        self.proc = None
        self.succeded = False
        self.value = ''


    def __call__(self, *append):
        if common.DRY_RUN and not self.nondestructive:
            self.succeded = True
            return self

        self.proc = sp.Popen(f'{self.cmd} {" ".join(append)}',
                             shell=True,
                             env={**os.environ, **self.env},
                             stdout=sp.PIPE,
                             stderr=sp.PIPE)
        self.proc.wait()
        self.succeded = self.proc.returncode == 0
        self.value = self.proc.stdout.read().decode()
        return self


    def report(self):
        if self.proc:
            with open(self.name, 'ab') as f:
                f.write(str(self).encode() + b'\n')
                f.write(b'-----BEGIN STDOUT-----\n')
                f.write(self.proc.stdout.read()+b'\n')
                f.write(b'-----END STDOUT-----\n')
                f.write(b'-----BEGIN STDERR-----\n')
                f.write(self.proc.stderr.read()+b'\n')
                f.write(b'-----END STDERR-----\n')


    def __str__(self):
        begin = f"{self.env} [{self.name}]({self.cmd})"
        if self.proc:
            return f"{begin} = {self.proc.returncode}"
        return begin


class Package(Action):
    def __init__(self, package, options, use_flags=None):
        self.package = package
        if use_flags is not None:
            if type(use_flags) == list:
                use_flags = ' '.join(use_flags)
        super().__init__(f'emerge {options} {package}',
                         name=f'{package.sub("/", "_")}',
                         env={'USE': use_flags},
                         nondestructive=False)


    def __call__(self, *append):
        use_file_name = self.package.replace('/', '.')
        with open(f'/etc/portage/package.use/{use_file_name}', 'a') as use_flags_file:
            use_flags_file.write(f'{self.package} {self.env["USE"]}')
        super().__call__(*append)


class Executor(ABC):
    @staticmethod
    def exec(action, *args, fallbacks=None, do_crash=False):
        l = logging.getLogger(__name__)
        l.info(f'Executing "{action.name}"')
        l.debug(f'Start of {action} + {list(args)}')
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
                l.info(f'do_crash specified and fallback return code is not 0, crash attempt imminent')
                raise RuntimeError(f'For failed [{action}] every specified fallback failed too')
