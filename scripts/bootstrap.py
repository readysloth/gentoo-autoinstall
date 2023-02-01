import os
import glob
import shutil
import logging
import urllib.request as ur

from entity import Action, Executor

import common
import install_logger


MOUNTPOINT = '/mnt/gentoo'


def _compile_qemu_wrapper():
    with open('qemu-wrapper.c', 'w') as f:
        f.write("""
#include <string.h>
#include <unistd.h>

int main(int argc, char **argv, char **envp) {
    char *newargv[argc + 3];

    newargv[0] = argv[0];
    newargv[1] = "-cpu";
    newargv[2] = "cortex-a53"; /* here you can set the cpu you are building for */

    memcpy(&newargv[3], &argv[1], sizeof(*argv) * (argc -1));
    newargv[argc + 2] = NULL;
    return execve("/usr/bin/qemu-aarch64", newargv, envp);
}
""")
    Executor.exec(Action('gcc -static qemu-wrapper.c -O2 -s -o qemu-wrapper',
                         name='qemu wrapper compilation'))


def _launch_ntpd():
    Executor.exec(Action('ntpd -q -g', name='time syncing'), do_crash=True)


def _stage3_download(processor='arm64',
                     init='openrc',
                     desktop=False,
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

    l.info(f'Downloading {distro_location_file.replace(".txt", "")}')

    distro_location_data = map(bytes.decode, ur.urlopen(f'{site}/{folder}/{distro_location_file}').readlines())
    distro_path_line = next((l for l in distro_location_data if not l.startswith('#')))
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


def _binhost_setup():
    arch = 'aarch64'
    binfmt_register = ':'.join([f':{arch}',
                                r'M',
                                r':\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\xb7\x00',
                                r'\xff\xff\xff\xff\xff\xff\xff\xfc\xff\xff\xff\xff\xff\xff\xff\xff\xfe\xff\xff\xff',
                                r'/qemu-wrapper:'])
    binary_setup = [Action(f'echo -1 > /proc/sys/fs/binfmt_misc/{arch}',
                           name=f'binfmt {arch} unregister'),
                    Action(f'echo "{binfmt_register}" > /proc/sys/fs/binfmt_misc/register',
                           name='binfmt qemu-wrapper register')]
    for a in binary_setup:
        Executor.exec(a)

    Executor.exec(Action('emerge --usepkgonly --oneshot --nodeps qemu',
                         env={'ROOT': MOUNTPOINT},
                         name='usermode qemu setup'))
    _compile_qemu_wrapper()
    shutil.copy('qemu-wrapper', MOUNTPOINT)


def _final_bootstrap_configuration():
    repos_path = '/var/db/repos/gentoo'
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
                     Action(f'mount --make-rslave       {MOUNTPOINT}/dev', name='enslaving virtual fs'),
                     Action(f'mkdir -p {MOUNTPOINT}{repos_path}', name='creating path for binding repos'),
                     Action(f'mount --bind {repos_path} {MOUNTPOINT}{repos_path}', name='binding repos')]
    for a in final_actions:
        Executor.exec(a, do_crash=True)
    _binhost_setup()


def _chroot_to_mnt():
    if common.DRY_RUN:
        return
    scripts = list(glob.glob('*.sh')
                   + glob.glob('*.py')
                   + glob.glob('*.config')
                   + glob.glob('*.patch')
                   + glob.glob('*.cmd'))
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


def bootstrap(processor='arm64', init='openrc'):
    l = logging.getLogger(__name__)
    _launch_ntpd()
    stage3_archive = _stage3_download(processor=processor, init='openrc')
    _unpack(stage3_archive)
    _mirrorselect()
    _final_bootstrap_configuration()
    _chroot_to_mnt()
    l.checkpoint(f'Chrooted to {MOUNTPOINT}')
