from flask import Flask, jsonify, request
import nmap
from tools import get_local_network
import subprocess

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/devices', methods=['GET'])
def list_devices():
    nm = nmap.PortScanner()
    target =  get_local_network() # IP 
    print(target)
    if not target:
        return jsonify({'error': 'No se pudo determinar la red local'}), 500

    
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

            #print(host)
            device_info = {
                'ip': host,
                'mac': nm[host]['addresses'].get('mac', 'Unknown'),
                'hostname': nm[host].hostname() or 'Unknown',
                'state': nm[host].state(),
                'ssh': ssh_isopen
            }
            devices.append(device_info)

        return jsonify({'devices': devices})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/backup', methods=['POST'])
def backup_device():
    data = request.get_json()
    ip = data.get('ip')

    if not ip:
        return jsonify({'error': 'Falta la IP del dispositivo'}), 400

    try:
        # Ruta al playbook de Ansible
        playbook_path = "/code/ansible/backup_pc.yml"
        # Ruta a la clave privada (ya configurada en ansible.cfg o se pasa aquí)
        key_path = "/code/ansible/netsnap_id_rsa"

        # Comando ansible-playbook con extra-vars
        ansible_command = (
            f"ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook {playbook_path} "
            f"-i {ip}, "
            f"-u admin "
            f"--private-key {key_path} "
            f"--extra-vars 'target_host={ip}'"
        )

        result = subprocess.run(ansible_command, shell=True, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            return jsonify({'status': 'Backup exitoso', 'ansible_output': result.stdout})
        else:
            return jsonify({
                'status': 'Error en backup',
                'ansible_output': result.stdout,
                'ansible_error': result.stderr
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)