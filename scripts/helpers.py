from load_variables import load_variables
import socket

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