import requests

device_ip = ["172.18.0.5"]

# url
url = "http://localhost:5000/backup/all"

# Datos a enviar
payload = {
    "ips": device_ip
}

try:
    response = requests.post(url, json=payload, timeout=15)
    if response.status_code == 200:
        print("Respuesta exitosa:")
        print(response.json())
    else:
        print("Error:")
        print(response.status_code, response.text)
except Exception as e:
    print(f"Error de conexión: {e}")
