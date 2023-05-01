#!/usr/bin/env bash


DIR="$(dirname "$0")/../scripts/configs/patches"

git apply --verbose "$DIR"/power.patch
git apply --verbose "$DIR"/power.dtb.patch
git apply --verbose "$DIR"/arm64-dts-allwinner-h616-Add-device-node-for-SID.patch
git apply --verbose "$DIR"/arm64-dts-allwinner-h616-Add-thermal-sensor-and-thermal-zones.patch
git apply --verbose "$DIR"/arm64-dts-allwinner-sun50i-h616-Add-GPU-node.patch
git apply --verbose "$DIR"/arm64-dts-allwiner-sun50i-h616.dtsi-add-usb-ehci-ohc.patch
git apply --verbose "$DIR"/orangepizero2_dts_set_bldo2_to_1.8v.patch
git apply --verbose "$DIR"/hdmi.dtb.patch
git apply --verbose "$DIR"/arm64-dts-allwinner-sun50i-h616-Add-VPU-node.patch
git apply --verbose "$DIR"/sunxi-info.dtb.patch
git apply --verbose "$DIR"/thermal.dtb.patch
git apply --verbose "$DIR"/cpu-opp-table.dtb.patch
git apply --verbose "$DIR"/pwm.dtb.patch
git apply --verbose "$DIR"/dma.dtb.patch
git apply --verbose "$DIR"/hdmi_audio.dtb.patch
git apply --verbose "$DIR"/gpu.dtb.patch
# I don't really understand what for this patch exists
# git apply --verbose "$DIR"/sram.dtb.patch
git apply --verbose "$DIR"/ths-workaround.uboot.patch
# I'l try to test it with u-boot defaults
#git apply --verbose "$DIR"/r_rsb-to-r_i2c.patch