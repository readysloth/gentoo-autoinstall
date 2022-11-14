import os
import multiprocessing as mp

import common
from entity import Action, Executor
from packages import (PACKAGE_LIST,
                      POST_INSTALL_CALLBACKS,
                      MASKS,
                      pre_install,
                      post_install,
                      execute_each_in)


def add_common_flags_to_make_conf(additional_use_flags='',
                                  delay_performance_tweaks=False):
    if type(additional_use_flags) != str:
        additional_use_flags = ' '.join(additional_use_flags)

    emerge_binary_opt = ''

    def set_parallel_emerge():
        mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
        mem_gib = mem_bytes//(1024**3)
        emerge_jobs = int(mem_gib // 1.5) # concurrent emerge jobs heuristics

        common.add_variable_to_file(common.MAKE_CONF_PATH,
                                    'EMERGE_DEFAULT_OPTS',
                                    f'--jobs={emerge_jobs} {emerge_binary_opt}')
        common.add_variable_to_file(common.MAKE_CONF_PATH,
                                    'FEATURES',
                                    'parallel-install parallel-fetch')
    if delay_performance_tweaks:
        # to save RAM
        POST_INSTALL_CALLBACKS.append(set_parallel_emerge)
        common.remove_variable_value(common.MAKE_CONF_PATH, 'COMMON_FLAGS', '-pipe')
        POST_INSTALL_CALLBACKS.append(lambda: common.add_variable_to_file(common.MAKE_CONF_PATH,
                                                                          'COMMON_FLAGS',
                                                                          '-pipe'))
    else:
        set_parallel_emerge()

    common.add_variable_to_file(common.MAKE_CONF_PATH, 'ACCEPT_LICENSE', '*')
    default_useflags = ' '.join(['python', 'alsa', 'opencl',
                                 'inotify', 'lto', 'pgo',
                                 'openmp', 'zstd', 'jumbo-build',
                                 '-wayland', '-gnome-online-accounts', '-npm',
                                 'jit', 'threads', 'gpm',
                                 'minimal', 'ssl'])
    common.add_variable_to_file(common.MAKE_CONF_PATH, 'USE', f'${{USE}} {default_useflags} {additional_use_flags}')
    common.add_variable_to_file(common.MAKE_CONF_PATH, 'PORTAGE_IONICE_COMMAND', r'ionice -c 3 -p \${PID}')
    common.add_variable_to_file(common.MAKE_CONF_PATH, 'INPUT_DEVICES', 'synaptics libinput')
    os.makedirs(f'{common.TARGET_ROOT}/etc/portage/package.use/', exist_ok=True)


def process_quirks(quirks):
    os.makedirs(f'{common.TARGET_ROOT}/etc/portage/env', exist_ok=True)
    os.makedirs(f'{common.TARGET_ROOT}/etc/portage/profile/', exist_ok=True)

    if quirks['notmpfs']:
        os.makedirs(f'{common.TARGET_ROOT}/var/tmp/notmpfs', exist_ok=True)
        with open(f'{common.TARGET_ROOT}/etc/portage/env/notmpfs.conf', 'w') as f:
            f.writelines([f'PORTAGE_TMPDIR="{common.TARGET_ROOT}/var/tmp/notmpfs"'])
    if quirks['linker-tradeoff']:
        with open(f'{common.TARGET_ROOT}/etc/portage/env/linker-tradeoff.conf', 'w') as f:
            f.writelines([r'LDFLAGS="${LDFLAGS} -Wl,--no-keep-memory"'])
    if quirks['half-nproc']:
        with open(f'{common.TARGET_ROOT}/etc/portage/env/half-nproc.conf', 'w') as f:
            f.writelines([f'MAKEOPTS="-j{mp.cpu_count() // 2}"'])
    if quirks['less-llvm']:
        llvm_targets = ' '.join(['AArch64', '-AMDGPU', '-ARM', '-AVR',
                                 '-BPF', '-Hexagon', '-Lanai', '-Mips',
                                 '-MSP430', '-NVPTX', '-PowerPC', '-RISCV',
                                 '-Sparc', '-SystemZ', '-VE', '-XCore',
                                 '-ARC', '-CSKY', '-LoongArch', '-M68k',
                                 '-WebAssembly', '-X86'])
        Executor.exec(Action(f'echo "*/* LLVM_TARGETS: {llvm_targets}" >> {common.TARGET_ROOT}/etc/portage/profile/package.use.force',
                             name='setting llvm targets'))
        # upstream version based on zig, which fails to compile with use flags above
        MASKS.append('>sys-fs/ncdu-1.17')


def process_features(features):
    if features['no-tty-ctrl-alt-del']:
        Executor.exec(Action('sed -i "/ctrlaltdel/ s/.*/#&/" /etc/inittab',
                             name='removing ctrl-alt-del reboot'))


def build_packages():
    pre_install()
    failed_packages_count = execute_each_in(PACKAGE_LIST)
    failed_actions_count = post_install()
    return (failed_packages_count, failed_actions_count)
