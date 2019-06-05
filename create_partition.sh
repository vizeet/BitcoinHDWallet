#!/bin/bash

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

partprobe

# create extended partition
(echo n; echo e; echo ; echo ; echo ; echo w) | sudo fdisk $1

partprobe

# create 200 MB partition
(echo n; echo ; echo +200M; echo w) | sudo fdisk $1

partprobe

# change type to empty
(echo t; echo ; echo 0; echo w) | sudo fdisk $1

partprobe

# create linux partition
(echo n; echo ; echo ; echo w) | sudo fdisk $1

# Copy code iso to Empty Partition
part=$(echo "p"| sudo fdisk $1 | grep "^$1" | awk '$NF== "Empty" {print $1}')

dd if=disk.iso of=$part

# Mount Data Partition
part=$(echo "p"| sudo fdisk $1 | grep "^$1" | awk '$NF== "Linux" {print $1}')
mkdir /media/$USER/data
mount $part /media/$USER/data


