import itertools as it

import disk_ops

from entity import Executor


def prepare_for_partitioning(disk):
    wipe_disk_action = disk_ops.wipe_disk(disk)
    lvm_groups_get_action = disk_ops.get_lvm_groups()
    Executor.exec(wipe_disk_action, do_crash=True)
    Executor.exec(lvm_groups_get_action)

    lvm_rm_wipe_action = disk_ops.rm_lvm_groups(lvm_groups_get_action.value)
    Executor.exec(lvm_rm_wipe_action)


def part_disk(disk):
    parted_action = disk_ops.parted_on(disk)
    parted_script = it.chain(disk_ops.part_for_bootloader(),
                             disk_ops.part_for_boot(),
                             disk_ops.part_for_lvm())

    for l in parted_script:
        Executor.exec(parted_action, f'"{l}"', do_crash=True)

    get_bootloader_action = disk_ops.get_dev_node(disk, 1)
    get_lvm_action = disk_ops.get_dev_node(disk, 3)
    Executor.exec(get_bootloader_action, do_crash=True)
    Executor.exec(get_lvm_action, do_crash=True)
    return (get_bootloader_action.value, get_lvm_action.value)


def create_lvm_partition(bootloader_partition,
                         lvm_partition,
                         rootfs_percent=100,
                         swap_size=2048):
    lvm_daemon_start_action = disk_ops.start_lvm_daemon()
    physical_volume_creation_action = disk_ops.create_physical_volume(lvm_partition)
    lvm_partitioning_actions = disk_ops.allocate_space_in_lvm(rootfs_percent=rootfs_percent,
                                                              swap_size=swap_size)
    fs_and_swap_actions = disk_ops.make_fs_and_swap(bootloader_partition)
    for a in [lvm_daemon_start_action, physical_volume_creation_action] \
             + lvm_partitioning_actions \
             + fs_and_swap_actions:
        Executor.exec(a, do_crash=True)


def prepare_for_os_install():
    Executor.exec(disk_ops.prepare_for_os_install(), do_crash=True)
