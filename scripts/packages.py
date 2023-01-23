import os
import shutil
import logging
import threading as t
import itertools as it
import urllib.request as ur

import common
import install_logger

from pathlib import Path

from entity import Package, Action, MetaAction, Executor, ParallelActions


def reoder_packages_for_early_merge(pkg_list):
    def is_world(p):
        return p.package == '@world'

    def is_package(p):
        return type(p) == Package

    def is_normal_package(p):
        return is_package(p) and not is_world(p) and p.merge_as_always

    def is_bulk_package(p):
        return is_package(p) and not is_world(p) and not p.merge_as_always

    normal_merge_packages = [p for p in pkg_list if is_normal_package(p)]
    bulk_merge_packages = [p for p in pkg_list if is_bulk_package(p)]
    actions = [e for e in pkg_list if not is_package(e)]

    world_package = [p for p in pkg_list if is_package(p) and is_world(p)][0]
    world_package.options = f'{world_package.options} --keep-going'
    world_package.cmd = world_package.cmd_template.format(opts=world_package.options,
                                                          pkg=world_package.package)

    reordered_package_list = normal_merge_packages \
                             + actions \
                             + bulk_merge_packages \
                             + [world_package]
    return reordered_package_list


def exclude_from_world_rebuild(pkg_list):
    package_names = []
    world_rebuild_pkg = None

    is_parallel_action = lambda p: type(p) == ParallelActions
    is_not_parallel_action = lambda p: type(p) != ParallelActions

    parallel_action_containers = filter(is_parallel_action, pkg_list)
    normal_pkgs = filter(is_not_parallel_action, pkg_list)

    parallel_actions = it.chain.from_iterable((pa.actions for pa in parallel_action_containers))

    for pkg in filter(lambda p: type(p) == Package, it.chain(normal_pkgs, parallel_actions)):
        if pkg.package == '@world':
            world_rebuild_pkg = pkg
        elif pkg.package in ['sys-libs/ncurses',
                             'sys-apps/util-linux',
                             'sys-libs/gpm']:
            # we should build @world with this packages
            continue
        elif pkg.package.startswith('sys-'):
            package_names.append(pkg.package)

    world_rebuild_pkg.options = f'{world_rebuild_pkg.options} --exclude "{" ".join(package_names)}"'
    world_rebuild_pkg.cmd = world_rebuild_pkg.cmd_template.format(opts=world_rebuild_pkg.options,
                                                                  pkg=world_rebuild_pkg.package)


def move_kernel_src_to_tmpfs():
    if not common.TMPFS_SIZE:
        return
    kernel_sources = Path('/usr/src/linux')
    Executor.exec(Action(f'vmtouch -vft {kernel_sources}'))


def move_kernel_src_from_tmpfs():
    if not common.TMPFS_SIZE:
        return
    kernel_sources = Path('/usr/src/linux')
    Executor.exec(Action(f'vmtouch -vfe {kernel_sources}'))


MASKS = [
]

QUIRKED_PACKAGES = [
    Package('media-libs/libsndfile', use_flags='minimal', merge_as_always=True),
    Package('net-misc/aria2', use_flags='bittorent libuv ssh', merge_as_always=True),
    Package('dev-util/vmtouch', merge_as_always=True),
    Package('dev-perl/Locale-gettext', merge_as_always=True),
]


ESSENTIAL_PACKAGE_LIST = [
    # with global `gpm` use flag
    Package('app-shells/dash', merge_as_always=True),
    Package('sys-kernel/gentoo-sources', use_flags='symlink', merge_as_always=True),
    Package('sys-kernel/genkernel', merge_as_always=True),
    Package('sys-kernel/linux-firmware', merge_as_always=True),

    Package('@system', '-uDNv --usepkgonly', merge_as_always=True),
    Package('@world', '-uDNv --backtrack=100 --exclude="sys-devel/gcc"', merge_as_always=True),
    Package('sys-apps/portage', '-vND', use_flags='native-extensions ipc xattr'),
    Package('media-libs/libpng', use_flags='apng'),
    Package('app-editors/vim', use_flags='perl terminal lua'),
    Package('sys-apps/util-linux', use_flags='-logger'),
    Package('app-admin/sysklogd', use_flags='logger'),
    Package('sys-process/cronie'),


    Package('sys-boot/grub', use_flags='device-mapper mount'),
    Package('sys-apps/lm-sensors'),
    Package('sys-power/acpi'),
]


NETWORK_PACKAGE_LIST = [
    Package('net-misc/dhcpcd'),
    Package('net-wireless/iw'),
    Package('net-wireless/wireless-tools'),
    Package('net-wireless/wpa_supplicant', use_flags='ap'),

    Package('net-vpn/tor', use_flags='tor-hardening'),
    Package('net-dns/bind-tools'),
    Package('sys-apps/net-tools'),
    Package('net-proxy/mitmproxy'),
]


