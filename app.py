#!/usr/bin/python3

#
# Text encryptor and editor for folder
#
# Author: zhengbaole@huice.com
# Created at: 2021-02-20
#

import os
import shutil
import sys
import tempfile
from datetime import datetime
from hashlib import md5
from time import sleep

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

observer = None


# Clean up
def clean_up():
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)

    if observer is not None:
        observer.stop()
        observer.join()

    cmd_eject = f'diskutil eject /dev/{disk_id}'
    print(os.popen(cmd_eject).read())


# Generate random hex string
def random_hex():
    return md5(str(datetime.now().timestamp().as_integer_ratio()).encode()).hexdigest()[0:18]


# Do on ram disk volume file system has any change
def on_change(event):
    if len(ram_disk_dir) < 1 or len(plain_file) < 1:
        print("[ERROR] Directory not initialized")
        clean_up()
        sys.exit(-1)

    print(f"Hey, {event.src_path} has changed!")
    # package and encrypt file and override enc file
    # todo ignore .fseventsd & .DS_Store
    # fixme file or dir name contains space, tar will no work
    cmd_package = f'cd {ram_disk_dir} && tar -cf {plain_file} $(ls {ram_disk_dir})'
    print(os.popen(cmd_package).read())
    cmd_encrypt = f'echo "{cipher}" | openssl aes-256-cbc -a -salt -in "{plain_file}" -out "{enc_file}" -pass stdin'
    print(os.popen(cmd_encrypt).read())


# Print banner
def print_banner():
    print("    _                                                _   ")
    print("   (_)   ___   _ __     ___   _ __   _   _   _ __   | |_ ")
    print("   | |  / _ \ | '_ \   / __| | '__| | | | | | '_ \  | __|")
    print("   | | |  __/ | | | | | (__  | |    | |_| | | |_) | | |_ ")
    print("  _/ |  \___| |_| |_|  \___| |_|     \__, | | .__/   \__|")
    print(" |__/                                |___/  |_|          ")
    print("                                                         ")
    print("  v2.0                                                   ")
    print("                                                         ")
    print("                                                         ")


# Main
if __name__ == '__main__':

    print_banner()

    # fixme password should not be shown
    cipher = input("Input your cipher for encryption:\n")

    home_dir = os.getenv("HOME")
    enc_file = f'{home_dir}/jencrypt_encrypted_v2.enc'

    # create RAM disk and mount

    disk_name = random_hex()
    print(f'Create RAM disk {disk_name}')

    cmd_create_tam_disk = f'diskutil erasevolume HFS+ {disk_name} `hdiutil attach -nobrowse -nomount ram://8192`'
    print(cmd_create_tam_disk)
    print(os.popen(cmd_create_tam_disk).read())

    ram_disk_dir = f'/Volumes/{disk_name}'
    print(f'RAM disk is at {disk_name}')

    print("RAM disk mounted")

    # create tmp dir

    cmd_get_tmp_dir = "diskutil list | grep %s | awk '{print $5}'" % disk_name
    print(cmd_get_tmp_dir)
    disk_id = os.popen(cmd_get_tmp_dir).read()

    tmp_dir = os.path.join(tempfile.gettempdir(), random_hex())

    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    print(f'Temp dir is {tmp_dir}')

    plain_file = os.path.join(tmp_dir, 'jencrypt-decrypted.tar.gz')

    # if find encrypted file, decrypt and extract it to tmp dir
    if os.path.exists(enc_file) and os.path.isfile(enc_file):
        print("Encrypted file exists, decrypt and extract")
        cmd_decrypt = f'echo "{cipher}" | openssl aes-256-cbc -d -a -in {enc_file} -out {plain_file} -pass stdin'
        print(os.popen(cmd_decrypt).read())
        cmd_extract = f'tar -xf {plain_file} -C {ram_disk_dir}'
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

    observer = Observer()
    observer.schedule(watch_handler, ram_disk_dir, recursive=True)
    observer.start()

    print("Listening volume file changes and sync, exit with Ctrl-C. ")

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        # clean up tmp dir
        clean_up()
