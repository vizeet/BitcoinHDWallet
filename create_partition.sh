#!/bin/bash

# delete all partitions
for l in $(echo "p"| sudo fdisk /dev/sdb | grep "^$1"| awk '{print $1}')
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

# Empty Partition
part=$(echo "p"| sudo fdisk /dev/sdb | grep "^/dev/sdb" | awk '$7== "Empty" {print $1}')

./prepare_iso.sh

dd if=disk.iso of=$part
