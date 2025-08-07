from load_variables import load_variables
import requests
import socket

success_symbol, err_symbol, warning_symbol, info_symbol = load_variables()

def is_port_open(ip: str, port: int) -> bool:
    """
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        result = s.connect_ex((ip, port))
        return result == 0 # 0 means success
    
def raise_env_error(var_name: str):
    _, err_symbol, _, _ = load_variables()
    raise EnvironmentError(f"\033[31m{err_symbol} {var_name} environment variable is not set \033[0m")

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