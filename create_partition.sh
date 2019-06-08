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
(echo d; echo 1; echo w) | sudo fdisk $1
done

sudo partprobe $1

# create extended partition
(echo n; echo e; echo ; echo ; echo ; echo w) | sudo fdisk $1

sudo partprobe $1

# create 200 MB partition
(echo n; echo ; echo +200M; echo w) | sudo fdisk $1

sudo partprobe $1

# change type to empty
(echo t; echo ; echo 0; echo w) | sudo fdisk $1

sudo partprobe $1

# create linux partition
(echo n; echo ; echo ; echo w) | sudo fdisk $1

sudo partprobe $1

# Copy code iso to Empty Partition
part=$(echo "p"| sudo fdisk $1 | grep "^$1" | awk '$NF== "Empty" {print $1}')

sudo dd if=disk.iso of=$part

# Mount Data Partition
part=$(echo "p"| sudo fdisk $1 | grep "^$1" | awk '$NF== "Linux" {print $1}')
sudo mkdir /media/$USER/data
sudo mount $part /media/$USER/data


