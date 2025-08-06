# raspberry-pi-nas
  
This project implements a personal Network-Attached Storage (NAS) system with secure VPN access for remote connectivity on a Raspberry Pi. It acts as your private storage, always accessible allowing you to store, access, and share files over your network. A Python script enables automated weekly and monthly backups, ensuring your data is regularly and reliably saved.


## 📑 Table of Contents
  
1. [🧭 Project Goals](#-project-goals)
2. [🔧 Hardware](#hardware)
3. [⚙️ Software](#software)
4. [📋 Setup Instructions](#setup-instructions)
5. [💡 Things to Improve](#things-to-improve)
6. [📄 References](#references)


## 🧭 Project Goals
    
- 💾 **Centralized file storage and backup**  
  Provide a reliable way to store and back up personal files on a Raspberry Pi-powered NAS
- 🕒 **Scheduled** backups  
  Automatically back up data (e.g. from a laptop or phone) to the NAS on a regular schedule
- 🌍 **Remote access from anywhere**  
  Enable secure access to stored data globally via a VPN connection
- 📱 **Cross-device compatibility**  
  Ensure access to files from various devices (PCs, smartphones, tablets) regardless of the operating system
- 🗂️ **Web-based file interface**  
  Set up a browser-accessible interface (e.g. Nextcloud or File Browser) for convenient file management
- 💻 **Execute programs remotely**  
  Allow execution of program files (e.g. Python scripts -> toolbox) directly on the Raspberry Pi without needing to download them
- 🎮 **Game storage and remote access**  
  Explore the feasibility of storing games on the NAS and running them remotely, possibly via streaming or network mounts
- 🔐 **User-specific access control**  
  Implement user account management with customizable access rights and folder-level permissions


## 🔧 Hardware
  
- Raspberry Pi 4 (4GB RAM)
- Power Supply
- [Cooling Case](https://www.amazon.de/Miuzei-Raspberry-K%C3%BChlk%C3%B6rper-AUS-Schalter-kompatibel/dp/B08FHN6HX8/ref=sr_1_6?__mk_de_DE=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=5FPFBSAKBP9Z&dib=eyJ2IjoiMSJ9.rWEIGvFsseclRI2s8bgV39bF7XG7All8_g-AhRiQid9On6EFy_rC3N48WLd0AZfpFyoY1yVegiUlpzOjdMY02tNz_q04X9RcBukerVcsKd1X5Ksz04cGkgiOlWKvAJWBDdGMJrNKNHcTDyuuS8awbm4qIoeOop1SYBjb9YFnWyxWGprodjpeCNQjhK6w-UeHPfyRvkXwpvyVpLXbZnU8ykaIvxnAhbBK20tSAk2qo0A.rnqKbW4D1ynZZ0WTLVxQIZIBes_NIh7qFl9iISxBQw4&dib_tag=se&keywords=miuzei+case+for+raspberry+4&qid=1753211869&sprefix=miuzei+case+for+raspberry+4%2Caps%2C91&sr=8-6)  
- MicroSD card (32 GB)
- [External Storage (1 TB)](https://www.mediamarkt.de/de/product/_crucial-p3-plus-nvme-m2-2280ss-festplatte-1000-gb-ssd-m2-via-nvme-intern-2817721.html)
- [Case for SSD](https://www.mediamarkt.de/de/product/_isy-ise-1000-gy-nvme-ssd-gehause-grau-2876271.html)
- Ethernet Cable
- [Shelly Plug S MTR Gen3](https://kb.shelly.cloud/knowledge-base/shelly-plug-s-mtr-gen3) (for remote power control)


## ⚙️ Software
  
| Component                                                                   | Purpose                                                                                                                                                   |
| --------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [🍓 Raspberry Pi Imager](https://www.raspberrypi.com/software/)             | simplifies the process of installing an operating system onto a Raspberry Pi's SD card                                                                    |
| [🖥️ PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) | terminal emulator used to securely access the Raspberry Pi via SSH and Telnet                                                                             |
| 🧠 Raspberry Pi OS (Lite)                                                   | operating system (OS) for the Raspberry Pi                                                                                                                |
| 📂 Samba                                                                    | enables network file sharing; lets you access, upload, and manage files stored on the Raspberry Pi                                                        |
| 🛡️ PiVPN                                                                   | create a secure VPN tunnel; lets you access your Raspberry Pi and NAS from anywhere on the internet as if you were at home                                |
| 🌐 File Browser                                                             | web-based interface; lets yo access, manage, upload, and download files from your Raspberry Pi using just a browser; includes user login                  |
| [🔒 OpenVPN Client Software](https://openvpn.net/client/)                   | securely connects your device to a VPN server, enabling encrypted remote network access                                                                   |
| [📖 OpenVPN Open Source](https://openvpn.net/community/)                    | free, open-source VPN solution that provides secure, encrypted connections between networks or devices, needed to control the VPN connection using Python |


## 📋 Setup Instructions
  
1. Configure Raspberry Pi as NAS (see [🐾 Steps to Set-Up NAS](docs/setup-nas.md))
2. Set up VPN access (see [🏃‍♀️ Steps to Set-Up VPN](docs/setup-vpn.md))
3. Prepare `.env` file for the Python backup script 

| .env variable  | Explanation                                                                                                 | Example                                                    |
| -------------- | ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| WORKING_PATH   | Path to your working directory/ files and folders you want to backup                                        | "C:\\\\Users\\\\user1"                                     |
| BACKUP_PATH    | Destination path on NAS where backups will be stored                                                        | "\\\\\\\\123.456.7.891\\\\shared"                          |
| NASA_REMOTE_IP | IP address of your NAS device                                                                               | "123.456.7.891"                                            |
| NASA_USERNAME  | Username to access your NAS                                                                                 | "raspberry"                                                |
| NASA_PWD       | Password for your NAS user                                                                                  | "pi"                                                       |
| SHELLY_IP      | IP address of the Shelly Plug device                                                                        | "198.765.4.321"                                            |
| SMB_USERNAME   | Samba (SMB) username for accessing shared folders on NAS system                                             | "user1"                                                    |
| SMB_PWD        | Samba (SMB) password                                                                                        | "pwd123"                                                   |
| OVPN_PATH      | Path where [OpenVPN Open Source](https://openvpn.net/community/) GUI executable (openvpn-gui.exe) is stored | "C:\\\\Program Files\\\\OpenVPN\\\\bin\\\\openvpn-gui.exe" |
| OVPN_CONFIG    | Name of your OpenVPN profile/config file                                                                    | "Profile1.ovpn"                                            |
| WEEKLY_PREFIX  | Prefix name for weekly backup folder on your NAS                                                            | "weekly-backup-"                                           |
| MONTHLY_PREFIX | Prefix name for monthly backup folder on your NAS                                                           | "monthly-backup-"                                          |

4. Run the Python backup script (see [🐍 Python Script for Automated Backups](docs/backup-script.md)) using `python main.py` or add it as a cron job


## 💡 Things to Improve
    
- integrate MQTT support for remote power control of the Shelly Plug device (see [⚡ MQTT Power Control](improvements/mqtt-power-control))


## 📄 References

NAS:  
[DIY NAS (Network-Attached Storage) with Raspberry Pi 5](https://www.hackster.io/ElecrowOfficial/diy-nas-network-attached-storage-with-raspberry-pi-5-e91a37)  
[How to Build Your First NAS! Samba Share Setup Explained](https://www.youtube.com/watch?v=iDruhrG4hSk)  

VPN:  
[OpenVPN Raspberry Pi Setup using PiVPN! (Easy Tutorial)](https://www.youtube.com/watch?v=kLmbgJe1rEU)  
[VPN Server auf dem Raspberry Pi installieren - PiVPN der OpenVPN Client für den Pi](https://www.youtube.com/watch?v=A17sYeDcnws)  

MQTT:  
[MQTT: Der ultimative Guide für Einsteiger](https://netzwerk-guides.de/mqtt-guide-fuer-einsteiger/)  


[How To Connect To Raspberry Pi From Outside Network](https://www.howto-do.it/how-to-connect-to-raspberry-pi-from-outside-network/#Connecting_to_Raspberry_Pi_using_a_VPN)  
links to tutorial for VPN
[Is there an actual safe way to access my NAS from outside of my home Wi-Fi?](https://www.reddit.com/r/synology/comments/otczia/is_there_an_actual_safe_way_to_access_my_nas_from/)  

For upgrading Hardware Set-up: [Build Your Own Homelab NAS with a Raspberry Pi](https://kitemetric.com/blogs/build-your-own-homelab-nas-with-a-raspberry-pi)
- but will that allow the cooling system to still work?
- have a look
For connecting to NAS using iPhone: [How to build a Raspberry Pi NAS](https://www.raspberrypi.com/tutorials/nas-box-raspberry-pi-tutorial/)  
For adding more than one user: [Simple NAS server (with external access) with Raspberry Pi](https://hobby-project.com/arduino-raspberry-pi/simple-nas-server-with-external-access-with-raspberry-pi/)