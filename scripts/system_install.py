import os
import multiprocessing as mp

import common
from entity import Action, Executor
from packages import (PACKAGE_LIST,
                      POST_INSTALL_CALLBACKS,
                      pre_install,
                      post_install,
                      execute_each_in)


def add_common_flags_to_make_conf(additional_use_flags='',
                                  prefer_binary=False,
                                  delay_performance_tweaks=False):
    if type(additional_use_flags) != str:
        additional_use_flags = ' '.join(additional_use_flags)

    emerge_binary_opt = ''
    if prefer_binary:
        emerge_binary_opt = '--binpkg-respect-use=y --getbinpkg=y'
        additional_use_flags += ' bindist'
        with open(common.BIN_CONF_PATH, 'w') as binrepos:
            binrepos.writelines(['[binhost]',
                                 'priority = 9999',
                                 'sync-uri = https://gentoo.osuosl.org/experimental/amd64/binpkg/default/linux/17.1/x86-64/'])

    def set_parallel_emerge():
        common.add_variable_to_file(common.MAKE_CONF_PATH,
                                    'EMERGE_DEFAULT_OPTS',
                                    f'--jobs={mp.cpu_count() // 3 + 1} {emerge_binary_opt}')
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

    common.add_value_to_string_variable(common.MAKE_CONF_PATH, 'COMMON_FLAGS', '-march=native')
    common.add_variable_to_file(common.MAKE_CONF_PATH, 'ACCEPT_LICENSE', '*')
    common.add_variable_to_file(common.MAKE_CONF_PATH, 'USE', f'python alsa opencl inotify lto pgo openmp zstd {additional_use_flags}')

    llvm_targets = ' '.join(['-AArch64', '-AMDGPU', '-ARM', '-AVR',
                             '-BPF', '-Hexagon', '-Lanai', '-Mips',
                             '-MSP430', '-NVPTX', '-PowerPC', '-RISCV',
                             '-Sparc', '-SystemZ', '-VE', '-XCore',
                             '-ARC', '-CSKY', '-LoongArch', '-M68k'
                             'WebAssembly', 'X86'])

    Executor.exec(Action(f'echo "*/* LLVM_TARGETS: {llvm_targets}" >> /etc/portage/package.use/global',
                         name='setting llvm targets'))
    common.add_variable_to_file(common.MAKE_CONF_PATH, 'PORTAGE_IONICE_COMMAND', r'ionice -c 3 -p \${PID}')
    common.add_variable_to_file(common.MAKE_CONF_PATH, 'ACCEPT_KEYWORDS', '~amd64 amd64 x86')
    common.add_variable_to_file(common.MAKE_CONF_PATH, 'INPUT_DEVICES', 'synaptics libinput')
    common.add_variable_to_file(common.MAKE_CONF_PATH, 'GRUB_PLATFORMS', 'emu efi-32 efi-64 pc')


def process_quirks(quirks):
    os.makedirs('/etc/portage/env', exist_ok=True)
    if quirks['notmpfs']:
        os.makedirs('/var/tmp/notmpfs', exist_ok=True)
        with open('/etc/portage/env/notmpfs.conf', 'w') as f:
            f.writelines([f'PORTAGE_TMPDIR="/var/tmp/notmpfs"'])

    if quirks['linker-tradeoff']:
        with open('/etc/portage/env/linker-tradeoff.conf', 'w') as f:
            f.writelines([r'LDFLAGS="${LDFLAGS} -Wl,--no-keep-memory"'])
    if quirks['half-nproc']:
        with open('/etc/portage/env/half-nproc.conf', 'w') as f:
            f.writelines([f'MAKEOPTS="-j{mp.cpu_count() // 2}"'])


def setup_portage():
    basic_setup_actions = [Action('emerge-webrsync', name='webrsync'),
                           Action('emerge --oneshot sys-apps/portage', name='portage update'),
                           Action('emerge app-portage/gentoolkit', name='gentoolkit install')]
    get_gentoo_profiles_action = Action('eselect profile list', name='gentoo profile list', nondestructive=True)

    for a in basic_setup_actions:
        Executor.exec(a, do_crash=True)
    Executor.exec(get_gentoo_profiles_action, do_crash=True)

    header_text = f'select profile, [{common.DEFAULT_GENTOO_PROFILE}] is the default'
    print(f'+{"-"*len(header_text)}+')
    print(f'|{header_text}|')
    print(f'+{"-"*len(header_text)}+')
    print(get_gentoo_profiles_action.value)
    select_profile_action = Action('read -t 20 CHOICE; echo $CHOICE', nondestructive=True)
    Executor.exec(select_profile_action)

    selected_profile = select_profile_action.value.strip()
    if selected_profile.isdigit():
        selected_profile = int(selected_profile)
    else:
        selected_profile = common.DEFAULT_GENTOO_PROFILE

    Executor.exec(Action(f'eselect profile set --force {selected_profile}', name='setting gentoo profile'))

    Executor.exec(Action('emerge app-portage/cpuid2cpuflags', name='emerging cpuid2cpuflags'))
    Executor.exec(Action('echo "*/* $(cpuid2cpuflags)" >> /etc/portage/package.use/global', name='setting cpu-flags'))


def system_boot_configuration():
    common.add_variable_to_file('/etc/default/grub', 'GRUB_CMDLINE_LINUX', 'dolvm')
    fstab_swap_action = Action('echo "UUID=$(blkid -t LABEL=swap -s UUID -o value) \t none \t swap \t sw \t 0 \t 0" >> /etc/fstab',
                               name='fstab alter with swap')
    fstab_rootfs_action = Action('echo "UUID=$(blkid -t LABEL=rootfs -s UUID -o value) \t / \t ext4 \t noatime \t 0 \t 1" >> /etc/fstab',
                                 name='fstab alter with rootfs')
    Executor.exec(fstab_swap_action)
    Executor.exec(fstab_rootfs_action)


def enable_zswap():
    text = '\n'.join(["echo lz4 > /sys/module/zswap/parameters/compressor"
                      "echo 1 > /sys/module/zswap/parameters/enabled"])
    with open('/etc/local.d/50-zswap.start', 'w') as f:
        f.write(text)


def install_packages(download_only_folder=None):
    pre_install()
    if download_only_folder:
        os.makedirs(download_only_folder, exist_ok=True)
        failed_packages_count = execute_each_in(PACKAGE_LIST, '--fetchonly')
        Executor.exec(Action(f'rsync -a /var/cache/distfiles/ {download_only_folder}',
                             name='syncing downloaded packages'))
    else:
        failed_packages_count = execute_each_in(PACKAGE_LIST)
    failed_actions_count = post_install()
    return (failed_packages_count, failed_actions_count)
