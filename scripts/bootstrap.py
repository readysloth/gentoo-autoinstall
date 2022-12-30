import os
import glob
import shutil
import logging
import urllib.request as ur

from entity import Action, Executor

import common
import build_logger


def _compile_qemu_wrapper():
    with open('qemu-wrapper.c', 'w') as f:
        f.write("""
#include <string.h>
#include <unistd.h>

#define ADDITIONAL_ARGS 5

int main(int argc, char **argv, char **envp) {{
    char *newargv[argc + ADDITIONAL_ARGS];

    newargv[0] = argv[0];
    newargv[1] = "-L";
    newargv[2] = "{}";
    newargv[3] = "-cpu";
    newargv[4] = "cortex-a53"; /* here you can set the cpu you are building for */

    memcpy(&newargv[ADDITIONAL_ARGS], &argv[1], sizeof(*argv)*(argc-1));
    newargv[argc + ADDITIONAL_ARGS - 2] = NULL;
    return execve("/usr/bin/qemu-aarch64", newargv, envp);
}}
""".format(common.TARGET_ROOT))
    Executor.exec(Action('gcc -static qemu-wrapper.c -O2 -s -o qemu-wrapper',
                         name='qemu wrapper compilation'))


def qemu_setup():
    arch = 'aarch64'
    binfmt_register = ':'.join([f':{arch}',
                                r'M',
                                r':\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\xb7\x00',
                                r'\xff\xff\xff\xff\xff\xff\xff\xfc\xff\xff\xff\xff\xff\xff\xff\xff\xfe\xff\xff\xff',
                                f'{os.getcwd()}/qemu-wrapper:'])
    binary_setup = [Action(f'echo -1 > /proc/sys/fs/binfmt_misc/{arch}',
                           name=f'binfmt {arch} unregister'),
                    Action(f'echo "{binfmt_register}" > /proc/sys/fs/binfmt_misc/register',
                           name='binfmt qemu-wrapper register')]
    for a in binary_setup:
        Executor.exec(a)

    _compile_qemu_wrapper()
