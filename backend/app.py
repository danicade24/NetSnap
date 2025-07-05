from flask import Flask, jsonify, request
import nmap
from tools import *
import subprocess

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/ip',methods=['GET'])
def fet_ip():
    target =  get_local_network() # IP 
    print(target)
    if not target:
        return jsonify({'error': 'No se pudo determinar la red local'}), 500
    return jsonify({"ip":target}), 200

@app.route('/devices', methods=['GET'])
def list_devices():
    nm = nmap.PortScanner()
    target =  get_local_network() # IP 
    print(target)
    if not target:
        return jsonify({'error': 'No se pudo determinar la red local'}), 500

    ini = "[machines]\n"
    
    try:
        nm.scan(hosts=target, arguments='-sn')  

        devices = []
        for host in nm.all_hosts():
            ssh_isopen = False

            try:
                # Escanear solo puerto 22 (SSH) en el host detectado
                port_scan = nmap.PortScanner()
                port_scan.scan(hosts=host, ports='22', arguments='-T4')
                if port_scan[host].has_tcp(22) and port_scan[host]['tcp'][22]['state'] == 'open':
                    ssh_isopen = True
            except:
                pass 

            if ssh_isopen:
                ini = ini + f"{host}\n"

            #print(host)
            device_info = {
                'ip': host,
                'mac': nm[host]['addresses'].get('mac', 'Unknown'),
                'hostname': nm[host].hostname() or 'Unknown',
                'state': nm[host].state(),
                'ssh': ssh_isopen
            }
            devices.append(device_info)

        with open("./ansible/inventory.ini", 'w') as f:
            f.write(ini)

        return jsonify({'devices': devices})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/backup', methods=['POST'])
def backup_device():
    data = request.get_json()
    ips = data.get('ips')

    if not ips or not isinstance(ips, list):
        return jsonify({'error': 'Faltan las IPs o el formato es incorrecto (debe ser una lista)'}), 400

    playbook_path = "/code/ansible/backup_pc.yml"
    key_path = "/code/ansible/netsnap_id_rsa"

    resultados = []

    for ip in ips:
        ansible_command = (
            f"ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook {playbook_path} "
            f"-i {ip}, "
            f"-u admin "
            f"--private-key {key_path} "
            f"--extra-vars 'target_host={ip}'"
        )

        try:
            result = subprocess.run(ansible_command, shell=True, capture_output=True, text=True, timeout=60)
            ansible_output = process_ansible_result(result.stdout)

            resultados.append({
                'ip': ip,
                'status': 'Backup exitoso' if result.returncode == 0 else 'Error en backup',
                'ansible_output': ansible_output,
                'ansible_error': result.stderr if result.returncode != 0 else ''
            })

        except subprocess.TimeoutExpired:
            resultados.append({
                'ip': ip,
                'status': 'Error: Timeout',
                'ansible_output': '',
                'ansible_error': 'Timeout alcanzado al ejecutar Ansible'
            })
        except Exception as e:
            resultados.append({
                'ip': ip,
                'status': 'Error inesperado',
                'ansible_output': '',
                'ansible_error': str(e)
            })

    # Verifica si alguna IP falló
    errores = [r for r in resultados if 'Error' in r['status']]
    status_global = 'Backup exitoso para todos' if not errores else 'Backup completado con errores'

    return jsonify({'status': status_global, 'resultados': resultados}), (200 if not errores else 500)

@app.route('/backup/all', methods=['POST'])
def backup_all_devices():
    try:
        playbook_path = "/code/ansible/backup_pc.yml"
        inventory_path = "/code/ansible/inventory.ini"
        key_path = "/code/ansible/netsnap_id_rsa"

        ansible_command = (
            f"ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook {playbook_path} "
            f"-i {inventory_path} "
            f"-u admin "
            f"--private-key {key_path}"
        )

        result = subprocess.run(ansible_command, shell=True, capture_output=True, text=True, timeout=300)

        processed_output = process_ansible_result_complete(result.stdout)

        if result.returncode == 0:
            return jsonify({'status': 'Backup exitoso para todos', 'ansible_output': processed_output}), 200
        else:
            return jsonify({
                'status': 'Error en backup',
                'ansible_output': result.stdout,
                'ansible_error': result.stderr
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)