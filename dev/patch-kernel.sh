#!/usr/bin/env bash

set -x

DIR="$(dirname "$0")/../scripts/configs/patches/kernel"

git apply --verbose "$DIR"/0000-btt-cb1.patch
git apply --verbose "$DIR"/drv-soc-sunxi-sram-Add-SRAM-C1-H616-handling.patch
git apply --verbose "$DIR"/realtek-driver.patch
git apply --verbose "$DIR"/thermal.patch
git apply --verbose "$DIR"/axp1530.patch
git apply --verbose "$DIR"/axp1530.1.patch
