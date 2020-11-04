#!/bin/bash
echo "Cloning dependencies"
git clone --depth=1  https://github.com/d4rk-lucif3r/LuciferKernel.git -b circleci-nonoc
git branch
cd LuciferKernel
git clone --depth=1 -b master https://github.com/kdrag0n/proton-clang clang
git clone https://github.com/d4rk-lucif3r/Anykernel3-Tissot.git  --depth=1 AnyKernel
echo "Done"
KERNEL_DIR=$(pwd)
REPACK_DIR="${KERNEL_DIR}/AnyKernel"
IMAGE="${KERNEL_DIR}/arch/arm64/boot/Image.gz"
DTB_T="${KERNEL_DIR}/arch/arm64/boot/dts/qcom/msm8953-qrd-sku3-tissot-treble.dtb"
DTB="${KERNEL_DIR}/arch/arm64/boot/dts/qcom/msm8953-qrd-sku3-tissot-nontreble.dtb"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
export PATH="$(pwd)/clang/bin:$PATH"
export KBUILD_COMPILER_STRING="$($kernel/clang/bin/clang --version | head -n 1 | perl -pe 's/\((?:http|git).*?\)//gs' | sed -e 's/  */ /g' -e 's/[[:space:]]*$//' -e 's/^.*clang/clang/')"
export ARCH=arm64
export KBUILD_BUILD_USER=d4rklucif3r
export KBUILD_BUILD_HOST=circleci
# Compile plox
function compile() {
    make -j$(nproc)  ARCH=arm64 tissot_defconfig
    make -j$(nproc)  \
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
    zip -r9 LuciferKernel+V3.zip *
    curl https://bashupload.com/LuciferKernel+V3.zip --data-binary @LuciferKernel+V3.zip
}
compile
zipping

