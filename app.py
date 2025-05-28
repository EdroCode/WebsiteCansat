from flask import Flask, Response, jsonify
from math import radians, sin, cos, sqrt, atan2
from flask_cors import CORS
from extract import convert_csv_to_json
from time import sleep
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

global teste

# -----------------------------------
# Not the best code, but it works so shut up
# -----------------------------------




# Calcular Distancias etc etc

coordinates_history = []  
total_distance = 0.0

def haversine_distance(coord1, coord2):

    # Raio da Terra em km
    R = 6371
    
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


def velocidade_media(total_distance, tempo): # km/h
    return total_distance / (tempo / 3600) # (distance / (tempo / 3600) = distance * (3600 / tempo))

def velocidade(tempo): # km/h
    if len(coordinates_history) < 2 or tempo <= 0:
        return 0
    previous_location = coordinates_history[-2]
    last_location = coordinates_history[-1]
    return haversine_distance(previous_location, last_location) * (3600 / tempo) # Solução Robusca que precisa ser revisada (des / (1/3600) = des * 3600)

def deslocamento(): # km
    return haversine_distance(coordinates_history[-1], coordinates_history[0])















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

# def ssh_data_fetcher():
#     print("Iniciando conexão SSH...")
#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect("192.168.1.190", port=22, username="cansat", password="esca")
#     print("Conectado!")
#     command = f"bash -i -c 'source /home/cansat/cansat/bin/activate && python3 /home/cansat/Code/CanSat/Python/Main.py'"
#     stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)

#     pattern = re.compile(r"\{.*?\}")
#     for line in stdout:
#         print("RECEBIDO:", line)  # <--- debug
#         match = pattern.search(line)
#         if match:
#             try:
#                 data = json.loads(match.group())
#                 data_queue.put(data)
#             except Exception as e:
#                 print("Erro ao processar linha:", e)


# Eliminar antes do lançamento, pode ser um risco de segurança (so existe para meios de teste)
# No momento esta desativado

    

import random


def gerar_csv_fake():
    valores = [
        round(random.uniform(15, 18), 2),  # inside_temp
        round(random.uniform(60, 85), 2),  # inside_hum
        round(random.uniform(17, 18), 2),  # external_temp
        round(random.uniform(60, 65), 2),  # external_hum
        round(random.uniform(-1, 1), 9),   # accel_x
        round(random.uniform(-1, 1), 9),   # accel_y
        round(random.uniform(-1, 1), 9),   # accel_z
        round(random.uniform(0, 10), 9),   # gyro_x
        round(random.uniform(0, 10), 9),   # gyro_y
        round(random.uniform(0, 10), 9),   # gyro_z
        None, None, None,                  # mag_x, mag_y, mag_z (ignorados, pode colocar 0.0)
        round(random.uniform(45, 50), 1),  # pi_temp
        round(random.uniform(-90, 90), 6), # lat
        round(random.uniform(-180, 180),6),# lon
        round(random.uniform(80, 90), 2),  # alt
        round(random.uniform(1, 1.5), 2),  # pressure
        round(random.uniform(1, 1.5), 2),  # temp_bmp
        round(random.uniform(31880, 31890), 2),  # alt_bmp
        round(random.uniform(0, 5), 2),    # uv
        round(random.uniform(0.5, 1), 2),  # ambient_light
        round(random.uniform(0, 1), 2),    # uvi
        round(random.uniform(0.5, 1), 2),  # lux
        random.randint(2, 10)              # cpl
    ]

    # Substituir None por 0.0
    valores = [v if v is not None else 0.0 for v in valores]

    return ",".join(str(v) for v in valores)


















# Requiremente PYSERIAL
import serial.tools.list_ports 
ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()

portList = []

def data_fetcher():
    while True:
        if teste == False:
            if serialInst.in_waiting:
                try:
                    packet = serialInst.readline()

                    decoded = packet.decode('utf-8').strip()
                    print("Recebido:", decoded)
                    values = decoded.split(",")

                    if len(values) == 25:   # n colunas
                        float_values = list(map(float, values))  
                        data = convert_csv_to_json(*float_values)
                        data_queue.put(data)
                    else:
                        print("Número incorreto de colunas:", len(values))

                except Exception as e:
                    print(f"Erro ao processar dado serial: {e}")
        else:
            
            # TEST MODE
            csv_fake = gerar_csv_fake()
            print(csv_fake)
            values = csv_fake.split(",")
            float_values = list(map(float, values))
            data = convert_csv_to_json(*float_values)
            data_queue.put(data)
            sleep(1)
            



@app.route("/stream")
def stream():
    def event_stream():
        last_time = -1.0
        while True:
            data = data_queue.get()
            data['time_spent'] = time_spent
            if data['latitude'] is not None and data['longitude'] is not None:
                data['total_distance'] = update_distance(data['latitude'], data['longitude'])
                data['vel_media'] = velocidade_media(data['total_distance'], time_spent)
                data['vel'] = velocidade(time_spent - last_time)
                data['des'] = deslocamento()
                delta_time = time_spent - last_time
                if delta_time > 0:
                    data['cpm'] = data["cpl"] * (60 / delta_time)
                else:
                    data['cpm'] = 0 
            last_time = time_spent
            yield f"data: {json.dumps(data)}\n\n"
            
    return Response(event_stream(), mimetype="text/event-stream")




if __name__ == "__main__":

    for port in ports:
        portList.append(str(port))
        print(str(port))

    val = input("Seleciona a porta: COM")

    for x in range(0, len(portList)):
        if portList[x].startswith("COM" + str(val)):
            portVar = "COM" + str(val)
            print(portList[x])

    
    teste = False # Default
    x = input("Versão teste? (y/n):")
    while x.lower != "n" or "y":
        if x.lower() == "y":
            teste = True
            break
        elif x.lower() == "n":
            teste = False
            break

    print(teste)

    serialInst.baudrate = 9600 # Importante, verificar no código do Arduino
    serialInst.port = portVar
    serialInst.open()
        
    threading.Thread(target=data_fetcher, daemon=True).start()
    threading.Thread(target=clock, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)

    



