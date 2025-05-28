# Tinha feito o codigo aqui mas decidi colocar direto no app
def convert_csv_to_json(
    inside_temp, inside_hum, external_temp, external_hum,
    accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z,
    mag_x, mag_y, mag_z, pi_temp, lat, lon, alt,
    pressure, temp_bmp, alt_bmp, uv, ambient_light,
    uvi, lux, cpl
):

    return {
        "temperature": inside_temp,
        "humidity": inside_hum,
        "temperature_ext": external_temp,
        "humidity_ext": external_hum,
        "accel_x": accel_x,
        "accel_y": accel_y,
        "accel_z": accel_z,
        "gyro_x": gyro_x,
        "gyro_y": gyro_y,
        "gyro_z": gyro_z,
        "pi_temp": pi_temp,
        "latitude": lat,
        "longitude": lon,
        "altitude": alt,
        "pressure": pressure,
        "temp_bmp": temp_bmp,
        "alt_bmp": alt_bmp,
        "uv": uv,
        "ambient_light": ambient_light,
        "uvi": uvi,
        "lux": lux,
        "cpl": cpl
    }


