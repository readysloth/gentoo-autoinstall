import os
import glob
import shutil
import logging
import urllib.request as ur

from entity import Action, Executor

import common
import install_logger


def _launch_ntpd():
    Executor.exec(Action('ntpd -q -g', name='time syncing'), do_crash=True)


def _stage3_download(processor='amd64',
                     init='openrc',
                     desktop=True,
                     hardened=False,
                     nomultilib=False,
                     musl=False):
    l = logging.getLogger(__name__)
    l.info('Preparing to download stage3 acrhive')
    if common.DRY_RUN:
        return ''
    site = 'https://mirror.yandex.ru'
    folder = f'gentoo-distfiles/releases/{processor}/autobuilds'
    distro_location_file = f'latest-stage3-{processor}'
    if desktop:
        distro_location_file += '-desktop'
    if hardened:
        distro_location_file += '-hardened'
    if nomultilib:
        distro_location_file += '-nomultilib'
    if musl:
        distro_location_file += '-musl'
    distro_location_file += f'-{init}.txt'

    l.info(f'Will download {distro_location_file.replace(".txt", "")}')

    distro_location_data = map(bytes.decode, ur.urlopen(f'{site}/{folder}/{distro_location_file}').readlines())
    distro_path_line = next((l for l in distro_location_data if not l.startswith('#')))
    distro_path = distro_path_line.split()[0]
    filename = 'stage3'
    ur.urlretrieve(f'{site}/{folder}/{distro_path}', filename)
    l.checkpoint(f'Stage3 archive is downloaded!')
    return filename


def _unpack(stage3_archive):
    Executor.exec(Action(f'tar xpf {stage3_archive} --xattrs-include="*.*" --numeric-owner -C /mnt/gentoo',
                         name='stage3 archive extraction'), do_crash=True)


def _mirrorselect():
    Executor.exec(Action(f'mirrorselect -4 -D', name='mirrorselect'), do_crash=True)


def _final_bootstrap_configuration():
    final_actions = [Action('mkdir -p etc/portage/repos.conf', name='creating repos.conf folder'),
                     Action('cp usr/share/portage/config/repos.conf etc/portage/repos.conf/gentoo.conf',
                            name='copying repos.conf'),
                     Action('cp --dereference /etc/resolv.conf etc/', name='copying resolv.conf'),
                     Action('mount --types proc  /proc proc', name='mounting virtual fs'),
                     Action('mount --rbind       /sys  sys', name='binding virtual fs'),
                     Action('mount --make-rslave       sys', name='enslaving virtual fs'),
                     Action('mount --rbind       /dev  dev', name='binding virtual fs'),
                     Action('mount --make-rslave       dev', name='enslaving virtual fs')]
    for a in final_actions:
        Executor.exec(a, do_crash=True)


def _chroot_to_mnt():
    if common.DRY_RUN:
        return
    scripts = glob.glob('*.sh') + glob.glob('*.py')
    for script in scripts:
        shutil.copy(script, '/mnt/gentoo')
    os.chroot('/mnt/gentoo')
    os.chdir('/')


def bootstrap(processor='amd64', init='openrc'):
    l = logging.getLogger(__name__)
    _launch_ntpd()
    stage3_archive = _stage3_download(processor='amd64', init='openrc')
    _unpack(stage3_archive)
    _mirrorselect()
    _final_bootstrap_configuration()
    if not common.DRY_RUN:
        os.remove(stage3_archive)
    _chroot_to_mnt()
    l.checkpoint('Chrooted to /mnt/gentoo')
