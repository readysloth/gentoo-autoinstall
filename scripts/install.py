import logging
import argparse

import common

from entity import init_executor, deinit_executor

import packages as pkg

def parse_args():
    parser = argparse.ArgumentParser(description='Gentoo workspace installer')
    subparsers = parser.add_subparsers(dest='subparser_name')

    install_parser = subparsers.add_parser('install', help='install options')

    install_parser.add_argument('disk', help='dev node to install gentoo')
    install_parser.add_argument('-n', '--dry-run',
                                action='store_true',
                                help='pretend to install, do nothing actually')
    # TODO: https://dilfridge.blogspot.com/2021/09/experimental-binary-gentoo-package.html
    install_parser.add_argument('-b', '--prefer-binary',
                                action='store_true',
                                help='prefer binary packages to source')
    install_parser.add_argument('-v', '--verbose',
                                action='store_true',
                                help='enable debug logging')
    install_parser.add_argument('-c', '--cpu',
                                default='amd64',
                                nargs='?',
                                help='cpu architecture')
    install_parser.add_argument('-i', '--init',
                                default='openrc',
                                nargs='?',
                                help='init system')
    install_parser.add_argument('-u', '--use-flags',
                                default=[],
                                nargs='+',
                                help='system-wide use flags')
    install_parser.add_argument('-t', '--no-gui',
                                action='store_true',
                                help='install only terminal packages')
    install_parser.add_argument('-T', '--no-wm',
                                action='store_true',
                                help='install only terminal packages and X server')
    install_parser.add_argument('-p', '--no-packages',
                                action='store_true',
                                help='do not install any supplied packages')
    install_parser.add_argument('-H', '--hostname',
                                default='gentoo',
                                nargs='?',
                                help='OS hostname')
    install_parser.add_argument('-U', '--user',
                                default='user',
                                nargs='?',
                                help='user name')
    install_parser.add_argument('-r', '--resume',
                                action='store_true',
                                help='executed.actions file for installation resume')
    install_parser.add_argument('-d', '--download-packages-only',
                                help='folder for packages')
    install_parser.add_argument('-f', '--tmpfs',
                                help='tmpfs size for faster installation')
    install_parser.add_argument('-a', '--aria2',
                                action='store_true',
                                help='use aria2 as FETCHCOMMAND instead of wget')
    install_parser.add_argument('-q', '--quirks',
                                default=[],
                                nargs='+',
                                help='install quirks')
    install_parser.add_argument('-e', '--features',
                                default=[],
                                nargs='+',
                                help='install features')
    install_parser.add_argument('-m', '--merge-early',
                                action='store_true',
                                help='add all needed packages to world file, then make world update')


    info_parser = subparsers.add_parser('info', help='information')

    info_parser.add_argument('--list-quirks',
                             action='store_true',
                             help='list awailable install quirks')
    info_parser.add_argument('--list-features',
                             action='store_true',
                             help='list awailable install features')

    install_args = parser.parse_args()

    if install_args.subparser_name == 'info':
        if install_args.list_quirks:
            for q in common.QUIRKS:
                print('{} : {}'.format(*q))
        if install_args.list_features:
            for f in common.FEATURES:
                print('{} : {}'.format(*f))
        exit(0)

    if install_args.subparser_name == 'install':
        common.DRY_RUN = install_args.dry_run
        if install_args.verbose:
            common.LOGGER_LEVEL = logging.DEBUG

        if not install_args.no_gui or install_args.no_wm:
            install_args.use_flags.append('X')
            if install_args.no_wm:
                pkg.PACKAGE_LIST += pkg.X_SERVER_PACKAGE_LIST + pkg.X_PACKAGE_LIST
            else:
                pkg.PACKAGE_LIST += pkg.X_SERVER_PACKAGE_LIST \
                                    + pkg.X_WM_PACKAGE_LIST \
                                    + pkg.X_PACKAGE_LIST

        quirks = {}
        common.ENABLED_QUIRKS = set(install_args.quirks)
        for q, _ in common.QUIRKS:
            quirks[q] = q in common.ENABLED_QUIRKS

        features = {}
        common.ENABLED_FEATURES = set(install_args.features)
        for q, _ in common.FEATURES:
            features[q] = q in common.ENABLED_FEATURES


        if install_args.resume:
            common.RESUME = True
            common.EXECUTED_ACTIONS_FILENAME = install_args.resume
        if install_args.tmpfs:
            common.TMPFS_SIZE = install_args.tmpfs
        common.USE_ARIA2 = install_args.aria2
        common.MERGE_EARLY = install_args.merge_early

    return install_args, quirks, features


def partition_disk(disk):
    p.prepare_for_partitioning(disk)
    bootloader_part, lvm_part = p.part_disk(disk)
    p.create_lvm_partition(bootloader_part, lvm_part)
    p.prepare_for_os_install()
    return bootloader_part


args, quirks, features = parse_args()

import install_logger
import partitioning as p
import bootstrap as b
import system_install as si

l = logging.getLogger(__name__)

init_executor()


bootloader_part = partition_disk(args.disk)
l.checkpoint(f'Partitioned {args.disk}')
b.bootstrap(processor=args.cpu, init=args.init)
l.checkpoint(f'Bootstrapped for further install')
si.add_common_flags_to_make_conf(additional_use_flags=args.use_flags,
                                 prefer_binary=args.prefer_binary,
                                 delay_performance_tweaks=quirks['delay-performance'])
si.process_quirks(quirks)
si.process_features(features)
si.setup_portage()
l.checkpoint(f'Set up portage')
si.system_boot_configuration(bootloader_part)
l.checkpoint(f'Set up boot configuration')
si.enable_zswap()
si.create_user(args.user)

if not args.no_packages:
    l.checkpoint(f'Package install started')
    failed_packages, failed_actions = si.install_packages(args.download_packages_only)
    l.checkpoint(f'Package install ended')
    l.warning(f'{failed_packages} packages failed to install')
    l.warning(f'{failed_actions} actions failed to execute')


with open('/etc/conf.d/hostname', 'w') as f:
    f.write(f'hostname="{args.hostname}"')

l.checkpoint('Installation is finished!')
l.checkpoint(f'Do not forget to do `passwd {args.user}` to set user password')

deinit_executor()
