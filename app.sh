#!/usr/bin/env bash

#
# Text encryptor and editor for single text file
#
# Author: zhengbaole@huice.com
# Created at: 2021-02-19
#

enc_file="$HOME/jencrypt_encrypted.txt.enc"

tmp_dir=""
plain_file=""


## Show status

show_status() {
	if [ -f $enc_file ]
	then
		echo "Encrypted file exists. "
	else
		echo "Encrypted file does not exist. "
	fi
}


## Wipe all data (dangerous)

wipe_encrypted_data() {
	echo "Delete all encrypted data. This operation is irreversible! Are you sure? [y/n]"
	read result
	if [ "y" == "$result" ]
	then
		rm $enc_file
		echo "Successfully removed all encrypted data. "
	else
		echo "Operation canceled. "
	fi
}


## Clean up

cleanup() {
	remove_tmp_dir
	umount_disk
}


## Delete plain text file

remove_tmp_dir() {
	echo "Delete tmp dir"
}


## Unmount RAM disk

umount_disk() {
	echo "Eject ram disk"
	umount $tmp_dir
	diskutil eject "/dev/$disk_id"
}
		

## Decrypt file and open with vim, if not exists, create new one.

decrypt_and_edit_or_view() {

	echo 'Input your cipher for encryption:'

	read -s cipher

	## Create a RAM disk (default size is 8 MB)

	disk_name="jencrypt-$(date | md5)"
	disk_name=$( echo $disk_name | cut -c1-18)
	echo "Create RAM disk $disk_name"
	diskutil erasevolume HFS+ $disk_name `hdiutil attach -nobrowse -nomount ram://8192`
	tmp_dir="/Volumes/$disk_name"
	plain_file="$tmp_dir/jencrypt_decrypted.txt"

	## Mount RAM disk to tmp dir

	disk_id=$( diskutil list | grep $disk_name | awk '{print $5}')
	echo "RAM disk is at $disk_id"

	if [ ! -d $tmp_dir ]
	then
	    echo "Create tmp dir"
	    mkdir -p $tmp_dir
	fi

	echo "Mount RAM disk"

	## Decrypt file and save to RAM disk

	if [ -f $enc_file ]
	then
	    echo "Decrypt enc file"
	    {
	    	echo $cipher | openssl aes-256-cbc -d -a -in $enc_file -out $plain_file -pass stdin
		} || {
			echo "[ERROR] Decrypt failed! Check your cipher. "
			cleanup
	    	exit -1
		}
	fi

	## Edit or view text, remember save when exit vim

	echo "Edit plain file"
	vim $plain_file

	## Encrypt text again and save as encrypted file

	echo "Encrypt file"
	echo $cipher | openssl aes-256-cbc -a -salt -in $plain_file -out $enc_file -pass stdin

	## Remove and cleanup

	cleanup
}


## Main

echo "    _                                                _   "
echo "   (_)   ___   _ __     ___   _ __   _   _   _ __   | |_ "
echo "   | |  / _ \ | '_ \   / __| | '__| | | | | | '_ \  | __|"
echo "   | | |  __/ | | | | | (__  | |    | |_| | | |_) | | |_ "
echo "  _/ |  \___| |_| |_|  \___| |_|     \__, | | .__/   \__|"
echo " |__/                                |___/  |_|          "
echo "                                                         "
echo "  v1.0                                                   "
echo "                                                         "
echo "                                                         "

while true; do

	sleep 0.5

	echo "0. Exit"
	echo "1. View or edit"
	echo "2. Wipe encrypted data"
	echo "3. Show status"
	echo " "

	echo "What do you want? "
	read result

	case "$result" in
		0 )
			echo "exit"
			exit 0
			;;
		1 )
			decrypt_and_edit_or_view
			exit 0
			;;
		2 )
			wipe_encrypted_data
			exit 0
			;;
		3 )
			show_status
			exit 0
			;;
		* )
			echo ""
			echo "[ERROR] Invalid number! "
			echo ""
			sleep 0.5
			;;

	esac
done

