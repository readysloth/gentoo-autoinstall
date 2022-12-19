import os
import logging
import argparse

import common

from entity import init_executor, deinit_executor, Action, Executor


def parse_args():
    parser = argparse.ArgumentParser(description='Gentoo bin builder')
    subparsers = parser.add_subparsers(dest='subparser_name')

    build_parser = subparsers.add_parser('build', help='build options')
    build_parser.add_argument('target', help='ARCHITECTURE-VENDOR-OS-LIBC target from crossdev')
    build_parser.add_argument('-n', '--dry-run',
                              action='store_true',
                              help='pretend to build, do nothing actually')
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
                              help='build only terminal packages')
    build_parser.add_argument('-r', '--resume',
                              action='store_true',
                              help='executed.actions file for build resume')
    build_parser.add_argument('-f', '--tmpfs',
                              help='tmpfs size for faster build')
    build_parser.add_argument('-q', '--quirks',
                              default=[],
                              nargs='+',
                              help='build quirks')
    build_parser.add_argument('-e', '--features',
                              default=[],
                              nargs='+',
                              help='build features')
    build_parser.add_argument('-m', '--merge-early',
                              action='store_true',
                              help='add all needed packages to world file, then make world update')

    info_parser = subparsers.add_parser('info', help='information')
    info_parser.add_argument('--list-quirks',
                             action='store_true',
                             help='list available build quirks')
    info_parser.add_argument('--list-features',
                             action='store_true',
                             help='list available build features')

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
        common.TARGET = build_args.target
        common.TARGET_ROOT = f'/usr/{common.TARGET}'
        common.MAKE_CONF_PATH = f'{common.TARGET_ROOT}/{common.MAKE_CONF_PATH}'

        common.DRY_RUN = build_args.dry_run
        if build_args.verbose:
            common.LOGGER_LEVEL = logging.DEBUG

        if build_args.no_gui:
            build_args.use_flags.append('-X')
        else:
            build_args.use_flags.append('X')

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
        common.MERGE_EARLY = build_args.merge_early
    return build_args, quirks, features


args, quirks, features = parse_args()


import build_logger
import system_conf as sc

l = logging.getLogger(__name__)

init_executor()

Executor.exec(Action(f'yes | crossdev --clean -t {common.TARGET} && crossdev -t {common.TARGET}',
                     name='crossdev init'))
Executor.exec(Action(f'emerge-wrapper --target {common.TARGET} --init', name='cross-emerge init'),)
os.environ.update({'PORTAGE_CONFIGROOT': common.TARGET_ROOT})

sc.select_profile()
sc.add_common_flags_to_make_conf(additional_use_flags=args.use_flags,
                                 delay_performance_tweaks=quirks['delay-performance'])
sc.process_quirks(quirks)
sc.process_features(features)

l.checkpoint('Package build started')
failed_packages, failed_actions = sc.build_packages()
l.checkpoint('Package build ended')
l.warning(f'{failed_packages} packages failed to build')
l.warning(f'{failed_actions} actions failed to execute')

deinit_executor()
