import os
import time
import asyncio
import logging
import hashlib
import threading as t
import functools as ft
import subprocess as sp

from abc import ABC

import common
import build_logger


class Action:
    exec_counter = 0

    def __init__(self,
                 cmd,
                 name='-unnamed-',
                 env=None,
                 nondestructive=False,
                 pre=None,
                 post=None,
                 in_background=False):
        Action.exec_counter += 1

        self.cmd = cmd
        self.env = env or {}
        self.name = name[:100]
        self.nondestructive = nondestructive
        self.proc = None
        self.succeded = False
        self.value = ''
        self.pre = pre
        self.post = post
        self.in_background = in_background
        self.action_id = Action.exec_counter


    def __call__(self, *append):
        if common.DRY_RUN and not self.nondestructive:
            self.succeded = True
            return self

        l = logging.getLogger(__name__)

        if self.pre:
            l.debug('Executing pre-function')
            self.pre()

        with open('taken-actions.sh', 'a') as f:
            f.write(f'# {self.name}_{self.action_id}.stdout\n')
            f.write(f'# {self.name}_{self.action_id}.stderr\n')
            f.write(f'{self.cmd}\n')
        with open(f'{self.name}_{self.action_id}.stdout', 'ab') as stdout_file, \
             open(f'{self.name}_{self.action_id}.stderr', 'ab') as stderr_file:
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
        if self.succeded and self.post:
            l.debug('Executing post-function')
            if self.in_background:
                t.Thread(target=self.post).start()
            else:
                self.post()

        try:
            with open(f'{self.name}_{self.action_id}.stdout', 'r') as stdout_file:
                self.value = stdout_file.read().strip()
                l.debug(f'[{self.name}] value = "{self.value}"')
        except FileNotFoundError as e:
            l.warn(f"Couldn't openen stdout file for [{self.name}], $PWD='{os.getcwd()}': {e}")
        return self


    def __str__(self):
        begin = f"{self.env} [{self.name}]({self.cmd})"
        if self.proc:
            return f"{begin} = {self.proc.returncode}"
        return begin


    def __hash__(self):
        return int(hashlib.md5((self.name + self.cmd + str(self.action_id)).encode()).hexdigest(), 16)


class Package(Action):
    def __init__(self,
                 package,
                 options='',
                 use_flags='',
                 possible_quirks=None,
                 merge_as_always=False,
                 **kwargs):
        self.package = package
        if use_flags is not None:
            if type(use_flags) == list:
                use_flags = ' '.join(use_flags)
        self.use_flags = use_flags
        self.options = f'--buildpkg {options}'
        self.emerge = f'emerge-wrapper --target {common.TARGET}'
        self.merge_as_always = merge_as_always
        if self.options:
            self.merge_as_always = True
        self.possible_quirks = possible_quirks or []
        self.cmd_template = 'emerge --autounmask-write {opts} {pkg} || (echo -5 | etc-update && emerge {opts} {pkg})'
        self.cmd = self.cmd_template.format(opts=self.options, pkg=self.package)

        if common.MERGE_EARLY and not self.merge_as_always:
            self.cmd = f'echo "{self.package}" >> {common.TARGET_ROOT}/var/lib/portage/world'

        try_cmd_template = f'{self.emerge} --autounmask-write {{opts}} {{pkg}}'
        catch_cmd_template = f'echo -5 | etc-update && {self.emerge} {{opts}} {{pkg}}'
        self.cmd_template = f'{try_cmd_template} || ({catch_cmd_template})'
        self.cmd = self.cmd_template.format(opts=self.options,
                                            pkg=self.package)
        super().__init__(self.cmd,
                         name=f'{package.replace("/", "_")}',
                         nondestructive=False,
                         **kwargs)


    def download(self):
        cmd = self.cmd_template.format(opts=f'--fetchonly {self.options}',
                                       pkg=self.package)
        download_action = Action(cmd,
                                 name=f'prefetch-{self.package.replace("/", "_")}',
                                 nondestructive=False)
        Executor.exec(download_action)


    def __call__(self, *append):
        l = logging.getLogger(__name__)
        use_file_name = self.package.replace('/', '.')
        if self.use_flags:
            with open(f'{common.TARGET_ROOT}/etc/portage/package.use/{use_file_name}', 'a') as use_flags_file:
                use_flags_file.write(f'{self.package} {self.use_flags}')

        l.debug(f'Possible quirks: [{self.possible_quirks}]')
        for q in self.possible_quirks:
            if q not in common.ENABLED_QUIRKS:
                continue
            l.debug(f'Quirk {q} enabled for {self.package}')
            with open(f'{common.TARGET_ROOT}/etc/portage/package.env', 'a') as f:
                f.write(f'{self.package} {q}.conf\n')

        l.debug(f'Installing {self.package}, USE="{self.use_flags}"')
        super().__call__(*append)
        if not self.succeded:
            l.warning(f'{self.package} install failed')
            with open('reinstall-failed.sh', 'a') as f:
                f.write(f'{self.cmd}\n')
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
        super().__init__('')


    def __call__(self, *append):
        for a in self.actions:
            Executor.exec(a, *append)
            if not a.succeded:
                self.succeded = False
        return self


    def __str__(self):
        return f"{self.name} -> {self.actions}"


    def __hash__(self):
        return int(hashlib.md5((str(self) + str(self.action_id)).encode()).hexdigest(), 16)


class ParallelActions(Action):
    def __init__(self, *actions, name='-unnamed-parallel-action-'):
        self.actions = actions
        self.name = name
        self.succeded = False
        super().__init__('')


    def __call__(self, *append):
        async def schedule():
            loop = asyncio.get_running_loop()
            tasks = [loop.run_in_executor(None, ft.partial(a, *append)) for a in self.actions]
            finished_tasks = await asyncio.gather(*tasks)
            return any((ft.succeded for ft in finished_tasks))

        self.succeded = asyncio.run(schedule())
        return self


    def __str__(self):
        return f"{self.name} || {self.actions}"


    def __hash__(self):
        return int(hashlib.md5((str(self) + str(self.action_id)).encode()).hexdigest(), 16)


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
            return

        l.info(f'Executing "{action.name}"')
        l.debug(f'Start of {action} + {list(args)}')
        action_started = datetime.now()
        ended_action = action(*args)
        action_ended = datetime.now()
        l.info(f'{common.Colors.GREEN}"{action.name}" took {action_ended - action_started}{common.Colors.ENDC}')

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
