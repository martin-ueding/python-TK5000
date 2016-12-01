#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

import argparse
import glob

import serial


def main():
    options = _parse_args()

    serial_devices = glob.glob('/dev/serial/by-id/*')
    if len(serial_devices) == 0:
        raise runtime_error('There are no serial devices at all.')
    elif len(serial_devices) > 2:
        raise runtime_error("There is more than a single serial device, I don't know what to do.")

    serial_device = serial_devices[0]


    with serial.Serial(serial_device) as dev:
        print(dev.name)


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
