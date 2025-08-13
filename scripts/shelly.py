from load_variables import load_variables
import requests
import time

success_symbol, err_symbol, warning_symbol, info_symbol = load_variables()

def turn_on_shelly(host: str, auth_key: str, device_id: str, shelly_ip: str):
        """
        """
        url = f"https://{host}/v2/devices/api/set/switch?auth_key={auth_key}"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "id": device_id,
            "on": True
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                print(f"\033[32m{success_symbol} Shelly turned ON successfully \033[0m")
            else:
                raise RuntimeError(f"\033[31m{err_symbol} Failed to turn on Shelly. Status code: {response.status_code}: {e} \033[0m")
        except requests.RequestException as e:
            raise ConnectionError(f"\033[31m{err_symbol} Error connecting to Shelly at {shelly_ip}: {e} \033[0m")   

def shutdown_shelly(host: str, auth_key: str, device_id: str, shelly_ip: str):
        """
        """
        url = f"https://{host}/v2/devices/api/set/switch?auth_key={auth_key}"
        headers = {
             "Content-Type": "application/json"
        }
        payload = {
            "id": device_id,
            "on": False
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                print(f"\033[32m{success_symbol} Shelly turned OFF successfully \033[0m")
            else:
                raise RuntimeError(f"\033[31m{err_symbol} Failed to turn off Shelly. Status code: {response.status_code} \033[0m")
        except requests.RequestException as e:
            raise ConnectionError(f"\033[31m{err_symbol} Error connecting to Shelly at {shelly_ip}: {e} \033[0m")
        
def restart_shelly(host: str, auth_key: str, device_id: str, shelly_ip: str):
        """
        """
        shutdown_shelly(host, auth_key, device_id, shelly_ip)
        time.sleep(5)
        turn_on_shelly(host, auth_key, device_id, shelly_ip)