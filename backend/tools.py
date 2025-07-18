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

import ast

def process_ansible_result(result: str):
    try:
        idx = result.index('"host_info"')
        partial = result[idx:]

        # Buscar el cierre correcto del bloque
        end_idx = partial.find('}\n}') + 3
        if end_idx == 1:
            raise ValueError("No se encontró cierre del bloque host_info")

        # Extraer el texto del diccionario
        dict_text = '{' + partial[:end_idx] 

        # Convertir a diccionario real (no string)
        dict_text = dict_text.replace('\n', '').replace('\r', '').replace('\t', '')
        host_info_dict = ast.literal_eval(dict_text)

        return host_info_dict['host_info']

    except Exception as e:
        print("Error al procesar resultado:", e)
        return {}
    
import re

def find_all_indices(text, substring):
    return [match.start() for match in re.finditer(re.escape(substring), text)]

def process_ansible_result_complete(ansible_output):
    """
    Procesa la salida completa de Ansible y devuelve un dict con los resultados por host.
    """
    results = []

    idx = find_all_indices(ansible_output, "host_info")
    
    idx.pop(0)
    for i, ind in enumerate(idx[:-1]):
        results.append(process_ansible_result(ansible_output[ind-1:idx[i+1]]))
    
    return results

import difflib
import json

def comparar_configs(text1, text2):
    try:
        obj1 = json.loads(text1)
        obj2 = json.loads(text2)

        pretty1 = json.dumps(obj1, indent=2, ensure_ascii=False, sort_keys=True)
        pretty2 = json.dumps(obj2, indent=2, ensure_ascii=False, sort_keys=True)

        diff = difflib.unified_diff(
            pretty1.splitlines(keepends=True),
            pretty2.splitlines(keepends=True),
            lineterm=""
        )

        return ''.join(diff)
    except Exception as e:
        return f"Error al comparar: {e}"

if __name__ == "__main__":
    print(get_local_network())
