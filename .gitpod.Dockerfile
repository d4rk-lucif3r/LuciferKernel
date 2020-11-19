FROM gitpod/workspace-full
USER gitpod
RUN sudo apt-get update && \
    sudo apt-get install -y bc build-essential zip curl libstdc++6 git wget python gcc clang libssl-dev  rsync flex bison gcc-aarch64-linux-gnu 
   

# Install custom tools, runtimes, etc.
# For example "bastet", a command-line tetris clone:
# RUN brew install bastet
#
# More information: https://www.gitpod.io/docs/config-docker/
