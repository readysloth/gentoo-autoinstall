import os
import logging
import urllib.request as ur

import install_logger

from entity import Package, Action, Executor


ESSENTIAL_PACKAGE_LIST = [
    Package('sys-devel/gcc', use_flags='go sanitize graphite'),
    Package('app-shells/dash'),
    Package('@world', '-uDNv --with-bdeps=y --backtrack=100'),
    Package('media-libs/libpng', use_flags='apng'),
    Package('sys-libs/ncurses', use_flags='-gpm'),
    Package('app-editors/vim', use_flags='vim-pager perl terminal lua'),
    Package('sys-kernel/gentoo-sources', use_flags='symlink'),
    Package('sys-kernel/genkernel'),
    Package('sys-kernel/linux-firmware'),
    Package('app-admin/sysklogd', use_flags='logger'),
    Package('sys-process/cronie'),

    Package('sys-boot/grub', use_flags='device-mapper'),
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
    Package('dev-lang/rust'),
]


EXTRA_PACKAGE_LIST = [
    Package('media-fonts/noto', use_flags='cjk'),
    Package('media-fonts/noto-emoji'),
    Package('media-libs/mesa', use_flags=['classic', 'd3d9', 'lm-sensors',
                                          'osmesa', 'vdpau', 'vulkan']),
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
]


X_WM_PACKAGE_LIST = [
    Package('media-gfx/scrot'),
    Package('x11-misc/clipmenu', use_flags='rofi'),

    Package('x11-wm/bspwm'),
    Package('x11-misk/xdo'),
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
    os.makedirs(folder, exist_ok=True)
    for p in patches:
        l.info('Downloading patch for st')
        patchname = p.split('/')[1]
        ur.urlretrieve(f'{base_url}/{p}', f'{patch_folder_path}/{patchname}')



X_PACKAGE_LIST = [
    Package('app-emulation/virt-manager', use_flags='gtk'),
    Package('www-client/firefox',
            use_flags=['system-harfbuzz', 'system-icu', 'system-jpeg',
                       'system-libevent', 'system-png', 'system-python-libs',
                       'system-webp', 'geckodriver', 'screencast']),
    Package('app-office/libreoffice', use_flags='pdfimport'),
    Package('net-im/telegram-desktop', use_flags='screencast hunspell'),
    Package('media-gfx/feh', use_flags='xinerama'),
    Package('media-gfx/gimp', use_flags='webp lua'),
    Package('media-gfx/flameshot'),
    Package('media-video/peek'),
    Package('x11-terms/st', use_flags='savedconfig', pre=download_patches_for_st),
]


ACTION_LIST = [
    Action('genkernel --lvm --e2fsprogs --mountboot --busybox --install all',
           name='genkernel'),
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
    Action('bash create_configs.sh',
           name='configuration file creation')
]


def pre_install():
    pass


def execute_each_in(action_container):
    failed_count = 0
    for a in action_container:
        if type(a) == tuple:
            Executor.exec(a[0], fallbacks=a[1], do_crash=True)
        else:
            Executor.exec(a)
            if not a.succeded:
                failed_count += 1
    return failed_count


def post_install():
    return execute_each_in(ACTION_LIST)


PACKAGE_LIST = ESSENTIAL_PACKAGE_LIST \
               + NETWORK_PACKAGE_LIST \
               + FS_PACKAGE_LIST \
               + EXTRA_PACKAGE_LIST \
               + TERMINAL_PACKAGE_LIST \
               + DEV_PACKAGE_LIST
