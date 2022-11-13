import logging
import argparse

import common

from entity import init_executor, deinit_executor

import packages as pkg


def parse_args():
    parser = argparse.ArgumentParser(description='Gentoo bin builder')
    subparsers = parser.add_subparsers(dest='subparser_name')

    build_parser = subparsers.add_parser('build', help='build options')
    build_parser.add_argument('target', help='ARCHITECTURE-VENDOR-OS-LIBC target from crossdev')
    build_parser.add_argument('-n', '--dry-run',
                              action='store_true',
                              help='pretend to install, do nothing actually')
    # TODO: https://dilfridge.blogspot.com/2021/09/experimental-binary-gentoo-package.html
    build_parser.add_argument('-v', '--verbose',
                              action='store_true',
                              help='enable debug logging')
    build_parser.add_argument('-u', '--use-flags',
                              default=[],
                              nargs='+',
                              help='system-wide use flags')
    build_parser.add_argument('-t', '--no-gui',
                              action='store_true',
                              help='install only terminal packages')
    build_parser.add_argument('-T', '--no-wm',
                              action='store_true',
                              help='install only terminal packages and X server')
    build_parser.add_argument('-r', '--resume',
                              action='store_true',
                              help='executed.actions file for installation resume')
    build_parser.add_argument('-f', '--tmpfs',
                              help='tmpfs size for faster installation')
    build_parser.add_argument('-q', '--quirks',
                              default=[],
                              nargs='+',
                              help='install quirks')
    build_parser.add_argument('-e', '--features',
                              default=[],
                              nargs='+',
                              help='install features')

    info_parser = subparsers.add_parser('info', help='information')
    info_parser.add_argument('--list-quirks',
                             action='store_true',
                             help='list awailable install quirks')
    info_parser.add_argument('--list-features',
                             action='store_true',
                             help='list awailable install features')

    build_args = parser.parse_args()

    if build_args.subparser_name == 'info':
        if build_args.list_quirks:
            for q in common.QUIRKS:
                print('{} : {}'.format(*q))
        if build_args.list_features:
            for f in common.FEATURES:
                print('{} : {}'.format(*f))
        exit(0)

    if build_args.subparser_name == 'build':
        common.TARGET = args.target
        common.TARGET_ROOT = f'/usr/{args.target}'
        common.MAKE_CONF_PATH = f'{common.TARGET_ROOT}/{common.MAKE_CONF_PATH}'

        common.DRY_RUN = build_args.dry_run
        if build_args.verbose:
            common.LOGGER_LEVEL = logging.DEBUG

        if not build_args.no_gui or build_args.no_wm:
            build_args.use_flags.append('X')
            if build_args.no_wm:
                pkg.PACKAGE_LIST += pkg.X_SERVER_PACKAGE_LIST + pkg.X_PACKAGE_LIST
            else:
                pkg.PACKAGE_LIST += pkg.X_SERVER_PACKAGE_LIST \
                                    + pkg.X_WM_PACKAGE_LIST \
                                    + pkg.X_PACKAGE_LIST

        quirks = {}
        common.ENABLED_QUIRKS = set(build_args.quirks)
        for q, _ in common.QUIRKS:
            quirks[q] = q in common.ENABLED_QUIRKS

        features = {}
        common.ENABLED_FEATURES = set(build_args.features)
        for q, _ in common.FEATURES:
            features[q] = q in common.ENABLED_FEATURES


        if build_args.resume:
            common.RESUME = True
            common.EXECUTED_ACTIONS_FILENAME = build_args.resume
        if build_args.tmpfs:
            common.TMPFS_SIZE = build_args.tmpfs
    return build_args, quirks, features


args, quirks, features = parse_args()


import build_logger
import system_conf as sc

l = logging.getLogger(__name__)

init_executor()


sc.add_common_flags_to_make_conf(additional_use_flags=args.use_flags,
                                 delay_performance_tweaks=quirks['delay-performance'])
sc.process_quirks(quirks)
sc.process_features(features)

l.checkpoint('Package install started')
failed_packages, failed_actions = sc.build_packages()
l.checkpoint('Package install ended')
l.warning(f'{failed_packages} packages failed to install')
l.warning(f'{failed_actions} actions failed to execute')

deinit_executor()
