#!/bin/bash
echo "Cloning dependencies"
git clone --depth=1  https://github.com/d4rk-lucif3r/LuciferKernel.git -b NonOC
cd LuciferKernel
git clone --depth=1 -b master https://github.com/kdrag0n/proton-clang clang
git clone https://github.com/d4rk-lucif3r/Anykernel3-Tissot.git  --depth=1 AnyKernel
git clone $SEND_SCRIPT
KERNEL_DIR=$(pwd)
REPACK_DIR="${KERNEL_DIR}/AnyKernel"
IMAGE="${KERNEL_DIR}/out/arch/arm64/boot/Image.gz"
DTB_T="${KERNEL_DIR}/out/arch/arm64/boot/dts/qcom/msm8953-qrd-sku3-tissot-treble.dtb"
DTB="${KERNEL_DIR}/out/arch/arm64/boot/dts/qcom/msm8953-qrd-sku3-tissot-nontreble.dtb"
SEND_DIR="${KERNEL_DIR}/telegram.sh"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
export PATH="$(pwd)/clang/bin:$PATH"
export ARCH=arm64
export KBUILD_BUILD_USER=d4rklucif3r
export KBUILD_BUILD_HOST=circleci
# Compile plox
function compile() {
    make -j$(nproc) O=out ARCH=arm64 lucifer-tissot_defconfig
    make -j$(nproc) O=out \
                    ARCH=arm64 \
                      CC=clang \
                      CROSS_COMPILE=aarch64-linux-gnu- \
                      CROSS_COMPILE_ARM32=arm-linux-gnueabi- \

    cd $REPACK_DIR
    mkdir kernel
    mkdir dtb-treble
    mkdir dtb-nontreble

    if ! [ -a "$IMAGE" ]; then
        exit 1
        echo "There are some issues with image"
    fi
    cp $IMAGE $REPACK_DIR/kernel/

    if ! [ -a "$DTB" ]; then
        exit 1
        echo "There are some issues dtb "
    fi
    cp $DTB $REPACK_DIR/dtb-nontreble/

    if ! [ -a "$DTB_T" ]; then
        exit 1
        echo "There are some issues dtb treble"
    fi
    cp $DTB_T $REPACK_DIR/dtb-treble/
}
# Zipping
function zipping() {
    cd $REPACK_DIR || exit 1
    zip -r9 LuciferKernel+V3+NonOC.zip *
    cd $SEND_DIR   || exit 1
    echo "Changing Dir to Send FIle"
    ./telegram -t $TELEGRAM_TOKEN -c $TELEGRAM_CHAT -f $REPACK_DIR/LuciferKernel+V3+NonOC.zip "File Sent through CircleCi"
   #curl https://bashupload.com/LuciferKernel+V3.zip --data-binary @LuciferKernel+V3.zip
}
compile
zipping

