##  🐍 Python Script for Automated Backups

#### Handle OpenVPN

1. [Classic OpenVPN](https://openvpn.net/community/) required to control the connection using Python
	- will install to C:\Program Files\OpenVPN
	- with
		- bin\openvpn.exe
		- bin\openvpn-gui.exe
		- config\folder
2. Place .ovpn file (= client profile from PiVPN (see "🏃‍♀️ Steps to Set-Up VPN")) into C:\Program Files\OpenVPN\config\client.ovpn
3. Test connection manually before automating with Python
	- start openvpn-gui.exe (run as administrator)
	- right-click tray icon -> connect -> choose client
4. Enable automatic password usage
	- tick the option to save the password when connecting
	- this ensures that Python can start the VPN connection without requiring manual password entry
5. Automate with Python
	- profile name must match the filename (client.ovpn)
   ```Python
	import subprocess

	openvpn_gui = r"C:\Program Files\OpenVPN\bin\openvpn-gui.exe"

	# connect
	subprocess_run([openvpn.gui, "--command", "connect"], "client.ovpn")

	# disconnect
	subprocess_run([openvpn.gui, "--command", "disconnect", "client.ovpn"])
	```


## 🔌 Power Control of Shelly Plug Device Using HTTP Requests

