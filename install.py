import logging
import argparse

import common
import partitioning as p
import bootstrap as b
import system_install as si


def parse_args():
    parser = argparse.ArgumentParser(description='Gentoo workspace installer')
    parser.add_argument('disk', help='dev node to install gentoo')
    parser.add_argument('-n', '--dry-run',
                        action='store_true',
                        help='pretend to install, do nothing actually')
    parser.add_argument('-b', '--prefer-binary',
                        action='store_true',
                        help='prefer binary packages to source')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='enable debug logging')
    parser.add_argument('-p', '--cpu',
                        const='amd64',
                        nargs='?',
                        help='cpu architecture')
    parser.add_argument('-i', '--init',
                        const='openrc',
                        nargs='?',
                        help='init system')
    parser.add_argument('-u', '--use-flags',
                        default=[],
                        nargs='+',
                        help='system-wide use flags')
    parser.add_argument('-t', '--no-gui',
                        action='store_true',
                        help='install only terminal packages')
    parser.add_argument('-T', '--no-wm',
                        action='store_true',
                        help='install only terminal packages and X server')

    install_args = parser.parse_args()

    common.DRY_RUN = install_args.dry_run
    if install_args.verbose:
        common.LOGGER_LEVEL = logging.DEBUG

    if not install_args.no_gui:
        install_args.use_flags.append('X')
    return install_args


def partition_disk(disk):
    p.prepare_for_partitioning(disk)
    bootloader_part, lvm_part = p.part_disk(disk)
    p.create_lvm_partition(bootloader_part, lvm_part)
    p.prepare_for_os_install()


args = parse_args()

partition_disk(args.disk)
b.bootstrap(processor=args.cpu, init=args.init)
si.add_common_flags_to_make_conf(additional_use_flags=args.use_flags)
si.setup_portage()
