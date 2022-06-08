import math


def __get_ip_remainder__(ip: float) -> int:
    return int(round((ip % 1) * 10))

def ip_to_ip_w_remainder(ip: float) -> float:
    ip_large = int(ip)
    ip_remainder = __get_ip_remainder__(ip) / 3.0
    return ip_large + ip_remainder

def add_ip(a: float, b: float) -> float:
    ip_large_addition = float(math.floor(a) + math.floor(b))
    ip_remainder_addition = __get_ip_remainder__(a) + __get_ip_remainder__(b)

    if ip_remainder_addition == 4:
        return ip_large_addition + 1.1
    elif ip_remainder_addition == 3:
        return ip_large_addition + 1
    elif ip_remainder_addition == 2:
        return ip_large_addition + 0.2
    elif ip_remainder_addition == 1:
        return ip_large_addition + 0.1
    return ip_large_addition