import netifaces
import ipaddress

def get_local_network():
    for iface in netifaces.interfaces():
        print(iface)
        addrs = netifaces.ifaddresses(iface)
        ipv4_list = addrs.get(netifaces.AF_INET, [])
        
        for ipv4_info in ipv4_list:
            print(f"\t{ipv4_info}")
            ip_addr = ipv4_info.get('addr')
            netmask = ipv4_info.get('netmask')
            
            if not ip_addr or not netmask:
                continue

            ip = ipaddress.IPv4Address(ip_addr)
            if ip.is_loopback:
                continue  # Salta 127.0.0.1

            # Solo aceptamos IPs privadas (192.168.x.x, 10.x.x.x, 172.16.x.x — 172.31.x.x)
            if ip.is_private:
                network = ipaddress.IPv4Network(f"{ip_addr}/24", strict=False)
                return str(network)
    return None

if __name__ == "__main__":
    print(get_local_network())
