# Tinha feito o codigo aqui mas decidi colocar direto no app
from math import nan


def convert_csv_to_json(
    time, lat, lon, alt,
):

    return {
        "temperature": 0,
        "humidity": 0,
        "temperature_ext": 0,
        "humidity_ext": 0,
        "accel_x": 0,
        "accel_y": 0,
        "accel_z": 0,
        "gyro_x": 0,
        "gyro_y": 0,
        "gyro_z": 0,
        "pi_temp": 0,
        "latitude": lat,
        "longitude": lon,
        "altitude": alt,
        "pressure": 0,
        "temp_bmp": 0,
        "alt_bmp": 0,
        "uv": 0,
        "ambient_light": 0,
        "uvi": 0,
        "lux": 0,
        "cpl": 0,
        "ozone": 0
    }