FS_PACKAGE_LIST = [
    Package('sys-apps/mlocate'),
    Package('sys-fs/inotify-tools'),
    Package('sys-fs/e2fsprogs', use_flags='tools'),
    Package('sys-fs/fuse-exfat'),
    Package('sys-fs/ntfs3g', use_flags='fuse mount-ntfs ntfsprogs'),
    Package('sys-fs/mtools'),
    Package('sys-fs/ncdu'),
    Package('net-fs/sshfs'),
    Package('net-fs/samba'),
    Package('net-fs/cifs-utils'),
    Package('sys-apps/smartmontools'),
]


DEV_PACKAGE_LIST = [
    Package('dev-vcs/git', use_flags='cgi gpg webdav'),
    Package('dev-lang/swig'),
    Package('dev-lang/python',
            merge_as_always=True,
            use_flags='\n'.join(['gdbm readline sqlite tk',
                                 '*/* PYTHON_SINGLE_TARGET: -* python3_10',
                                 '*/* PYTHON_TARGETS: -* python3_10'])),
]


EXTRA_PACKAGE_LIST = [
    Package('app-arch/unrar'),
    Package('sys-apps/lshw'),
    Package('media-gfx/imagemagick',
            use_flags=['djvu', 'jpeg', 'lzma',
                       'png', 'postscript',
                       'raw', 'webp']),

    Package('www-client/links',
            use_flags=['freetype', 'libevent', 'unicode',
                       'ipv6', 'jpeg', 'lzma',
                       'tiff', 'fbcon']),

    Package('app-admin/doas'),
    Package('sys-apps/inxi'),
]



TERMINAL_PACKAGE_LIST = [
    Package('app-shells/fish'),
    Package('app-text/tree'),

    Package('app-shells/fzf'),
    Package('app-misc/tmux'),
    Package('sys-process/htop'),
]


X_SERVER_PACKAGE_LIST = [
    Package('x11-base/xorg-server', use_flags='xephyr xorg xvfb'),
    Package('x11-apps/setxkbmap'),
    Package('x11-apps/xrandr'),
    Package('x11-apps/xev'),
    Package('x11-misc/xdo'),
    Package('x11-misc/xdotool'),
    MetaAction(['git clone --depth=1 https://github.com/rvaiya/warpd.git',
                'cd warpd; make && make install; cd -',
                'rm -rf warpd'],
               name='warpd git install'),
]


X_WM_PACKAGE_LIST = [
    Package('media-gfx/scrot'),
    Package('x11-misc/clipmenu', use_flags='rofi -dmenu'),

    Package('x11-wm/bspwm'),
    Package('x11-misc/sxhkd'),

    Package('x11-misc/picom', use_flags='config-file drm opengl'),
    Package('x11-misc/polybar', use_flags='mpd network curl ipc'),
    Package('x11-misc/rofi'),
    Package('x11-misc/xclip'),
    Package('x11-apps/xdpyinfo'),
    Package('x11-apps/xbacklight'),
]


def download_patches_for_st():
    l = logging.getLogger(__name__)
    patch_folder_path = '/etc/portage/patches/x11-terms/st'
    base_url = 'https://st.suckless.org/patches/'
    patches = ['alpha/st-alpha-20220206-0.8.5.diff',
               'dynamic-cursor-color/st-dynamic-cursor-color-0.8.4.diff']
    os.makedirs(patch_folder_path, exist_ok=True)
    for p in patches:
        l.info('Downloading patch for st')
        patchname = p.split('/')[1]
        ur.urlretrieve(f'{base_url}/{p}', f'{patch_folder_path}/{patchname}')


X_PACKAGE_LIST = [
    Package('media-gfx/feh', use_flags='xinerama'),
    Package('x11-terms/st', use_flags='savedconfig', pre=download_patches_for_st),
]


ACTION_LIST = [
    Action("grub-install --target=$(lscpu | awk '/Architecture/ {print $2}')-efi --efi-directory=/boot --removable",
           name='grub config creation'),
    MetaAction(['git clone --depth=1 https://github.com/AdisonCavani/distro-grub-themes.git',
                'cp -r distro-grub-themes/customize/gentoo /boot/grub/themes',
                r'echo "GRUB_GFXMODE=1920x1080" >> /etc/default/grub',
                r'echo "GRUB_THEME=\"/boot/grub/themes/gentoo/theme.txt\"" >> /etc/default/grub',
                'rm -rf distro-grub-themes'],
               name='grub theme install'),
    Action(r'echo "GRUB_CMDLINE_LINUX=\"dolvm root=UUID=$(blkid -t LABEL=rootfs -s UUID -o value)\"" >> /etc/default/grub',
           name='grub liux cmdline'),
    Action('grub-mkconfig -o /boot/grub/grub.cfg',
           name='grub config creation'),
    MetaAction(['git clone https://git.trustedfirmware.org/TF-A/trusted-firmware-a.git',
                'cd trusted-firmware-a',
                'sed -i "s/[^[:space:]]*--fatal-warnings//g" Makefile',
                'make PLAT=sun50i_h616 -j$(nproc) all'],
               name='trusted-firmware compilation'),
    MetaAction(['git clone https://source.denx.de/u-boot/u-boot.git',
                'cd u-boot',
                'cp /u-boot.config .config',
                'git apply power.patch',
                'make olddefconfig',
                'make BL31=/trusted-firmware-a/build/sun50i_h616/release/bl31.bin -j$(nproc)',
                f'dd if=u-boot-sunxi-with-spl.bin of={common.DISK_NODE} bs=1k seek=8'],
               name='u-boot installation'),
] + [
    Action(f'rc-update add {s} boot',
           name=f'service {s} added to boot')
    for s in ['lvmetad', 'consolefont']
] + [
    Action(f'rc-update add {s} default',
           name=f'service {s} added to default')
    for s in ['sysklogd', 'cronie', 'alsasound',
              'docker', 'libvirtd', 'pulseaudio',
              'dbus', 'dhcpcd']
]


