Copy the image to the computer:

lsblk

sudo dcfldd if=/dev/sd- of=imagename.img
sudo sync

sudo modprobe loop
sudo losetup -f
sudo losetup /dev/loop0 myimage.img

sudo partprobe /dev/loop0
sudo gparted /dev/loop0
sudo losetup -d /dev/loop0
fdisk -l myimage.img
truncate --size=$[(9181183+1)*512] myimage.img

Then run the burn.sh script
