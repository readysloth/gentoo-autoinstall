from entity import Action


LVM_GROUP_NAME = 'vg01'


def wipe_disk(disk):
    return Action(f'wipefs -af {disk}', name="wipe disk's fs")


def get_lvm_groups():
    return Action("vgs | sed 1d | awk '{print $1}'", name='list lvm groups')


def rm_lvm_groups(groups):
    return Action(f'vgremove -y {groups}', name='wipe lvm groups')


def parted_on(disk):
    return Action(f'parted -a optimal --script {disk}', name='partition disk')


def part_for_bootloader():
    yield from ['mklabel gpt',
                'mkpart primary 1MiB 3MiB',
                'name 1 grub',
                'set 1 bios_grub on']

def part_for_boot():
    yield from ['mkpart primary 3MiB 259MiB',
                'name 2 boot',
                'set 2 boot on']


def part_for_lvm():
    yield from ['mkpart primary 259MiB -1',
                'name 3 lvm',
                'set 3 lvm on']


def get_dev_node(disk, number):
    return Action(f"fdisk -lo device | grep {disk} sed 1d | sed -n {number}p",
                  name='partition node name')


def start_lvm_daemon():
    return Action('/etc/init.d/lvm start',
                  name='lvm daemon start')


def create_physical_volume(partition):
    return Action(f'pvcreate -ff {partition} && vgcreate {LVM_GROUP_NAME} {partition}',
                  name='physical lvm volume creation')


def allocate_space_in_lvm(rootfs_percent=100, swap_size=2048):
    basic_lvm_partitioning = [Action(f'lvcreate -y -L 2048M -n swap {LVM_GROUP_NAME}',
                                     name='creation of lvm swap partition'),
                              Action(f'lvcreate -y -l {rootfs_percent}%FREE -n rootfs {LVM_GROUP_NAME}',
                                     name='creation of lvm rootfs partition')]
    if rootfs_percent != 100:
        basic_lvm_partitioning += [Action(f'lvcreate -y -l {100 - rootfs_percent}%FREE -n free_space {LVM_GROUP_NAME}',
                                          name='creation of lvm free_space partition')]
    return basic_lvm_partitioning


def make_fs_and_swap(partition):
    return [Action(f'mkfs.fat -F 32 {partition}', name='filesystem creation'),
            Action(f'mkfs.ext4 /dev/{LVM_GROUP_NAME}/rootfs', name='filesystem creation'),
            Action(f'mkswap /dev/{LVM_GROUP_NAME}/swap', name='swap creation'),
            Action(f'swapon /dev/{LVM_GROUP_NAME}/swap', name='swap initialization')]


def prepare_for_os_install():
    return Action(f'mount /dev/{LVM_GROUP_NAME}/rootfs /mnt/gentoo', name='target disk mount')
