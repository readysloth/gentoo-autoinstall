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
    world_emerge = world_package.cmd_template.format(opts=world_package.options,
                                                     pkg=world_package.package)
    world_package.cmd = f'until {world_emerge}; do :; done'

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
    '<dev-libs/openssl-3.0.9',
    # Installation results in SIGSEGV in compiler (wtf?)
    '>dev-util/ccache-4.7.4'
]

QUIRKED_PACKAGES = [
    Package('media-libs/libsndfile', use_flags='minimal', merge_as_always=True),
    Package('net-misc/aria2', use_flags='bittorent libuv ssh', merge_as_always=True),
    Package('dev-util/ccache', merge_as_always=True),
    Package('dev-util/vmtouch', merge_as_always=True),
]


ESSENTIAL_PACKAGE_LIST = [
    Package('sys-devel/gcc',
            merge_as_always=True,
            use_flags=['-ada', '-objc', '-objc-gc',
                       '-d', '-debug', 'sanitize',
                       'graphite', 'ntpl', 'jit'],
            possible_quirks=['half-nproc',
                             'linker-tradeoff',
                             'notmpfs'],
            keywords={'minimal': False}),

    Package('dev-python/pypy3',
            use_flags='gdbm jit sqlite tk',
            merge_as_always=True,
            keywords={'minimal': False}),

    ### Uncomment following lines if pypy is faster than CPython with lto+pgo
    ### on your machine
    ###
    #Action('echo "*/* PYTHON_TARGETS: pypy3" >> /etc/portage/package.use/global',
    #       name='system-wide pypy3'),
    #Action('echo "pypy3" >> /etc/python-exec/emerge.conf',
    #       name='system-wide pypy3'),
    Package('app-shells/dash', merge_as_always=True),
    Package('sys-kernel/gentoo-sources', use_flags='symlink', merge_as_always=True),
    Package('sys-kernel/genkernel', merge_as_always=True),
    Package('sys-kernel/linux-firmware',
            use_flags='compress-xz',
            merge_as_always=True),

    Action('wget https://raw.githubusercontent.com/readysloth/gentoo-autoinstall/main/scripts/configs/kernel-6.3.8.config',
           name='kernel config download'),
    # there can be tmpfs, so switch tmpdir to it
    Action(' '.join(['genkernel',
                     '--lvm',
                     '--e2fsprogs',
                     '--mountboot',
                     '--busybox',
                     '--install',
                     '--save-config',
                     '--firmware',
                     '--compress-initramfs-type=best',
                     '--all-ramdisk-modules',
                     '--kernel-cc=/usr/lib/ccache/bin/gcc',
                     '--kernel-config=kernel-6.3.8.config',
                     'all']),
           pre=move_kernel_src_to_tmpfs,
           post=move_kernel_src_from_tmpfs,
           in_background=True,
           name='genkernel'),

    # with global `gpm` use flag
    Package('sys-libs/ncurses', '--nodeps', env={'USE': '-gpm'}, merge_as_always=True),
    Package('sys-libs/gpm', '--nodeps', merge_as_always=True),
    Package('sys-libs/ncurses', merge_as_always=True),

    Package('sys-apps/portage', use_flags='native-extensions ipc xattr'),
    Package('sys-apps/util-linux', use_flags='-logger', merge_as_always=True),
    Package('@world', '-uDNv --with-bdeps=y --backtrack=100'),
    Package('media-libs/libpng', use_flags='apng'),
    Package('app-editors/vim', use_flags='vim-pager perl terminal lua'),
    Package('app-admin/sysklogd', use_flags='logger'),
    Package('sys-process/cronie'),

    Package('sys-boot/grub', use_flags='device-mapper mount'),
    Package('sys-boot/os-prober'),
    Package('sys-apps/lm-sensors'),
    Package('sys-power/acpi'),
    Package('sys-process/procenv'),
    Package('dev-libs/light'),
    Package('app-arch/zip'),
    Package('app-admin/pass', use_flags='git'),
    Package('app-admin/pass-otp'),
]


NETWORK_PACKAGE_LIST = [
    Package('net-misc/networkmanager',
            use_flags=['conncheck', 'connection-sharing',
                       'dhcpcd', 'elogind',
                       'iptables', 'wifi',
                       'tools']),
    Package('net-misc/dhcpcd'),
    Package('net-wireless/iw'),
    Package('net-wireless/wireless-tools'),
    Package('net-wireless/wpa_supplicant', use_flags='ap'),

    Package('net-misc/proxychains'),
    Package('net-vpn/tor', use_flags='tor-hardening'),
    Package('net-dns/bind-tools'),
    Package('sys-apps/net-tools'),
    Package('net-proxy/mitmproxy'),
    Package('net-proxy/privoxy', use_flags='compression fast-redirects whitelists'),
    Package('net-analyzer/tcpdump'),
    Package('net-misc/tigervnc', use_flags='server viewer')
]


