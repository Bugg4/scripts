#!/usr/bin/env python3

import subprocess as sp


SOURCE_DIR = "${HOME}/dotfiles"  # Root directory containing actual dotfiles
TARGET_DIR = "/tmp/linkman-dummy/"  # Root directory where symlinks will be created


def shell(cmd):
    return sp.run(cmd, shell=True, check=True)


if __name__ == "__main__":
    res = shell(f"ln -sfv {SOURCE_DIR}/* --target-directory {TARGET_DIR}")
