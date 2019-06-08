#!/bin/bash

sudo partprobe $1

# unmount partitions
for l in $(echo "p"| sudo fdisk $1 | grep "^$1"| awk '{print $1}')
do
umount $l
done

# delete all partitions
for l in $(echo "p"| sudo fdisk $1 | grep "^$1"| awk '{print $1}')
do
if [ $(echo "p"| sudo fdisk /dev/sdb | grep "^$1"| awk '{print $1}' | wc -l) == 1 ]
then
(echo d; echo w) | sudo fdisk $1
else
(echo d; echo 1; echo w) | sudo fdisk $1
fi
done

sudo partprobe $1

# create extended partition
(echo n; echo e; echo ; echo ; echo ; echo w) | sudo fdisk $1

sudo partprobe $1

# create 200 MB partition
(echo n; echo l; echo ; echo +200M; echo w) | sudo fdisk $1

sudo partprobe $1

# change type to empty
(echo t; echo ; echo 0; echo w) | sudo fdisk $1

sudo partprobe $1

# Copy code iso to Empty Partition
part=$(echo "p"| sudo fdisk $1 | grep "^$1" | awk '$NF== "Empty" {print $1}')

sudo dd if=disk.iso of=$part

# Change Partition type from Empty to Linux
partnum=$(echo "p"| sudo fdisk $1 | grep "^$1" | awk '$NF== "Empty" {print substr($1,9)}')
(echo t; echo $partnum; echo 83; echo w) | sudo fdisk $1

#sudo partprobe $1

# create linux partition
(echo n; echo l; echo ; echo ; echo w) | sudo fdisk $1

sudo partprobe $1

# Mount Data Partition
part=$(echo "p"| sudo fdisk $1 | grep "^$1" | tail -n 1 | awk '$NF== "Linux" {print $1}')

echo part=$part

sudo /sbin/mkfs.ext4 -L data $part

sudo mkdir -p /media/$USER/data
sudo mount $part /media/$USER/data
