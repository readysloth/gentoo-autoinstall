#!/usr/bin/env bash
set -x

DIR="$(dirname "$0")"

IMAGE="$1"
CD="$2"

CPUINFO_FILE="${3:-/proc/cpuinfo}"
QEMU="${4:-qemu-system-x86_64}"

MEMORY_FOR_QEMU="$(echo "$(free -t | tail -n 1 | awk '{print $2}') * 0.8 / 1024" | bc )"

$QEMU \
  -enable-kvm \
  -m "$(printf "%.0f" "$MEMORY_FOR_QEMU")" \
  -drive if=pflash,file=/usr/share/edk2-ovmf/OVMF_CODE.fd,format=raw,readonly=on \
  -cdrom "$CD" \
  -drive file="$IMAGE",format=raw \
  -nographic \
  -cpu "kvm64,$(python3 "$DIR"/cpuinfo2qemu/cpuinfo2qemu.py -f "$CPUINFO_FILE" "$QEMU")" \
  -netdev user,id=ssh_net,hostfwd=tcp:127.0.0.1:12222-:22 \
  -device e1000,netdev=ssh_net
