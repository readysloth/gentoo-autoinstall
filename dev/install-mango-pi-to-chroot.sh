#!/usr/bin/env bash

export LANG=en_US.UTF8

MOUNTPOINT="$1"

umount -R $MOUNTPOINT
swapoff /dev/lvg/swap
lvchange -an /dev/lvg/*
losetup -D
qemu-img create mangopi.img 63864569856
LOOP_DEVICE="$(losetup -fP --show mangopi.img)"
python3 install.py install -u bluetooth -f 10G -ambt "$LOOP_DEVICE"
