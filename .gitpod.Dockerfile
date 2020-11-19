FROM gitpod/workspace-full
USER gitpod
RUN sudo apt-get update && \
    sudo apt-get install -y \
     gcc-aarch64-linux-gnu  \
     g++-aarch64-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

# Install custom tools, runtimes, etc.
# For example "bastet", a command-line tetris clone:
# RUN brew install bastet
#
# More information: https://www.gitpod.io/docs/config-docker/
