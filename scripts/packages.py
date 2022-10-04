import os
import logging
import threading as t
import urllib.request as ur

import common
import install_logger

from entity import Package, Action, MetaAction, Executor


def combine_package_install(pkg_list):
    def is_raw_package(pkg):
        return not type(pkg) == MetaAction and \
               not pkg.use_flags and \
               not pkg.possible_quirks and \
               not pkg.options

    raw_package_names = [p.package for p in pkg_list if is_raw_package(p)]
    non_raw_packages = [p for p in pkg_list if not is_raw_package(p)]
    big_package = Package(' '.join(raw_package_names))
    return non_raw_packages + [big_package]


MASKS = [
    '<sys-libs/compiler-rt-15.0.0'
]

QUIRKED_PACKAGES = [
    Package('sys-libs/ncurses', '--oneshot', use_flags='-gpm'), # should solve circular dep
    Package('sys-libs/gpm'), # should solve circular dep
    Package('sys-libs/ncurses', '--oneshot'), # should solve circular dep
]


ESSENTIAL_PACKAGE_LIST = [
    Package('sys-devel/gcc',
            use_flags='-ada -objc -objc-gc -fortran sanitize graphite',
            possible_quirks=['half-nproc',
                             'linker-tradeoff',
                             'notmpfs']),
    Package('app-shells/dash'),
    Package('@world', '-uDNv --with-bdeps=y --backtrack=100'),
    Package('media-libs/libpng', use_flags='apng'),
    Package('app-editors/vim', use_flags='vim-pager perl terminal lua'),
    Package('sys-kernel/gentoo-sources', use_flags='symlink'),
    Package('sys-kernel/genkernel'),
    Package('sys-kernel/linux-firmware'),
    Action('genkernel --lvm --e2fsprogs --mountboot --busybox --install all',
           name='genkernel'),
    Package('app-admin/sysklogd', use_flags='logger'),
    Package('sys-process/cronie'),

    Package('sys-boot/grub', use_flags='device-mapper mount'),
    Package('sys-boot/os-prober'),
    Package('sys-apps/lm-sensors'),
    Package('sys-power/acpi'),
]


NETWORK_PACKAGE_LIST = [
    Package('net-misc/dhcpcd'),
    Package('net-wireless/iw'),
    Package('net-wireless/wireless-tools'),
    Package('net-wireless/wpa_supplicant', use_flags='ap'),

    Package('net-misc/proxychains'),
    Package('net-vpn/tor', use_flags='tor-hardening'),
    Package('net-dns/bind-tools'),
    Package('sys-apps/net-tools'),
]


FS_PACKAGE_LIST = [
    Package('sys-apps/mlocate'),
    Package('sys-fs/inotify-tools'),
    Package('sys-fs/e2fsprogs', use_flags='tools'),
    Package('sys-fs/fuse-exfat'),
    Package('sys-fs/exfatprogs'),
    Package('sys-fs/ntfs3g', use_flags='fuse mount-ntfs ntfsprogs'),
    Package('sys-fs/mtools'),
    Package('sys-fs/ncdu'),
    Package('net-fs/sshfs'),
    Package('net-fs/samba'),
    Package('net-fs/cifs-utils'),
]


DEV_PACKAGE_LIST = [
    Package('dev-util/cmake'),
    Package('dev-vcs/git', use_flags='cgi gpg highlight webdav'),
    Package('dev-lang/python', use_flags='gdbm readline sqlite tk'),
    Package('dev-python/pypy3', use_flags='gdbm jit sqlite tk'),
    Package('sys-devel/gdb', use_flags='server source-highlight xml xxhash'),
    Package('dev-scheme/racket', use_flags='futures chez'),
    Package('dev-lang/clojure'),
    Package('dev-python/bpython', use_flags='jedi'),
    Package('dev-util/android-tools'),
    Package('dev-util/rr'),
    Package('dev-lang/rust',
            possible_quirks=['half-nproc',
                             'linker-tradeoff',
                             'notmpfs']),
]


