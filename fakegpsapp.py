
from math import cos, pi, sin, radians, atan2, sqrt
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
time_spent = 0

def clock():
    global time_spent
    while True:
        time.sleep(1)
        time_spent += 1



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


def velocidade_media(total_distance, tempo): # km/s
    if tempo == 0:
        return
    else:
        return total_distance / (tempo / 3600) # (distance / (tempo / 3600) = distance * (3600 / tempo))

def velocidade(): # km/s
    if len(coordinates_history) < 2:
        return 0
    else:
        previous_location = coordinates_history[-2]
        last_location = coordinates_history[-1]
        return haversine_distance(previous_location, last_location) * 3600 # Solução Robusca que precisa ser revisada (des / (1/3600) = des * 3600)

def deslocamento(): # km
    return haversine_distance(coordinates_history[-1], coordinates_history[0])



def fake_gps_generator():
    lat = 41.5600
    lon = -8.4000
    direction = random.uniform(-pi, pi)
    lat_change = 0 
    lon_change = 0

    while True:


        total_distance = update_distance(lat, lon)


        multiplier = random.uniform(0.00002, 0.00005) 

        lat_change = (sin(direction) * multiplier)
        lon_change = (cos(direction) * multiplier) 
        direction += random.uniform(-0.4, 0.4)

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
            "cpl": random.randint(1, 10),
            "time_spent": time_spent,
            "total_distance": total_distance,
            "vel_media": velocidade_media(total_distance, time_spent),
            "vel": velocidade(),
            "des": deslocamento()
            
        }

        data_queue.put(fake_data)
        time.sleep(1) 



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

    threading.Thread(target=clock, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
