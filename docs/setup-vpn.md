## 🏃‍♀️ Steps to Set-Up VPN

1. Connect to Raspberry Pi over local network using SSH and PuTTY
2. Install PiVPN
   ```
	curl -L https://install.pivpn.io | bash
	```
	- set up static IP address?
		- depends whether you set the IP address of your Pi on your router to static
		- set to static... answer "\<Yes>", otherwise "\<No>"
	- choose OpenVPN (space to select) and proceed
	- port "1194" is the OpenVPN port (choose any other free port number for increased security)
	- choose "Google" as DNS provider
	- choose "DNS Entry" (follow before doing so: [Raspberry Pi DDNS Setup Tutorial! (DuckDNS)](https://www.youtube.com/watch?v=s-66gmIHoyE) / written instructions: [How to Setup DuckDNS on a Raspberry Pi](https://www.wundertech.net/how-to-setup-duckdns-on-a-raspberry-pi/))
	- public DNS name : "\<subdomain>.duckdns.org"
3. Create a profile
   ```
	pivpn add
	```
4. See all the profiles that you created
   ```
	cd ovpns
	ls
	```
5. Get this profile off your Pi to the device which you want to connect via VPN to your local network
	- NAS is already set-up: copy ovpn profile to shared folder
	  ```
		sudo cp <profile-name>.ovpn /mnt/mystorage/shared
		```
	- if not: follow instructions in video 06:13: [OpenVPN Raspberry Pi Setup using PiVPN! (Easy Tutorail)](https://www.youtube.com/watch?v=kLmbgJe1rEU)
6. Port forward UDP port on router to Raspberry Pi (setup depends on router)
7. Decide between Split-Tunnel VPN and Full-Tunnel VPN
	- split-tunnel connection is enough since the purpose is to access our shared Samba folder from outside our network
	- full-tunnel VPN connection should be used when trying to secure your connection at public Wi-Fi locations
	- a OpenVPN profile is by default configured as a full-tunnel VPN connection
	- to make an OpenVPN profile act as split-tunnel VPN add the following two lines to the profile file (where the IP address must correpond to network IP address range)
	  *route-nopull*
	  *route 192.168.2.0 255.255.255.0 vpn_gateway*
<img src="../images/split-full-tunnel-vpn-comparison.png" width=550px/>
8. Download OpenVPN client software (different for each device)
	- Windows: [OpenVPN Connect for Windows](https://openvpn.net/client/)  
	- iOS: OpenVPN Connect
	- Android: OpenVPN für Android
