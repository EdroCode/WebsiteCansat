
from math import cos, pi, sin
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
    direction = random.uniform(-pi, pi)
    lat_change = 0 
    lon_change = 0

    while True:


        multiplier = random.uniform(0, 0.00005) 

        lat_change = (sin(direction) * multiplier)
        lon_change = (cos(direction) * multiplier) 
        direction += random.uniform(-0.2, 0.2)

        lat += lat_change
        lon += lon_change


        fake_data = {
            "latitude": lat,
            "longitude": lon,
            "temperature": round(random.uniform(15, 18), 2),
            "humidity": round(random.uniform(60, 85), 2),
            "temperature_ext": round(random.uniform(17, 18), 2),
            "humidity_ext": round(random.uniform(60, 65), 2),
            "accel_x": round(random.uniform(-1, 1), 9),
            "accel_y": round(random.uniform(-1, 1), 9),
            "accel_z": round(random.uniform(-1, 1), 9),
            "gyro_x": round(random.uniform(0, 10), 9),
            "gyro_y": round(random.uniform(0, 10), 9),
            "gyro_z": round(random.uniform(0, 10), 9),
            "mag_x": None,
            "mag_y": None,
            "mag_z": None,
            "pi_temp": round(random.uniform(45, 50), 1),
            "latitude": lat,
            "longitude": lon,
            "altitude": round(random.uniform(80, 90), 2),
            "pressure": round(random.uniform(1, 1.5), 2),
            "temp_bmp": round(random.uniform(1, 1.5), 2),
            "alt_bmp": round(random.uniform(31880, 31890), 2),
            "uv": round(random.uniform(0, 5), 2),
            "ambient_light": round(random.uniform(0.5, 1), 2),
            "uvi": round(random.uniform(0, 1), 2),
            "lux": round(random.uniform(0.5, 1), 2),
            "cpl": random.randint(1, 10)
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