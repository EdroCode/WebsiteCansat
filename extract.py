# Tinha feito o codigo aqui mas decidi colocar direto no app
from math import nan


def convert_csv_to_json(
    time, temp, hum, press, alt, hea, ax, ay, az, gx, gy, gz, gpsval, lat, lon, altgps, speed, sat
):

    return {
        "time": time,
        "temperature": temp,
        "humidity": hum,
        "pressure": press,
        "altitude": alt,

        "heading": hea,

        "accel_x": ax,
        "accel_y": ay,
        "accel_z": az,
        "gyro_x": gx,
        "gyro_y": gy,
        "gyro_z": gz,

        "gps_valid": gpsval,
        "latitude": lat,
        "longitude": lon,
        "altitude_gps": altgps,
        "speed": speed,
        "satellites": sat
    }


