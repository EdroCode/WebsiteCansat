
from flask import Flask, Response, jsonify
from flask_cors import CORS
import threading
import json
import paramiko
import re
import queue
import time
import random

app = Flask(__name__)
CORS(app)

data_queue = queue.Queue()

# Função real de SSH (desativada durante teste)
def ssh_data_fetcher():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("192.168.1.190", port=22, username="cansat", password="esca")
    command = f"bash -i -c 'source /home/cansat/cansat/bin/activate && python3 /home/cansat/Code/CanSat/Python/Main.py'"
    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)

    pattern = re.compile(r"\{.*?\}")
    for line in stdout:
        match = pattern.search(line)
        if match:
            try:
                data = eval(match.group()) 
                data_queue.put(data)
            except:
                continue


def fake_gps_generator():
    lat = 41.5600
    lon = -8.4000

    while True:


        lat_change = random.uniform(-0.005, 0.005) 
        lon_change = random.uniform(-0.005, 0.005)  

        lat += lat_change
        lon += lon_change

        fake_data = {
            "latitude": lat,
            "longitude": lon,
            "temperature": random.randrange(20, 40),
            "humidity": random.randrange(20, 40),
            "pressure": random.randrange(10000, 11000),
            "altitude": random.randrange(60, 80),
            "beta": 0,
            "muons": 0,
            "gases": 0,
            "uv": 0,
            "ozone": 0,
            "pi_temp": random.randrange(50, 80)
        }

        data_queue.put(fake_data)
        time.sleep(1) 



def shutdown():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("192.168.1.190", port=22, username="cansat", password="esca")
    command = "sudo /sbin/shutdown now"
    ssh.exec_command(command, get_pty=True)

@app.route("/shutdown", methods=["POST"])
def shutdown_pi():
    print("Shutdown request received!")  
    try:
        shutdown()
        return jsonify(status="success", message="Shutdown command sent."), 200
    except Exception as e:
        print("Erro ao desligar:", e)
        return jsonify(status="error", message=str(e)), 500

@app.route("/stream")
def stream():
    def event_stream():
        while True:
            data = data_queue.get()
            yield f"data: {json.dumps(data)}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    # Usa apenas 1 thread de cada vez: fake_gps_generator (teste) OU ssh_data_fetcher (produção)
    threading.Thread(target=fake_gps_generator, daemon=True).start()
    # threading.Thread(target=ssh_data_fetcher, daemon=True).start()

    app.run(host="0.0.0.0", port=5000)