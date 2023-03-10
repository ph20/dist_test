#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Detect locally mounted disk (make sure it is local) with at least X MB free space,
create Z files of size Y, run Z “dd” processes which where each process will fill the selected file with
Data and print time took to complete the work.
"""

import sys
import time
import tempfile
import subprocess

try:
    import psutil
except ImportError:
    print('Please install psutil module')
    sys.exit(1)


DD_BIN = '/usr/bin/dd'


def mega_bytes(megabytes):
    return megabytes * 1024 * 1024


def get_local_mount_points():
    for part in psutil.disk_partitions():
        if part.device.startswith('/dev/sd') and part.mountpoint.startswith('/'):
            yield part.mountpoint


def filter_free_space(mount_points, min_free_space):
    mount_point_list = []
    for mount_point in mount_points:
        try:
            free_space = psutil.disk_usage(mount_point).free
        except PermissionError as e:
            free_space = 0
            print(f'WARN: Can\'t obtaine free space for {mount_point}: {e}', file=sys.stderr)
        if free_space > min_free_space:
            mount_point_list.append(mount_point)
    return mount_point_list


def get_root_dir(min_free_space):
    path_list = filter_free_space(get_local_mount_points(), min_free_space)
    if not path_list:
        print('No mount points with enough free space', file=sys.stderr)
        sys.exit(1)
    return path_list[0]


def test_write(file_size, file_count, dir_path):
    dd_ps_pool = []
    end_time = start_time = time.time()
    for i in range(file_count):
        file_path = f'{dir_path}/file{i}'
        print(f'Creating file {file_path} with size {file_size}...')
        dd_ps = subprocess.Popen([DD_BIN, 'if=/dev/zero', f'of={file_path}', f'bs={file_size}', 'count=1'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        dd_ps_pool.append(dd_ps)

    while True:
        # break if all processes are done
        if all([dd_ps.poll() is not None for dd_ps in dd_ps_pool]):
            end_time = time.time()
            break
    return end_time - start_time


def main(min_free_space, file_size, file_count):
    root_dir = get_root_dir(min_free_space)
    with tempfile.TemporaryDirectory(dir=root_dir) as tmp_dir:
        time_took = test_write(file_size, file_count, tmp_dir)
    return time_took


if __name__ == '__main__':
    try:
        min_free_space, file_size, file_count = sys.argv[1:]
        min_free_space, file_size = mega_bytes(int(min_free_space)), mega_bytes(int(file_size))
        file_count = int(file_count)
    except ValueError:
        print(f'Usage: {sys.argv[0]} min_free_space (MB) file_size (MB) file_count. F.e. 5000 100 10', file=sys.stderr)
        sys.exit(1)

    time_took = main(min_free_space, file_size, file_count)
    print(f'Time took: {time_took:.2f} seconds')
