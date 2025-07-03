from flask import Flask, jsonify
import nmap

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/devices', methods=['GET'])
def list_devices():
    nm = nmap.PortScanner()
    target = '192.168.18.1/24'  # IP red
    
    try:
        nm.scan(hosts=target, arguments='-sn')  

        devices = []
        for host in nm.all_hosts():
            #print(host)
            device_info = {
                'ip': host,
                'mac': nm[host]['addresses'].get('mac', 'Unknown'),
                'hostname': nm[host].hostname() or 'Unknown',
                'state': nm[host].state()
            }
            devices.append(device_info)

        return jsonify({'devices': devices})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)