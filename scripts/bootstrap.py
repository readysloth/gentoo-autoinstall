import os
import glob
import shutil
import logging
import urllib.request as ur

from entity import Action, Executor

import common
import install_logger


MOUNTPOINT = '/mnt/gentoo'


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
    distro_prefix = 'latest-stage3'
    distro_type = ''
    if desktop:
        distro_type = 'desktop'
    if hardened:
        distro_type = 'hardened'
    if nomultilib:
        distro_type = 'nomultilib'
    if musl:
        distro_type = 'musl'
    distro_isoname = f'{distro_prefix}-{processor}-{distro_type}-{init}'

    l.info(f'Downloading {distro_isoname}')

    distro_location_data = map(bytes.decode, ur.urlopen(f'{site}/{folder}/{distro_isoname}.txt').readlines())
    distro_path_line = next((l for l in distro_location_data if f'{processor}-{distro_type}-{init}' in l))
    distro_path = distro_path_line.split()[0]
    filename = 'stage3'
    ur.urlretrieve(f'{site}/{folder}/{distro_path}', filename)
    l.checkpoint(f'Stage3 archive is downloaded!')

    with open('taken-actions.sh', 'a') as f:
        f.write(f'wget {site}/{folder}/{distro_path} -o {filename}\n')
    return filename


def _unpack(stage3_archive):
    Executor.exec(Action(f'tar xpf {stage3_archive} --xattrs-include="*.*" --numeric-owner -C {MOUNTPOINT}',
                         name='stage3 archive extraction'), do_crash=True)
    Executor.exec(Action(f'rm -f {stage3_archive}', name='removal of stage3 archive'))


def _mirrorselect():
    Executor.exec(Action(f'mirrorselect -s{common.MIRROR_COUNT} -4 -D', name='mirrorselect'), do_crash=True)


def _final_bootstrap_configuration():
    final_actions = [Action(f'mkdir -p {MOUNTPOINT}/etc/portage/repos.conf', name='creating repos.conf folder'),
                     Action(f'cp /usr/share/portage/config/repos.conf {MOUNTPOINT}/etc/portage/repos.conf/gentoo.conf',
                            name='copying repos.conf'),
                     Action(f'cp --dereference /etc/resolv.conf {MOUNTPOINT}/etc/', name='copying resolv.conf'),
                     Action(f'mount --types proc  /proc {MOUNTPOINT}/proc', name='mounting virtual fs'),
                     Action(f'mount --rbind       /sys  {MOUNTPOINT}/sys', name='binding virtual fs'),
                     Action(f'mount --make-rslave       {MOUNTPOINT}/sys', name='enslaving virtual fs'),
                     Action(f'mount --rbind       /run  {MOUNTPOINT}/run', name='binding virtual fs'),
                     Action(f'mount --make-rslave       {MOUNTPOINT}/run', name='enslaving virtual fs'),
                     Action(f'mount --rbind       /dev  {MOUNTPOINT}/dev', name='binding virtual fs'),
                     Action(f'mount --make-rslave       {MOUNTPOINT}/dev', name='enslaving virtual fs')]
    for a in final_actions:
        Executor.exec(a, do_crash=True)


def _chroot_to_mnt():
    if common.DRY_RUN:
        return
    scripts = list(glob.glob('*.sh') + glob.glob('*.py'))
    for script in scripts:
        shutil.copy(script, MOUNTPOINT)
    if not os.path.isfile(f'{MOUNTPOINT}/{common.EXECUTED_ACTIONS_FILENAME}'):
        Executor.executed_actions_file.close()
        shutil.copy(common.EXECUTED_ACTIONS_FILENAME, MOUNTPOINT)
    os.chroot(MOUNTPOINT)
    os.chdir('/')

    with open('taken-actions.sh', 'a') as f:
        f.write(f'cp {" ".join(scripts)} {MOUNTPOINT}\n')
        f.write(f'chroot {MOUNTPOINT}\n')
    Executor.executed_actions_file = open(common.EXECUTED_ACTIONS_FILENAME, 'a')


def bootstrap(processor='amd64', init='openrc'):
    l = logging.getLogger(__name__)
    #_launch_ntpd()
    stage3_archive = _stage3_download(processor=processor, init=init)
    _unpack(stage3_archive)
    #_mirrorselect()
    _final_bootstrap_configuration()
    _chroot_to_mnt()
    l.checkpoint(f'Chrooted to {MOUNTPOINT}')
