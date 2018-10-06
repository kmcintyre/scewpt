#!/bin/bash
if [ -d /ramdisk ]
then
  echo 'cleanup'
  sudo rm -rf /ramdisk/*  
else
  echo 'create'
  sudo mkdir /ramdisk
  sudo chmod 777 /ramdisk
fi
if mount | grep /ramdisk > /dev/null; then
    echo "unmount"
    sudo umount -v /ramdisk/
fi
echo "create mount"
sudo mount -t tmpfs -o size=256M tmpfs /ramdisk
