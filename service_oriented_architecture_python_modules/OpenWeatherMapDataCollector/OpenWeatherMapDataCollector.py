# !DOCUMENTATION SPHINX STYLE

# -*- PingMyHealth -*-
# Rik Wachner - 1720651 - PingMyHealth Project 2020 - IIT

"""
PingMyHealth openweathermap data collector
--------------------------------------------------------------------------

Server use the openweathermap api and store the data in the database

"""

from datetime import datetime, timezone
from influxdb import InfluxDBClient
import requests
import time

# ----------------------------------------------------------------------- #
# LOGGING                                                                 #
# ----------------------------------------------------------------------- #
import logging

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# ----------------------------------------------------------------------- #
# PARAMS                                                                  #
# ----------------------------------------------------------------------- #
version = "1.0.0"
owm_version = "2.5"
owm_location = "Ludwigshafen am Rhein, DE" # location
owm_api_key = "737f1139827be24d1ee2a02f546ad118" # OpenWeatherMap api key
influxdb_server_host, influxdb_server_port = "localhost", 8086
write_database_name = "openweathermap_db"
measurement_name = "openweatherdata"
data_sampling_rate = 30


def database_connection():
    """ Connect to the database
    """
    client = InfluxDBClient(influxdb_server_host, influxdb_server_port)
    client.create_database(write_database_name)
    client.switch_database(write_database_name)
    return client


def get_weather():
    """ Get openweathermap web request access
    """
    url = "https://api.openweathermap.org/data/{}/weather?q={}&units=metric&appid={}".format(owm_version, owm_location,
                                                                                             owm_api_key)
    r = requests.get(url)
    return r.json()


def run_measurement():
    """ Start to collect data via openweathermap api
    """
    temperature = None
    humidity = None
    pressure = None
    wind_speed = 0.0
    wind_degree = 0.0

    log.info('CONNECTING TO THE DATABASE SERVER...')
    client = database_connection()
    log.info('CONNECTING TO THE DATABASE SERVER SUCCESSFULLY')
    while True:
        try:
            log.info('STARTING TO COLLECT OPENWEATHERMAP MEASUREMENTS...')
            owm_measurement_raw = get_weather()
            timestamp = datetime.now(timezone.utc)
            temperature = round(float(owm_measurement_raw["main"].get("temp", temperature)), 2)
            humidity = round(float(owm_measurement_raw["main"].get("humidity", humidity)), 2)
            pressure = round(float(owm_measurement_raw["main"].get("pressure", pressure)), 2)
            wind_speed = round(float(owm_measurement_raw["wind"].get("speed", wind_speed)), 2)
            wind_degree = round(float(owm_measurement_raw["wind"].get("deg", wind_degree)), 2)
            log.info('COLLECTION SUCCESSFULLY')
            log.info('STARTING TO FORMAT COLLECTED DATA FOR THE DATABASE...')
            formated_data = [{
                'measurement': measurement_name,
                'time': timestamp,
                'tags': {
                    'scriptVersion': version,
                    'openWeatherMapVersion': owm_version,
                    'location': owm_location,
                },
                'fields': {
                    'temperature_celsius': temperature,
                    'humidity': humidity,
                    'pressure': pressure,
                    'windSpeed': wind_speed,
                    'windDegree': wind_degree
                }
            }]
            log.debug(formated_data)
            log.info('WRITE FORMATTED DATA TO THE DATABASE...')
            client.write_points(formated_data)
            log.info('WRITING TO THE DATABASE SERVER SUCCESSFULLY')
            time.sleep(data_sampling_rate)
        except Exception as e:
            log.error('COLLECTING OPENWEATHERMAP MEASUREMENT DATA FAILED: ' + str(e))
            return


if __name__ == '__main__':
    run_measurement()
