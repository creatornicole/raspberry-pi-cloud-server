from collections.abc import Callable
from helpers import is_port_open, raise_env_error
import locale
import os
import platform
import requests
from smbclient import register_session
import subprocess
import time
from load_variables import load_variables
import sys
from shelly import turn_on_shelly, restart_shelly

def connect():
    """
    """
    def connected_to_same_network(target_ip: str, target_mac: str) -> bool:
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
                    encoding = locale.getpreferredencoding(False)
                    output = subprocess.check_output(["arp", "-a", target_ip]).decode(encoding, errors="ignore")
                    for line in output.splitlines():
                        if target_ip in line:
                            return line.split()[1].replace("-", ":").lower()
                else:
                    output = subprocess.check_output(["arp", "-n", target_ip]).decode(errors="ignore")
                    for line in output.splitlines():
                        if target_ip in line:
                            return line.split()[2].lower()
            except Exception as e:
                raise RuntimeError(f"\033[31m{err_symbol} Failed to get MAC address for IP {target_ip}: {e} \033[0m")

        print(f"{info_symbol} Checking if Shelly Plug ({shelly_ip}) is reachable...")

        if not ping(target_ip):
            print(f"\033[33m{warning_symbol} Shelly plug at {shelly_ip} is unreachable - you are likely OUTSIDE your local network \033[0m")
            return False
        
        mac = get_mac(target_ip)
        if mac == target_mac:
            print(f"\033[32m{success_symbol} Shelly plug is reachable \033[0m")
        else:
            print(f"\033[33m{warning_symbol} Ping replied, but MAC address doesn't match \033[0m")
            print(f"\033[33m{warning_symbol} Found: {mac}, expected: {shelly_mac} \033[0m")
            print(f"\033[33m{warning_symbol} You might be OUTSIDE your local network or talking to a different device \033[0m")
            return False
        
        return True    
    
    def verify_local_connection(nas_ip: str, nas_port: int, host: str, auth_key: str, device_id: str, shelly_ip: str) -> bool:
        """
        """
        def wait_for_pi_boot(nas_ip: str, nas_port: int, timeout: int = 30) -> bool:
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
    
        if is_port_open(nas_ip, nas_port):
            print(f"\033[32m{success_symbol} Pi already booted up and NAS service reachable \033[0m")
            return True
        
        if wait_for_pi_boot(nas_ip, nas_port):
             print(f"\033[32m{success_symbol} Pi booted up successfully and NAS service reachable \033[0m")
             return True
        
        print(f"\033[33m{warning_symbol} Pi cannot be reached, restarting Shelly... \033[0m")
        restart_shelly(host, auth_key, device_id, shelly_ip)

        if wait_for_pi_boot(nas_ip, nas_port):
            print(f"\033[32m{success_symbol} Pi booted up successfully after restarting the Shelly \033[0m")
            print(f"\033[32m{success_symbol} NAS service reachable \033[0m")
            return True
        
        return False

    def verify_vpn_connection(ovpn_bat: str, nas_ip: str, nas_port: int, host: str, auth_key: str, device_id: str, shelly_ip: str) -> bool:
        """
        """
        def connect_to_vpn(ovpn_bat: str, nas_ip: str) -> bool:
            """
            """
            try: 
                vpn_proc = subprocess.run(
                    [ovpn_bat],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                if vpn_proc.returncode != 0:
                    raise RuntimeError(f"\033[31m{err_symbol} VPN batch file process returned non-zero exit code: {vpn_proc.returncode} \033[0m")
                
                ping_proc = subprocess.run(
                    ["ping", "-n", "1", nas_ip],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                return ping_proc.returncode == 0
            
            except Exception as e:
                raise Exception(f"\033[31m{err_symbol} Exception during VPN connection attempt: {e} \033[0m")     
        
        def wait_for_vpn_connection(ovpn_bat: str, nas_ip: str, nas_port: int, host: str, auth_key: str, devide_id: str, timeout: int = 30) -> bool:
            """
            """
            print(f"{info_symbol} Waiting for VPN connection", end="", flush=True)
            for _ in range(timeout):
                if connect_to_vpn(ovpn_bat, nas_ip):
                    print() # end the line of dots
                    return True
                print(".", end="", flush=True)
                time.sleep(1)
            print() # end the line of dots
            return False

        if connect_to_vpn(ovpn_bat, nas_ip) or wait_for_vpn_connection(ovpn_bat, nas_ip, nas_port, host, auth_key, device_id):
            print(f"\033[32m{success_symbol} VPN connected successfully \033[0m")
            if is_port_open(nas_ip, nas_port):
                print(f"\033[32m{success_symbol} NAS service up and running and can be reached \033[0m")
                return True
            else:
                print(f"\033[31m{err_symbol} NAS service cannot be reached \033[0m")
                return False
            
        print(f"\033[33m{warning_symbol} VPN connection cannot be reached, restarting Shelly... \033[0m")
        restart_shelly(host, auth_key, device_id, shelly_ip)

        if wait_for_vpn_connection(ovpn_bat, nas_ip, nas_port, host, auth_key, device_id):
            print(f"\033[32m{success_symbol} Connected to VPN successfully after restarting the Shelly \033[0m")
            return True
        
        return False

    success_symbol, err_symbol, warning_symbol, info_symbol = load_variables()

    (shelly_ip := os.getenv("SHELLY_IP")) or raise_env_error("SHELLY_IP")
    (shelly_mac := os.getenv("SHELLY_MAC")) or raise_env_error("SHELLY_MAC")
    (shelly_device_id := os.getenv("SHELLY_DEVICE_ID")) or raise_env_error("SHELLY_DEVICE_ID")
    (shelly_cloud_server := os.getenv("SHELLY_CLOUD_SERVER")) or raise_env_error("SHELLY_CLOUD_SERVER")
    (shelly_cloud_auth_key := os.getenv("SHELLY_CLOUD_AUTH_KEY")) or raise_env_error("SHELLY_CLOUD_AUTH_KEY")

    # does not matter whether Shelly is already turned on
    turn_on_shelly(shelly_cloud_server, shelly_cloud_auth_key, shelly_device_id, shelly_ip)

    # decide whether vpn has to be turned on
    (nas_ip := os.getenv("NASA_REMOTE_IP")) or raise_env_error("NASA_REMOTE_IP")
    (nas_port := int(os.getenv("NASA_PORT"))) or raise_env_error("NASA_PORT")

    (ovpn_bat := os.getenv("OVPN_CONNECT_BAT")) or raise_env_error("OVPN_CONNECT_BAT")

    if connected_to_same_network(shelly_ip, shelly_mac):
        print(f"{info_symbol} INSIDE local network or already connected to VPN")
        status = "local"

        if not verify_local_connection(nas_ip, nas_port, shelly_cloud_server, shelly_cloud_auth_key, shelly_device_id, shelly_ip):
            raise RuntimeError(f"\033[31m{err_symbol} Raspberry Pi failed to boot up or NAS service cannot be reached \033[0m")
                
    else:
        print(f"\033[33m{warning_symbol} Not in local network, connecting to VPN... \033[0m")
        status = "vpn"

        if not verify_vpn_connection(ovpn_bat, nas_ip, nas_port, shelly_cloud_server, shelly_cloud_auth_key, shelly_device_id)
            raise RuntimeError(f"\033[31m{err_symbol} VPN connection attempt failed \033[0m")

    # register session to Raspberry Pi NAS
    (nas_username := os.getenv("SMB_USERNAME")) or raise_env_error("SMB_USERNAME")
    (nas_pwd := os.getenv("SMB_PWD")) or raise_env_error("SMB_PWD")

    register_session(nas_ip, username=nas_username, password=nas_pwd)

    if status == "local":
        print(f"\033[32m{success_symbol} Registered session to NAS \033[0m")
    elif status == "vpn":
        print(f"\033[32m{success_symbol} Registered session to NAS via VPN \033[0m")