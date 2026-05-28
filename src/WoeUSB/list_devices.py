#!/usr/bin/env python3

import os
import re
import subprocess


def usb_drive(show_all=False):
    devices_list = []

    lsblk = subprocess.run(["lsblk",
                            "--output", "NAME",
                            "--noheadings",
                            "--nodeps"], stdout=subprocess.PIPE).stdout.decode("utf-8")

    devices = re.sub("sr[0-9]|cdrom[0-9]", "", lsblk).split()

    for device in devices:
        if not is_removable_and_writable_device(device):
            if not show_all:
                continue

        # FIXME: Needs a more reliable detection mechanism instead of simply assuming it is under /dev
        block_device = "/dev/" + device

        device_capacity = subprocess.run(["lsblk",
                                          "--output", "SIZE",
                                          "--noheadings",
                                          "--nodeps",
                                          block_device], stdout=subprocess.PIPE).stdout.decode("utf-8").strip()

        device_model = subprocess.run(["lsblk",
                                       "--output", "MODEL",
                                       "--noheadings",
                                       "--nodeps",
                                       block_device], stdout=subprocess.PIPE).stdout.decode("utf-8").strip()

        if device_model != "":
            devices_list.append([block_device, block_device + "(" + device_model + ", " + device_capacity + ")"])
        else:
            devices_list.append([block_device, block_device + "(" + device_capacity + ")"])

    return devices_list


def is_removable_and_writable_device(block_device_name):
    sysfs_block_device_dir = "/sys/block/" + block_device_name
    removable_path = sysfs_block_device_dir + "/removable"
    ro_path = sysfs_block_device_dir + "/ro"

    if os.path.isfile(removable_path) and os.path.isfile(ro_path):
        with open(removable_path) as removable:
            removable_content = removable.read()

        with open(ro_path) as ro:
            ro_content = ro.read()

        if removable_content.strip("\n") == "1" and ro_content.strip("\n") == "0":
            return True
        else:
            return False
    else:
        return False


def dvd_drive():
    devices_list = []
    find = subprocess.run(["find", "/sys/block",
                           "-maxdepth", "1",
                           "-mindepth", "1"], stdout=subprocess.PIPE).stdout.decode("utf-8").split()
    devices = []
    for device in find:
        tmp = re.findall("sr[0-9]", device)

        if tmp == []:
            continue

        devices.append([device, tmp[0]])

    for device in devices:
        optical_disk_drive_devfs_path = "/dev/" + device[1]

        with open(device[0] + "/device/model", "r") as model:
            model_content = model.read().strip()

        devices_list.append([optical_disk_drive_devfs_path, optical_disk_drive_devfs_path + " - " + model_content])

    return devices_list
