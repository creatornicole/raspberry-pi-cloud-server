import socket

def is_port_open(ip: str, port: int) -> bool:
    """
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        result = s.connect_ex((ip, port))
        return result == 0 # 0 means success