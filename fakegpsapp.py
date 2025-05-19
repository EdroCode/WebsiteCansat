
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
time_spent = 0

def clock():
    global time_spent
    while True:
        time.sleep(1)
        time_spent += 1

def fake_gps_generator():
    lat = 41.5600
    lon = -8.4000
    direction = random.uniform(-pi, pi)
    lat_change = 0 
    lon_change = 0

    while True:


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