POST_INSTALL_CALLBACKS = []


def pre_install():
    total_memory_action = Action("free -t | awk '/Total/{print $2}'",
                                 name='getting total memory')
    Executor.exec(total_memory_action, do_crash=True)
    # If system has less than 10 Gigs of free space, better create swap
    free_memory = int(total_memory_action.value)
    _12_GB = 12000000
    if free_memory < _12_GB:
        l = logging.getLogger(__name__)
        l.info(f'Your system have less than 12 Gigs of free space, creating swap')
        block_count = (_12_GB - free_memory) // 1024
        swapfile = '/tmp/swapfile'
        dd_action = Action(f'dd if=/dev/zero of={swapfile} bs=1M count={block_count}',
                           name='swap file initialization')
        mkswap_action = Action(f'mkswap {swapfile}',
                               name='formatting swap file')
        swapon_action = Action(f'swapon {swapfile}',
                               name='activating swap file')
        for a in [dd_action, mkswap_action, swapon_action]:
            Executor.exec(a)
    with open('/etc/portage/package.mask/install.mask', 'w') as f:
        f.writelines([f'{m}\n' for m in MASKS])


    if common.TMPFS_SIZE:
        tmpfs_action = Action(f'mount -t tmpfs -o size={common.TMPFS_SIZE} tmpfs /var/tmp/portage',
                              name='tmpfs mount')
        Executor.exec(tmpfs_action)

    Executor.exec(Package('app-portage/mirrorselect', merge_as_always=True))
    Executor.exec(Action(f'mirrorselect -s{common.MIRROR_COUNT} -4 -D', name='mirrorselect'))
    Executor.exec(Action('emerge --sync', name='emerge sync'))

    Executor.exec(Action('perl-cleaner --reallyall', name='perl clean'))


    execute_each_in(QUIRKED_PACKAGES)
    if common.USE_ARIA2:
        aria_cmd = [r"/usr/bin/aria2c",
                    r"--dir=\${DISTDIR}",
                    r"--out=\${FILE}",
                    r"--allow-overwrite=true",
                    r"--max-tries=5",
                    r"--max-file-not-found=2",
                    r"--user-agent=Wget/1.19.1",
                    r"--connect-timeout=5",
                    r"--timeout=5",
                    f"--split={common.MIRROR_COUNT}",
                    r"--min-split-size=2M",
                    r"--max-connection-per-server=2",
                    r"--uri-selector=inorder \${URI}"]
        common.add_variable_to_file(common.MAKE_CONF_PATH,
                                    'FETCHCOMMAND',
                                    ' '.join(aria_cmd))


    prefetch_thread = t.Thread(target=predownload,
                               args=([p for p in PACKAGE_LIST if type(p) == Package][1:],))
    prefetch_thread.start()


def predownload(package_container):
    for pkg in package_container:
        pkg.download()


def execute_each_in(action_container, *args):
    failed_count = 0
    for a in action_container:
        if type(a) == tuple:
            Executor.exec(a[0], *args, fallbacks=a[1], do_crash=True)
        else:
            Executor.exec(a, *args)
            if not a.succeded:
                failed_count += 1
    return failed_count


def post_install():
    for c in POST_INSTALL_CALLBACKS:
        c()
    return execute_each_in(ACTION_LIST)


PACKAGE_LIST = ESSENTIAL_PACKAGE_LIST \
               + NETWORK_PACKAGE_LIST \
               + FS_PACKAGE_LIST \
               + EXTRA_PACKAGE_LIST \
               + TERMINAL_PACKAGE_LIST \
               + DEV_PACKAGE_LIST

if common.MERGE_EARLY:
    PACKAGE_LIST = reoder_packages_for_early_merge(PACKAGE_LIST)
else:
    exclude_from_world_rebuild(PACKAGE_LIST)