FS_PACKAGE_LIST = [
    Package('sys-apps/mlocate'),
    Package('sys-fs/inotify-tools'),
    Package('sys-fs/e2fsprogs', use_flags='tools'),
    Package('sys-fs/fuse-exfat'),
    Package('sys-fs/exfatprogs'),
    Package('sys-fs/ntfs3g', use_flags='fuse mount-ntfs ntfsprogs'),
    Package('sys-fs/mtools'),
    Package('sys-fs/ncdu-bin'),
    Package('net-fs/sshfs'),
    Package('net-fs/samba'),
    Package('net-fs/cifs-utils'),
    Package('sys-apps/smartmontools'),
    Package('sys-fs/dosfstools'),
    Package('sys-fs/fuse-zip'),
]


DEV_PACKAGE_LIST = [
    Package('dev-util/cmake'),
    Package('dev-vcs/git', use_flags='cgi gpg highlight webdav'),
    Package('dev-lang/python', use_flags='gdbm readline sqlite tk'),
    Package('sys-devel/gdb', use_flags='server source-highlight xml xxhash'),
    Package('dev-scheme/racket',
            use_flags='futures chez',
            keywords={'minimal': False}),
    Package('dev-lang/clojure',
            keywords={'minimal': False}),
    Package('dev-util/android-tools'),
    Package('dev-util/rr',
            keywords={'minimal': False}),
    Package('dev-lang/rust',
            possible_quirks=['half-nproc',
                             'linker-tradeoff',
                             'notmpfs'],
            keywords={'minimal': False}),
    Package('dev-dotnet/dotnet-sdk-bin',
            use_flags='dotnet-symlink',
            keywords={'minimal': False}),
    Package('dev-util/coccigrep',
            keywords={'minimal': False}),
    Package('dev-util/radare2'),
    Package('dev-util/bloaty',
            keywords={'minimal': False}),
    Package('dev-util/difftastic'),
    Package('dev-util/gef'),
    Package('dev-util/ltrace'),
    Package('dev-util/strace'),
    Package('dev-util/valgrind',
            keywords={'minimal': False}),
    Package('app-misc/binwalk'),
    Package('dev-util/cppcheck',
            use_flags='htmlreport',
            keywords={'minimal': False}),
    Package('app-forensics/radamsa'),
    Package('app-forensics/aflplusplus',
            keywords={'minimal': False}),
    Package('app-forensics/zzuf'),
    Package('dev-util/poke', use_flags='nbd'),
    Package('media-gfx/graphviz'),
    Package('dev-util/bear'),
    Package('app-misc/hivex', use_flags='readline'),
]


EXTRA_PACKAGE_LIST = [
    Package('media-fonts/noto'),
    Package('media-fonts/fira-code'),
    Package('media-fonts/noto-emoji'),
    Package('dev-util/glslang'),  # for mesa build
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
            use_flags=['freetype', 'libevent', 'unicode',
                       'ipv6', 'jpeg', 'lzma',
                       'tiff', 'fbcon']),

    Package('app-text/html-xml-utils',
            keywords={'minimal': False}),
    Package('app-admin/doas'),
    Package('sys-apps/inxi'),
    Package('app-misc/jq'),
    Package('app-misc/yq'),

    Package('media-gfx/freecad',
            use_flags=['addonmgr', 'designer', 'fem',
                       'gui', 'image', 'inspection',
                       'material', 'netgen', 'part-design',
                       'show', 'surface', 'techdraw'],
            keywords={'minimal': False}),
    Package('media-gfx/openscad'),
    Package('net-print/hplip', use_flags='hpcups'),
    Package('app-eselect/eselect-repository'),
]


TERMINAL_PACKAGE_LIST = [
    Package('app-shells/fish'),
    Package('app-text/tree'),

    Package('app-shells/fzf'),
    Package('app-misc/tmux'),
    Package('sys-apps/ripgrep-all', keywords={'minimal': False}),
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
                'cd warpd; DISABLE_WAYLAND=1 make && make install; cd -',
                'rm -rf warpd'],
               name='warpd git install'),
    Package('x11-misc/xfe'),
    Package('x11-apps/xkill'),
]


