from flask import Flask, Response, jsonify
from math import radians, sin, cos, sqrt, atan2
from flask_cors import CORS

import threading
import json
import paramiko
import re
import queue
import time

app = Flask(__name__)
CORS(app)  

data_queue = queue.Queue()
time_spent = 0






# Calcular Distancias etc etc

coordinates_history = []  
total_distance = 0.0

def haversine_distance(coord1, coord2):

    # Raio da Terra em metros
    R = 6371000
    
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)
    
    a = (sin(delta_phi / 2) ** 2 +
         cos(phi1) * cos(phi2) *
         sin(delta_lambda / 2) ** 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c



def update_distance(new_lat, new_lon):

    global total_distance, coordinates_history
    
    if new_lat is None or new_lon is None:
        return total_distance
    
    new_point = (new_lat, new_lon)
    
    if coordinates_history:
        last_point = coordinates_history[-1]
        segment_distance = haversine_distance(last_point, new_point)
        total_distance += segment_distance
    
    coordinates_history.append(new_point)

    return total_distance


def velocidade_media(total_distance, tempo): # m/s
    return total_distance / tempo

def velocidade(tempo): # m/s
    previous_location = coordinates_history[-2]
    last_location = coordinates_history[-1]
    return haversine_distance(previous_location, last_location) / (tempo - (tempo -2)) # Solução Robusca que precisa ser revisada

def deslocamento(): # m
    return haversine_distance(coordinates_history[len(coordinates_history) - 1], coordinates_history[0])















# def ssh_data_fetcher():
#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect("192.168.1.190", port=22, username="cansat", password="esca")
#     command = f"bash -i -c 'source /home/cansat/cansat/bin/activate && python3 /home/cansat/Code/CanSat/Python/Main.py'"
#     stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)

#     pattern = re.compile(r"(\{.*\})")
#     for line in stdout:
#         match = pattern.search(line)
#         if match:
#             try:
#                 data = eval(match.group()) 
#                 data_queue.put(data)
#             except:
#                 continue


# USAR EM CASO DE DEBUG


def clock():
    global time_spent
    while True:
        time.sleep(1)
        time_spent += 1

def ssh_data_fetcher():
    print("Iniciando conexão SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("192.168.1.190", port=22, username="cansat", password="esca")
    print("Conectado!")
    command = f"bash -i -c 'source /home/cansat/cansat/bin/activate && python3 /home/cansat/Code/CanSat/Python/Main.py'"
    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)

    pattern = re.compile(r"\{.*?\}")
    for line in stdout:
        print("RECEBIDO:", line)  # <--- debug
        match = pattern.search(line)
        if match:
            try:
                data = json.loads(match.group())
                data_queue.put(data)
            except Exception as e:
                print("Erro ao processar linha:", e)


# Eliminar antes do lançamento, pode ser um risco de segurança (so existe para meios de teste)
# No momento esta desativado

    
@app.route("/stream")
def stream():
    def event_stream():
        while True:
            data = data_queue.get()
            data['time_spent'] = time_spent
            if data['latitude'] is not None and data['longitude'] is not None:
                data['total_distance'] = update_distance(data['latitude'], data['longitude'])
                data['vel_media'] = velocidade_media(data['total_distance'], time_spent)
                data['vel'] = velocidade(time_spent)
                data['des'] = deslocamento()
            yield f"data: {json.dumps(data)}\n\n"
            
    return Response(event_stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    threading.Thread(target=ssh_data_fetcher, daemon=True).start()
    threading.Thread(target=clock, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)

