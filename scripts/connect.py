from helpers import is_port_open, raise_env_error
import os
import requests
from smbclient import register_session
import subprocess
import time
from load_variables import load_variables

def connect():
    """
    """
    def is_on_same_network(target_ip: str) -> bool:
        """
        """
        result = subprocess.run(
            ["ping", "-n", "1", target_ip], 
            capture_output=True, 
            text=True, 
            encoding="utf-8", 
            errors="ignore"
        )
        return result.returncode == 0 # 0 = ping success
    
    def connect_to_vpn(ovpn_gui: str, ovpn_profile: str):
        """
        """
        subprocess.run([ovpn_gui, "--command", "connect", ovpn_profile])

    def is_shelly_on(ip: str) -> bool:
        """
        """
        url = f"http://{ip}/relay/0"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get("ison"):
                return True
            else:
                return False
        except requests.RequestException as e:
            raise RuntimeError(f"\033[31m{err_symbol} Failed to reach Shelly at {ip} \033[0m")

    def turn_on_shelly(ip: str):
        url = f"http://{ip}/relay/0?turn=on"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"\033[32m{success_symbol} Shelly turned ON successfully \033[0m")
            else:
                raise RuntimeError(f"\033[31m{err_symbol} Failed to turn on Shelly. Status code: {response.status_code} \033[0m")
        except requests.RequestException as e:
            raise ConnectionError(f"\033[31m{err_symbol} Error connecting to Shelly at {ip}: {e} \033[0m")
        
    success_symbol, err_symbol, warning_symbol, info_symbol = load_variables()

    (shelly_ip := os.getenv("SHELLY_IP")) or raise_env_error("SHELLY_IP")

    if is_on_same_network(shelly_ip):
        print(f"{info_symbol} NAS in local network")
        status = "local"
    else:
        print(f"\033[33m{warning_symbol} NAS not in local network, connecting to VPN... \033[0m")

        (ovpn_gui := os.getenv("OVPN_PATH")) or raise_env_error("OVPN_PATH")
        (ovpn_profile := os.getenv("OVPN_CONFIG")) or raise_env_error("OVPN_CONFIG")

        connect_to_vpn(ovpn_gui, ovpn_profile)
        time.sleep(15)

        status = "vpn" if is_on_same_network(shelly_ip) else "unreachable"

    if status == "unreachable":
        raise RuntimeError(f"\033[31m{err_symbol} Device still unreachable after VPN connection attempt \033[0m")
    elif status == "vpn":
        print(f"\033[32m{success_symbol} Connected to VPN successfully \033[0m")
    
    (nas_ip := os.getenv("NASA_REMOTE_IP")) or raise_env_error("NASA_REMOTE_IP")
    nas_port = 445

    if is_shelly_on(shelly_ip):
        print(f"{info_symbol} Shelly already turned ON")
    else:
        turn_on_shelly(shelly_ip)
        print(f"{info_symbol} Booting up Raspberry Pi", end="", flush=True)

        counter = 0
        # wait for the Pi to boot up
        while not is_port_open(nas_ip, nas_port) and counter <= 60:
            print(".", end="", flush=True)
            counter += 1
            time.sleep(1)
        print() # move to the next line after the loop
        
    if not is_port_open(nas_ip, nas_port):
        raise RuntimeError(f"\033[31m{err_symbol} NAS cannot be reached \033[0m")

    # connect to Raspberry Pi NAS
    (nas_username := os.getenv("SMB_USERNAME")) or raise_env_error("SMB_USERNAME")
    (nas_pwd := os.getenv("SMB_PWD")) or raise_env_error("SMB_PWD")

    register_session(nas_ip, username=nas_username, password=nas_pwd)

    if status == "local":
        print(f"\033[32m{success_symbol} Registered to NAS \033[0m")
    elif status == "vpn":
        print(f"\033[32m{success_symbol} Registered to NAS via VPN \033[0m")