X_WM_PACKAGE_LIST = [
    Package('media-gfx/scrot'),
    Package('x11-misc/clipmenu',
            use_flags='rofi -dmenu'),

    Package('x11-wm/bspwm'),
    Package('x11-misc/sxhkd'),

    Package('x11-misc/picom',
            use_flags='config-file drm opengl'),
    Package('x11-misc/polybar',
            use_flags='mpd network curl ipc'),
    Package('x11-misc/rofi'),
    Package('x11-misc/xclip'),
    Package('x11-apps/xdpyinfo'),
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
    Package('app-emulation/libvirt',
            use_flags='libssh lvm parted qemu libvirtd',
            keywords={'minimal': False}),
    Package('app-emulation/virt-manager',
            use_flags='gtk',
            keywords={'minimal': False}),
    # Quirk, because firefox requires node js and nodejs
    # doesn't build with `lto` USE flag
    Package('net-libs/nodejs',
            use_flags='-lto npm',
            keywords={'minimal': False}),
    Package('www-client/firefox',
            use_flags=['system-harfbuzz', 'system-icu', 'system-jpeg',
                       'system-libevent', 'system-png', 'system-python-libs',
                       'system-webp', 'geckodriver'],
            possible_quirks=['half-nproc',
                             'linker-tradeoff',
                             'notmpfs'],
            keywords={'minimal': False}),
    Package('app-office/libreoffice',
            use_flags='pdfimport',
            possible_quirks=['half-nproc',
                             'linker-tradeoff',
                             'notmpfs'],
            keywords={'minimal': False}),
    Package('net-im/telegram-desktop',
            use_flags='screencast hunspell'),
    Package('media-gfx/feh', use_flags='xinerama'),
    Package('media-gfx/gimp',
            use_flags='webp lua',
            keywords={'minimal': False}),
    Package('media-gfx/flameshot'),
    Package('media-video/peek'),
    Package('app-admin/conky',
            use_flags='intel-backlight iostats portmon imlib',
            keywords={'minimal': False}),
    Package('x11-terms/st',
            use_flags='savedconfig',
            pre=download_patches_for_st),
]


ACTION_LIST = [
    Action("grub-install --target=$(lscpu | awk '/Architecture/ {print $2}')-efi --efi-directory=/boot --removable",
           name='grub config creation'),
    MetaAction(['git clone --depth=1 https://github.com/AdisonCavani/distro-grub-themes.git',
                'mkdir -p /boot/grub/themes/gentoo',
                'tar -xvf distro-grub-themes/themes/gentoo.tar -C /boot/grub/themes/gentoo',
                r'echo "GRUB_GFXMODE=1920x1080" >> /etc/default/grub',
                r'echo "GRUB_THEME=\"/boot/grub/themes/gentoo/theme.txt\"" >> /etc/default/grub',
                'rm -rf distro-grub-themes'],
               name='grub theme install'),
    Action(r'echo "GRUB_CMDLINE_LINUX=\"dolvm root=UUID=$(blkid -t LABEL=rootfs -s UUID -o value)\"" >> /etc/default/grub',
           name='grub liux cmdline'),
    Action('grub-mkconfig -o /boot/grub/grub.cfg',
           name='grub config creation'),
    Action("chmod +x /etc/local.d/*.start",
           name='local.d execution privilege'),
] + [
    Action(f'rc-update add {s} boot',
           name=f'service {s} added to boot')
    for s in ['lvmetad', 'consolefont']
] + [
    Action(f'rc-update add {s} default',
           name=f'service {s} added to default')
    for s in ['sysklogd', 'cronie', 'alsasound',
              'docker', 'libvirtd', 'pulseaudio',
              'dbus', 'NetworkManager']
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

    common.add_value_to_string_variable(common.MAKE_CONF_PATH, 'FEATURES', 'ccache')
    common.add_variable_to_file(common.MAKE_CONF_PATH, 'CCACHE_DIR', '/var/cache/ccache')

    os.makedirs('/var/cache/ccache/', exist_ok=True)
    common.add_variable_to_file('/var/cache/ccache/ccache.conf',
                                'max_size',
                                '15.0G',
                                quot='')
    common.add_variable_to_file('/var/cache/ccache/ccache.conf',
                                'hash_dir',
                                'false',
                                quot='')
    common.add_variable_to_file('/var/cache/ccache/ccache.conf',
                                'compiler_check',
                                r'%compiler% -dumpversion',
                                quot='')
    common.add_variable_to_file('/var/cache/ccache/ccache.conf',
                                'cache_dir_levels',
                                '3',
                                quot='')
    common.add_variable_to_file('/var/cache/ccache/ccache.conf',
                                'compression',
                                'true',
                                quot='')
    common.add_variable_to_file('/var/cache/ccache/ccache.conf',
                                'compression_level',
                                '1',
                                quot='')
    common.add_variable_to_file('/var/cache/ccache/ccache.conf',
                                'cache_dir',
                                '/var/cache/ccache/cache',
                                quot='')

    shutil.chown('/var/cache/ccache/', user='portage', group='portage')

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


def log_package_list(pkg_list, excluded_pkgs=None):
    l = logging.getLogger(__name__)
    for p in pkg_list:
        if type(p) == Package:
            l.info(f'Would be installed {p.package}')
    if excluded_pkgs:
        for p in excluded_pkgs:
            if type(p) == Package:
                l.info(f'Excluded from install {p.package}')


PACKAGE_LIST = ESSENTIAL_PACKAGE_LIST \
               + NETWORK_PACKAGE_LIST \
               + FS_PACKAGE_LIST \
               + EXTRA_PACKAGE_LIST \
               + TERMINAL_PACKAGE_LIST \
               + DEV_PACKAGE_LIST
