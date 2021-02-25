#!/usr/bin/env python3

#
# Text encryptor and editor for folder
#
# Author: zhengbaole@huice.com
# Created at: 2021-02-20
#

import os
import platform
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from getpass import getpass
from hashlib import md5
from time import sleep

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

observer: Observer
tmp_dir = ''
disk_id = ''
ram_disk_dir = ''
plain_file = ''
cipher = ''
enc_file = ''
unmounted = False


# Clean up
def clean_up():
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)

    global observer
    if observer is not None:
        observer.stop()
        observer.join()

    disk_dev = f'/dev/{disk_id}'

    if os.path.exists(disk_dev):
        cmd_eject = f'diskutil eject {disk_dev}'
        print(os.popen(cmd_eject).read())


# Generate random hex string
def random_hex():
    return md5(str(datetime.now().timestamp().as_integer_ratio()).encode()).hexdigest()[0:18]


# Do on ram disk volume file system has any change
def on_change(event):
    global unmounted

    if not os.path.exists(ram_disk_dir):
        if not unmounted:
            print("Volume was ejected.")
            unmounted = True
            return

    if unmounted:
        return

    if len(ram_disk_dir) < 1 or len(plain_file) < 1:
        print("[ERROR] Directory not initialized. ")
        clean_up()
        sys.exit(-1)

    if event.src_path.split('/')[-1] in ['.DS_Store', '.fseventsd', '.Trashes']:
        return

    # print(f"[INFO] {event.src_path} has changed! ")

    # package and encrypt file and override enc file
    filename_list = os.listdir(ram_disk_dir)

    filenames = []
    for filename in filename_list:
        filenames.append(f'"{filename}"')

    files_string = ' '.join(filenames)

    cmd_package = f'cd {ram_disk_dir} && tar -cf {plain_file} {files_string}'
    os.popen(cmd_package).read()

    cmd_encrypt = f'echo "{cipher}" | openssl aes-256-cbc -a -salt -in "{plain_file}" -out "{enc_file}" -pass stdin'
    os.popen(cmd_encrypt).read()


# Print banner
def print_banner():
    print(
        '''
    _                                                _   
   (_)   ___   _ __     ___   _ __   _   _   _ __   | |_ 
   | |  / _ \ | '_ \   / __| | '__| | | | | | '_ \  | __|
   | | |  __/ | | | | | (__  | |    | |_| | | |_) | | |_ 
  _/ |  \___| |_| |_|  \___| |_|     \__, | | .__/   \__|
 |__/                                |___/  |_|          

 v2.0.15
        '''
    )


# Main
def mount_volume():
    # get password from terminal input

    enc_file_exists = os.path.exists(enc_file) and os.path.isfile(enc_file)

    global cipher
    cipher = getpass("Input your password for encryption:\n")

    if not enc_file_exists:
        cipher_confirm = getpass("Input your password again:\n")
        if cipher != cipher_confirm:
            print("Passwords are different! ")
            sys.exit(-1)

    # create RAM disk and mount

    disk_name = f'jencrypt-{random_hex()[0:10]}'
    print(f'Create RAM disk {disk_name}')

    cmd_create_tam_disk = f'diskutil erasevolume HFS+ {disk_name} `hdiutil attach -nobrowse -nomount ram://8192`'
    print(cmd_create_tam_disk)
    print(os.popen(cmd_create_tam_disk).read())

    global ram_disk_dir
    ram_disk_dir = f'/Volumes/{disk_name}'
    print(f'RAM disk is at {ram_disk_dir}')

    print("RAM disk mounted")

    # create tmp dir

    cmd_get_tmp_dir = "diskutil list | grep %s | awk '{print $5}'" % disk_name
    print(cmd_get_tmp_dir)

    global disk_id
    disk_id = os.popen(cmd_get_tmp_dir).read().strip()

    global tmp_dir
    tmp_dir = os.path.join(tempfile.gettempdir(), random_hex())

    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    print(f'Temp dir is {tmp_dir}')

    global plain_file
    plain_file = os.path.join(tmp_dir, 'jencrypt-decrypted.tar.gz')

    # if find encrypted file, decrypt and extract it to tmp dir
    if enc_file_exists:

        print("Encrypted file exists, decrypt and extract")

        # todo when cipher error, show warning
        cmd_decrypt = f'echo "{cipher}" | openssl aes-256-cbc -d -a -in {enc_file} -out {plain_file} -pass stdin'

        print(os.popen(cmd_decrypt).read())

        cmd_extract = f'tar -xf {plain_file} -C {ram_disk_dir}'

        if not os.path.exists(plain_file):
            print("[ERROR] Decryption failed, check your password. ")
            sys.exit(-1)

        print(os.popen(cmd_extract).read())

    # watch ram disk volume change and handle event
    patterns = '*'
    ignore_patterns = "fseventsd|DS_Store"
    ignore_directories = False
    case_sensitive = True
    watch_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

    watch_handler.on_created = on_change
    watch_handler.on_deleted = on_change
    watch_handler.on_modified = on_change
    watch_handler.on_moved = on_change

    global observer
    observer = Observer()
    observer.schedule(watch_handler, ram_disk_dir, recursive=True)
    observer.start()

    print("Listening volume file changes and sync, exit with Ctrl-C. ")

    try:
        while True:
            sleep(1)
            if unmounted:
                clean_up()
                print("Jencrypt exit now. ")
                sys.exit(0)

    except KeyboardInterrupt:
        print("\nEncrypting and cleaning temporary file. ")

        observer.stop()
        observer.join()

        # clean up tmp dir
        clean_up()

        print("Jencrypt exit now. ")


# Wipe all data (dangerous)
def wipe_encrypted_data():
    wipe = input("Delete all encrypted data. This operation is irreversible! Are you sure? [y/n] \n")
    if "y" == wipe:
        if os.path.exists(enc_file):
            os.remove(enc_file)
            print("Successfully removed all encrypted data. ")
        else:
            print("Encrypted file does not exist. ")
    else:
        print("Operation canceled. ")


# Show status
def show_status():
    global enc_file
    exists = os.path.exists(enc_file)
    if exists:
        print("Encrypted file exists. ")
    else:
        print("Encrypted file does not exist. ")


# Assert all needed program installed
def assert_cmd_exists():
    cmd_list = [
        ['tar', '-h'],
        ['openssl', '-h'],
        ['diskutil', 'list']
    ]

    error_exists = False

    for cmd in cmd_list:
        p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        p.communicate()
        if 0 != p.returncode:
            error_exists = True
            print(f'[ERROR] {cmd[0]} is not installed. ')

    if error_exists:
        sys.exit(-1)


def assert_os_support():
    if "Darwin" != platform.system():
        print("[ERROR] This program can not run on this platform. It supports macOS only. ")
        sys.exit(-1)


def main():
    print_banner()

    assert_os_support()

    assert_cmd_exists()

    home_dir = os.getenv("HOME")
    global enc_file
    enc_file = f'{home_dir}/jencrypt_encrypted_v2.enc'

    while True:
        sleep(0.5)

        print(
            ''' 
0. Exit
1. Mount private volume (default)
2. Wipe encrypted data
3. Show status"
            '''
        )

        result = input("What do you want? \n").strip()

        if "0" == result:
            print("Jencrypt exit now. ")
            break
        elif "1" == result:
            mount_volume()
            break
        elif "2" == result:
            wipe_encrypted_data()
            break
        elif "3" == result:
            show_status()
            break
        else:
            print("[ERROR] Invalid number! ")
            sleep(0.5)


if __name__ == '__main__':
    sys.exit(main())