EXTRA_PACKAGE_LIST = [
    Package('media-fonts/noto', use_flags='cjk'),
    Package('media-fonts/noto-emoji'),
    Package('dev-util/glslang'), # for mesa build
    Package('media-libs/mesa', use_flags=['classic', 'd3d9', 'lm-sensors',
                                          'osmesa', 'vdpau', 'vulkan']),
    Package('media-sound/pulseaudio', use_flags='daemon glib'),
    Package('media-sound/alsa-utils', use_flags='bat'),
    Package('media-libs/libmpd'),
    Package('media-sound/mpd'),
    Package('app-arch/unrar'),
    Package('sys-apps/lshw'),
    Package('app-containers/docker'),
    Package('app-containers/docker-cli'),
    Package('app-containers/docker-compose'),
    Package('app-emulation/qemu',
            use_flags=['aio', 'alsa', 'capstone', 'curl', 'fdt',
                       'io-uring', 'plugins', 'png', 'jpeg', 'fuse',
                       'sdl', 'sdl-image', 'spice', 'ssh', 'usb',
                       'usbredir', 'gtk', 'vnc', 'vhost-net']),
    Package('app-emulation/wine-staging',
            use_flags=['dos', 'gecko', 'faudio',
                       'mono', 'udev', 'run-exes',
                       'netapi', 'samba', 'sdl',
                       'vulkan']),
    Package('app-emulation/winetricks'),
    Package('media-gfx/imagemagick',
            use_flags=['djvu', 'jpeg', 'lzma',
                       'png', 'postscript',
                       'raw', 'svg', 'webp']),

    Package('www-client/links',
            use_flags=['freetype', 'libevent', 'fbcon',
                       'ipv6', 'jpeg', 'lzma',
                       'ssl', 'svga', 'tiff',
                       'unicode']),

    Package('app-text/html-xml-utils'),
]



TERMINAL_PACKAGE_LIST = [
    Package('app-shells/fish'),
    Package('app-text/tree'),

    Package('app-shells/fzf'),
    Package('app-misc/tmux'),
    Package('sys-apps/ripgrep-all'),
    Package('sys-process/htop'),
]


X_SERVER_PACKAGE_LIST = [
    Package('x11-base/xorg-server', use_flags='xephyr xorg xvfb'),
    Package('x11-apps/setxkbmap'),
    Package('x11-apps/xrandr'),
    Package('x11-apps/xev'),
    Package('x11-misc/xdo'),
    Package('x11-misc/xdotool'),
    MetaAction(['git clone https://github.com/jordansissel/keynav.git',
                'cd keynav; make install; cd -',
                'rm -rf keynav'],
               name='keynav git install'),
]


X_WM_PACKAGE_LIST = [
    Package('media-gfx/scrot'),
    Package('x11-misc/clipmenu', use_flags='rofi'),

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
    patch_folder_path = '/etc/portage/patches/dev-lang/x11-terms/st'
    base_url = 'https://st.suckless.org/patches/'
    patches = ['alpha/st-alpha-20220206-0.8.5.diff',
               'dynamic-cursor-color/st-dynamic-cursor-color-0.8.4.diff']
    os.makedirs(patch_folder_path, exist_ok=True)
    for p in patches:
        l.info('Downloading patch for st')
        patchname = p.split('/')[1]
        ur.urlretrieve(f'{base_url}/{p}', f'{patch_folder_path}/{patchname}')


X_PACKAGE_LIST = [
    Package('app-emulation/virt-manager', use_flags='gtk'),
    Package('www-client/firefox',
            use_flags=['system-harfbuzz', 'system-icu', 'system-jpeg',
                       'system-libevent', 'system-png', 'system-python-libs',
                       'system-webp', 'geckodriver'],
            possible_quirks=['half-nproc',
                             'linker-tradeoff',
                             'notmpfs']),
    Package('app-office/libreoffice',
            use_flags='pdfimport',
            possible_quirks=['half-nproc',
                             'linker-tradeoff',
                             'notmpfs']),
    Package('net-im/telegram-desktop', use_flags='screencast hunspell'),
    Package('media-gfx/feh', use_flags='xinerama'),
    Package('media-gfx/gimp', use_flags='webp lua'),
    Package('media-gfx/flameshot'),
    Package('media-video/peek'),
    Package('x11-terms/st', use_flags='savedconfig', pre=download_patches_for_st),
]


ACTION_LIST = [
    Action('grub-mkconfig -o /boot/grub/grub.cfg',
           name='grub config creation'),
    Action("grub-install --target=$(lscpu | awk '/Architecture/ {print $2}')-efi --efi-directory=/boot --removable",
           name='grub config creation'),
    Action('rc-update add sysklogd default',
           name='service update'),
    Action('rc-update add cronie default',
           name='service update'),
    Action('mkdir ~/.config',
           name='.config folder creation in home'),
    Action('rc-update add alsasound default',
           name='service update'),
    Action('rc-update add docker default',
           name='service update'),
    Action('rc-update add libvirtd default',
           name='service update'),
    Action('rc-update add dhpcd default',
           name='service update'),
    Action('rc-update add lvmetad boot',
           name='service update'),
    Action('bash create_configs.sh',
           name='configuration file creation')
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
        f.writelines(MASKS)


    if common.TMPFS_SIZE:
        tmpfs_action = Action(f'mount -t tmpfs -o size={common.TMPFS_SIZE} tmpfs /var/tmp/portage',
                              name='tmpfs mount')
        Executor.exec(tmpfs_action)

    Executor.exec(Action('perl-cleaner --reallyall', name='perl clean'))
    execute_each_in(QUIRKED_PACKAGES)
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

#PACKAGE_LIST = combine_package_install(PACKAGE_LIST)
