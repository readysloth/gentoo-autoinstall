import multiprocessing as mp

import common
from entity import Action, Executor
from packages import PACKAGE_LIST


def add_common_flags_to_make_conf(additional_use_flags='', prefer_binary=False):
    if type(additional_use_flags) != str:
        additional_use_flags = ' '.join(additional_use_flags)

    emerge_binary_opt = '--getbinpkgonly' if prefer_binary else ''

    common.add_value_to_string_variable(common.MAKE_CONF_PATH, 'COMMON_FLAGS', '-pipe -march=native')
    common.add_variable_to_file(common.MAKE_CONF_PATH, 'ACCEPT_LICENSE', '*')
    common.add_variable_to_file(common.MAKE_CONF_PATH, 'FEATURES', 'parallel-install parallel-fetch')
    common.add_variable_to_file(common.MAKE_CONF_PATH, 'USE', f'lto pgo openmp {additional_use_flags}')
    common.add_variable_to_file(common.MAKE_CONF_PATH, 'EMERGE_DEFAULT_OPTS', f'--jobs={mp.cpu_count() // 3 + 1} {emerge_binary_opt}')
    common.add_variable_to_file(common.MAKE_CONF_PATH, 'ACCEPT_KEYWORDS', '~amd64 amd64 x86')
    common.add_variable_to_file(common.MAKE_CONF_PATH, 'INPUT_DEVICES', 'synaptics libinput')
    common.add_variable_to_file(common.MAKE_CONF_PATH, 'GRUB_PLATFORMS', 'emu efi-32 efi-64 pc')


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
    Executor.exec(Action('echo "*/* $(cpuid2cpuflags)" > /etc/portage/package.use/00cpu-flags', name='setting cpu-flags'))


def install_packages():
    failed_count = 0
    for p in PACKAGE_LIST:
        if type(p) == tuple:
            Executor.exec(p[0], fallbacks=p[1], do_crash=True)
        else:
            Executor.exec(p)
            if not p.succeded:
                failed_count += 1
    return failed_count
