from helpers import is_port_open, raise_env_error, shutdown_shelly
import os
import platform
import requests
from smbclient import register_session
import subprocess
import time
from load_variables import load_variables
import sys

def connect():
    """
    """
    def connected_to_local_network(target_ip: str, target_mac: str) -> bool:
        """
        """
        def ping(target_ip: str):
            """
            """
            param = "-n" if platform.system().lower() == "windows" else "-c"
            result = subprocess.run(
                ["ping", param, "1", target_ip],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
            return result.returncode == 0 # 0 means success
        
        def get_mac(target_ip: str) -> str:
            """
            """
            try:
                if platform.system().lower() == "windows":
                    output = subprocess.check_output(["arp", "-a", target_ip]).decode()
                    for line in output.splitlines():
                        if target_ip in line:
                            return line.split()[1].replace("-", ":").lower()
                else:
                    output = subprocess.check_output(["arp", "-n", target_ip]).decode()
                    for line in output.splitlines():
                        if target_ip in line:
                            return line.split()[2].lower()
            except Exception as e:
                raise RuntimeError(f"\033[31m Failed to get MAC address for IP {target_ip}: {e} \033[0m")

        print(f"{info_symbol} Checking if Shelly Plug ({shelly_ip}) is reachable...")

        if not ping(target_ip):
            print(f"\033[32m{warning_symbol} Shelly plug at {shelly_ip} is unreachable - you are likely OUTSIDE your local network \033[0m")
            return False
        
        mac = get_mac(target_ip)
        print(mac, target_mac)
        if mac == target_mac:
            print(f"\033[32m{success_symbol} Shelly plug is reachable \033[0m")
        else:
            print(f"\033[33m{warning_symbol} Ping replied, but MAC address doesn't match \033[0m")
            print(f"\033[33m{warning_symbol} Found: {mac}, expected: {shelly_mac} \033[0m")
            print(f"\033[33m{warning_symbol} You might be OUTSIDE your local network or talking to a different device \033[0m")
            return False
        
        return True
    
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
        """
        """
        url = f"http://{ip}/relay/0?turn=on"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"\033[32m{success_symbol} Shelly turned ON successfully \033[0m")
            else:
                raise RuntimeError(f"\033[31m{err_symbol} Failed to turn on Shelly. Status code: {response.status_code} \033[0m")
        except requests.RequestException as e:
            raise ConnectionError(f"\033[31m{err_symbol} Error connecting to Shelly at {ip}: {e} \033[0m")
    
    def boot_up_pi(nas_ip: str, nas_port: str, timeout: int = 60) -> bool:
        """
        """
        print(f"{info_symbol} Booting up Raspberry Pi", end="", flush=True)
        for _ in range(timeout):
            if is_port_open(nas_ip, nas_port):
                print() # end the line of dots
                return True
            print(".", end="", flush=True)
            time.sleep(1)
        print() # end the line of dots
        return False

    success_symbol, err_symbol, warning_symbol, info_symbol = load_variables()

    (shelly_ip := os.getenv("SHELLY_IP")) or raise_env_error("SHELLY_IP")
    (shelly_mac := os.getenv("SHELLY_MAC")) or raise_env_error("SHELLY_MAC")

    if connected_to_local_network(shelly_ip, shelly_mac):
        print(f"{info_symbol} NAS in local network")
        status = "local"
    else:
        print(f"\033[33m{warning_symbol} NAS not in local network, connecting to VPN... \033[0m")

        (ovpn_gui := os.getenv("OVPN_PATH")) or raise_env_error("OVPN_PATH")
        (ovpn_profile := os.getenv("OVPN_CONFIG")) or raise_env_error("OVPN_CONFIG")

        connect_to_vpn(ovpn_gui, ovpn_profile)
        time.sleep(15)

        status = "vpn" if connected_to_local_network(shelly_ip) else "unreachable"

    if status == "unreachable":
        raise RuntimeError(f"\033[31m{err_symbol} Device still unreachable after VPN connection attempt \033[0m")
    elif status == "vpn":
        print(f"\033[32m{success_symbol} Connected to VPN successfully \033[0m")
    
    (nas_ip := os.getenv("NASA_REMOTE_IP")) or raise_env_error("NASA_REMOTE_IP")
    nas_port = 445

    if is_shelly_on(shelly_ip):
        if is_port_open(nas_ip, nas_port):
            print(f"{info_symbol} Shelly already turned ON")
            pi_booted = True
        else:
            print(f"{info_symbol} Shelly ON but Pi not running")
            print(f"{info_symbol} Restarting Shelly...")
            shutdown_shelly(shelly_ip)
            time.sleep(5)
            turn_on_shelly(shelly_ip)
            pi_booted = boot_up_pi(nas_ip, nas_port)
    else:
        turn_on_shelly(shelly_ip)
        pi_booted = boot_up_pi(nas_ip, nas_port)
        
    if not pi_booted:
        raise RuntimeError(f"\033[31m{err_symbol} NAS cannot be reached \033[0m")

    # connect to Raspberry Pi NAS
    (nas_username := os.getenv("SMB_USERNAME")) or raise_env_error("SMB_USERNAME")
    (nas_pwd := os.getenv("SMB_PWD")) or raise_env_error("SMB_PWD")

    register_session(nas_ip, username=nas_username, password=nas_pwd)

    if status == "local":
        print(f"\033[32m{success_symbol} Registered to NAS \033[0m")
    elif status == "vpn":
        print(f"\033[32m{success_symbol} Registered to NAS via VPN \033[0m")