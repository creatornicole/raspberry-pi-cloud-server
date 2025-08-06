## 🐾 Steps to Set-Up NAS

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Backup and format MicroSD
3. Start Raspberry Pi Images once it has been installed - choose your device, Raspberry Pi OS Lite (64-Bit) and your MicroSD card
4. Change settings: set up username and password, enable SSH, (optional) choose time zone
5. Remove MicroSD card once it's ready and insert into Raspberry Pi
6. Connect Raspberry Pi to network and power it up
7. Connect wireless using SSH (will need username and password, IP address of Pi (find out by connecting to router))
	- use [PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) - lets you remotely access the command line of another device (like here the Rasperry Pi) from WIndows PC
	- Linux/macOS have built-in SSH clients in the terminal; Windows doesn't, PuTTY fills that gap
8. Set a static IP address for your Pi
9. Update and upgrade everything once you are connected via SSH to your Raspberry Pi (simply good practice)
   ```
	sudo apt update
	sudo apt upgrade
	```
10. Find your storage that is connected to your Pi (sda, not mounted yet)
    ```
	lsblk
	```
11. Partition storage
    ```
	sudo fdisk /dev/sda
	m # Command (m for help)
	d # Delete a partition
	w # Write table to disk and exit

	# Create new fresh partition
	sudo fdisk /dev/sda
	n # Add a new partition
	w # Write table to disk and exit
	```
12. Format storage/ the newly created partition
    ```
	sudo mkfs.ext4 /dev/sda1
	```
13. Mount drive to system (so that we can access it)
    ```
	# Create mount point = new directory inside the system
	cd ..
	cd ..
	ls # show directories etc. (correct if you can see home, mnt, tmp, ...)
	cd /mnt/
	sudo mkdir mystorage
	ls
	cd ..

	# Mount drive to system
	sudo mount /dev/sda1 /mnt/mystorage
	
	```
14. Automate mount process (= mount drive to system everytime it is started; otherwise you would have to repeat it)
    ```
	sudo nano /etc/fstab
	```
	- add following to the end of the file before the comments:
	  */dev/sda1 /mnt/mystorage ext4 defaults,noatime 0 1*
	- Strg + X -> Y -> Enter
15. Reboot the system to check whether the drive is mounted automatically
    ```
	sudo reboot
	lsblk
	```
16. Create shared folder
    ```
	cd ..
	cd ..
	cd mnt/mystorage
	sudo mkdir shared
	ls
	```
17. Grant read and write permissions to all users on the system
    ```
	sudo chmod -R 777 /mnt/mystorage/shared
	```
18. Install Samba (so that the newly created shared folder can be shared)
    ```
	sudo apt install samba samba-common-bin
	```
19. Modify the config file of Samba to tell it to shared our folder over the network
    ```
	sudo nano /etc/samba/smb.conf
	```
	- add to the end of the file
	  *\[shared\]*
	  *path=/mnt/mystorage/shared*
	  *writeable=Yes*
	  *create mask=0777*
	  *directory mask=0777*
	  *public=no*
	- Strg + X -> Y -> Enter
20. Restart Samba to load the new configuration
    ```
	sudo systemctl restart smbd
	```
21. Grant drive access to user
	- \<username> is your username on the Pi
	- entering new password will add you as user to Samba
    ```
	sudo smbpasswd -a <username>
	```
22. Create a txt-file to test the NAS system
    ```
    cd /mnt/mystorage/shared
    touch helloworld.txt
    ls
    sudo nano helloworld.txt # add some content
    ```
23. Windows: go to "This PC" and enter "\\\\\<ip>\shared" -> enter your login credential to **Samba**
24. Now that we know that everything is working, we can add our Raspberry Pi to our network locations
	- right click under "This PC" -> add network address -> \\\\\<ip>\shared