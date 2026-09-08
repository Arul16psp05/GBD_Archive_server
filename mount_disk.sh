# Find Archive data disk 
# $ lsblk
#sda           8:0    0   3.6T  0 disk 
#└─sda2        8:2    0   3.6T  0 part
#$ cd GBD_Archive_server
sudo mount -o uid=$(id -u),gid=$(id -g) /dev/sda2 pulsar_data
