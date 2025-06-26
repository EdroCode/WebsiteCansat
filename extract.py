# Tinha feito o codigo aqui mas decidi colocar direto no app
from math import nan


def convert_csv_to_json(
    time, inside_temp, inside_hum,
    accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, lat, lon, alt,
    pressure, temp_bmp, alt_bmp, ozone,
):

    return {
        "temperature": inside_temp,
        "humidity": inside_hum,
        "temperature_ext": 0,
        "humidity_ext": 0,
        "accel_x": accel_x,
        "accel_y": accel_y,
        "accel_z": accel_z,
        "gyro_x": gyro_x,
        "gyro_y": gyro_y,
        "gyro_z": gyro_z,
        "pi_temp": 0,
        "latitude": lat,
        "longitude": lon,
        "altitude": alt,
        "pressure": pressure,
        "temp_bmp": temp_bmp,
        "alt_bmp": alt_bmp,
        "uv": 0,
        "ambient_light": 0,
        "uvi": 0,
        "lux": 0,
        "cpl": 0,
        "ozone": ozone
    }


