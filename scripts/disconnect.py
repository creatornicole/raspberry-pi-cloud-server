from helpers import is_port_open
from load_variables import load_variables
import os
import paramiko
import requests
import subprocess
import time

def disconnect():
    """
    """
    def shutdown_pi(ip: str, username: str, pwd: str):
        """
        """
        try:
            # connect via SSH
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=pwd)

            # use sudo to shut down the Pi
            ssh.exec_command("sudo shutdown -h now")
            print(f"{info_symbol} Shutdown command sent to Raspberry Pi at {ip}")

            ssh.close()
        except Exception as e:
            raise RuntimeError(f"\033[31m{err_symbol} Unexpected error occured: {e} \033[0m")

    def shutdown_shelly(ip: str):
        """
        """
        url = f"http://{ip}/relay/0?turn=off"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"\033[32m{success_symbol} Shelly turned OFF successfully \033[0m")
            else:
                raise RuntimeError(f"\033[31m{err_symbol} Failed to turn off Shelly. Status code: {response.status_code} \033[0m")
        except requests.RequestException as e:
            raise ConnectionError(f"\033[31m{err_symbol} Error connecting to Shelly at {ip}: {e} \033[0m")

    def disconnect_vpn_if_connected(ovpn_gui: str, ovpn_profile: str):
        """
        """
        try:
            result = subprocess.run(
                [ovpn_gui, "--command", "status", ovpn_profile],
                capture_output=True,
                text=True
            )
            if "CONNECTED" in result.stdout.upper():
                print(f"{info_symbol} VPN is connected, disconnecting...")
                subprocess.run([ovpn_gui, "--command", "disconnect", ovpn_profile])
                print(f"\033[32m{success_symbol} VPN disconnected successfully \033[0m")
            else:
                print(f"{info_symbol} VPN is not connected, no need to disconnect")
        except Exception as e:
            raise RuntimeError(f"\033[31m{err_symbol} Error checking/disconnecting VPN: {e} \033[0m")

    success_symbol, err_symbol, warning_symbol, info_symbol = load_variables()

    nas_ip = os.getenv("NASA_REMOTE_IP")
    if not nas_ip:
        raise EnvironmentError(f"\033[31m{err_symbol} NASA_REMOTE_IP environment variable is not set \033[0m")
    nas_port = 445
    # nas_username = os.getenv("NASA_USERNAME")
    # if not nas_username:
        # raise EnvironmentError(f"\033[31m{err_symbol} NASA_USERNAME environment variable is not set \033[0m")
    # nas_pwd = os.getenv("NASA_PWD")
    # if not nas_pwd:
        # raise EnvironmentError(f"\033[31m{err_symbol} NASA_PWD environment variable is not set \033[0m")

    # shutdown_pi(nas_ip, nas_username, nas_username)
    print(f"{info_symbol} Waiting for Raspberry Pi to shut down", end="", flush=True)
    
    counter = 0
    # wait up to 60 seconds for the Pi to shut down
    while is_port_open(nas_ip, nas_port) and counter <= 60:
        print(".", end="", flush=True)
        counter += 1
        time.sleep(1)
    print() # move to the next line after the loop

    if is_port_open(nas_ip, nas_port):
        raise RuntimeError(f"\033[31m{err_symbol} NAS cannot be shut down \033[0m")

    shelly_ip = os.getenv("SHELLY_IP")
    if not shelly_ip:
        raise EnvironmentError(f"\033[31m{err_symbol}] SHELLY_IP environment variable is not set \033[0m")
    
    shutdown_shelly(shelly_ip)
    time.sleep(5)

    ovpn_gui = os.getenv("OVPN_PATH")
    if not ovpn_gui:
        raise EnvironmentError(f"\033[31m{err_symbol}] OVPN_PATH environment variable is not set \033[0m")
    ovpn_profile = os.getenv("OVPN_CONFIG")
    if not ovpn_profile:
        raise EnvironmentError(f"\033[31m{err_symbol}] OVPN_CONFIG environment variable is not set \033[0m")
    
    disconnect_vpn_if_connected(ovpn_gui, ovpn_profile)

