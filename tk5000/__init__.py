#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

import argparse
import glob
import re

import serial

# Import color output package, fall back to normal output of that is not
# installed.
try:
    import termcolor
except ImportError:
    print('Install the `termcolor` Python module to get color output')
    termcolor = lambda x: None
    termcolor.cprint = lambda x, *args, **kwargs: print(x)


error_code_messages = {
    0: 'Unbekannter Fehler',
    1: 'Falsches Passwort',
}


class Tracker(object):
    ok_pattern = re.compile(br'\$OK:\w+=([^,\n\r]+)(?:,([^,\n\r]*))*')
    err_pattern = re.compile(br'\$ERR:(?:\w+=)?(\d+)')

    def __init__(self, dev, password):
        self.dev = dev
        self.dev.baudrate = 15200
        self.password = password

    @property
    def version(self):
        self._execute(b'VER')
        return self._parse_oneline_result()

    def get_positions(self):
        self._execute(b'DLREC', b'0', b'0')
        return self._get_multiline_result()

    @property
    def location(self):
        self._execute(b'GETLOCATION')
        return self._get_oneline_result()

    def get_sos(self):
        self._execute(b'EMSMS', b'?')
        result = self._parse_oneline_result()
        return result[0]

    sos = property(get_sos)

    def _execute(self, command, *params):
        if len(params) > 0:
            param_str = b',' + b','.join(map(bytes, params))
        else:
            param_str = b''

        parts = [
            b'$WP+',
            command,
            b'=',
            self.password,
            param_str,
            b'\r'
        ]

        to_send = b''.join(parts)
        termcolor.cprint('← ' + to_send.decode().strip(), 'blue')
        self.dev.write(to_send)

    def _get_oneline_result(self):
        return self.dev.readline()

    def _get_multiline_result(self, last=b'$MSG:'):
        status = self._parse_oneline_result()

        lines = []
        while True:
            line = self.dev.readline()
            lines.append(line)
            if line.startswith(last):
                break

        return status, lines[:-1], lines[-1]

    def _parse_oneline_result(self):
        result = self._get_oneline_result()

        parsed = False
        success = False

        color = 'yellow'

        m = self.ok_pattern.search(result)
        if m:
            parsed = True
            success = True
            return_val = m.groups()
            color = 'green'

        m = self.err_pattern.search(result)
        if m:
            parsed = True
            error_code = int(m.group(1))
            color = 'red'

        termcolor.cprint('→ ' + result.decode().strip(), color)

        if not parsed:
            raise RuntimeError('Answer from tracker could not be parsed. Was ' + str(result))

        if not success:
            raise RuntimeError('Error from tracker: ' + error_code_messages[error_code])

        return return_val


def interpret_raw_positions(lines):
    result = []
    for line in lines:
        parts = line.strip().split(b',')
        result.append((parts[1], parts[3], parts[2]))

    return result


def store_positions_as_tsv(filename, positions):
    with open(filename, 'wb') as f:
        f.write(b'date,latitude,longitude\n')
        for position in positions:
            f.write(b','.join(position) + b'\n')


def main():
    options = _parse_args()

    print()

    serial_devices = glob.glob('/dev/serial/by-id/*')
    if len(serial_devices) == 0:
        raise RuntimeError('There are no serial devices at all.')
    elif len(serial_devices) > 2:
        raise RuntimeError("There is more than a single serial device, I don't know what to do.")

    serial_device = serial_devices[0]


    with serial.Serial(serial_device) as dev:
        tracker = Tracker(dev, b'0000')

        print(tracker.version)
        print()
        print(tracker.sos)
        print()
        print(tracker.location)
        print()

        status, positions_raw, message = tracker.get_positions()
        positions = interpret_raw_positions(positions_raw)
        store_positions_as_tsv('positions.tsv', positions)


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
