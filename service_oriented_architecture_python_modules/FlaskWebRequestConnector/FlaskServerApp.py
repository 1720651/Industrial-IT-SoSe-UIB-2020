# !DOCUMENTATION SPHINX STYLE

# -*- PingMyHealth -*-
# Rik Wachner - 1720651 - PingMyHealth Project 2020 - IIT

"""
PingMyHealth flask server
--------------------------------------------------------------------------

Server process web request and change openhab item states

"""
import os
import sys
from datetime import datetime, timezone
from flask import Flask, render_template
from influxdb import InfluxDBClient
import requests

# ----------------------------------------------------------------------- #
# APP = FLASK(__NAME__)                                                   #
# ----------------------------------------------------------------------- #
# To Bypass pyinstall flask "missing folder", Flask need the static and template folder
if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)

# ----------------------------------------------------------------------- #
# PARAMS                                                                  #
# ----------------------------------------------------------------------- #
version = "1.0.0"
influxdb_server_host, influxdb_server_port = "localhost", 8086 # InfluxDB adress
openhab_server_host, openhab_server_port = "localhost", 8080 # OpenHAB adress
write_database_name = "ifttt_web_request_db" # InfluxDB database name
measurement_name = "ifttt_to_openhab_web_request" # InfluxDB measurement name
openhab_rest_api = "http://{}:{}/rest".format(openhab_server_host, openhab_server_port) # Building REST 


def write_to_database(key, value, success, status_code):
    """ Connect to the database and write request key, value and the success state

    :param string key: value parameter from ifttt web request
    :param string value: value parameter from ifttt web request
    :param bool success: ifttt web request success state
    :param string status_code: http status code of rest api call
    """
    app.logger.info('CONNECTING TO THE DATABASE SERVER...')
    influxdb_client = InfluxDBClient(influxdb_server_host, influxdb_server_port) # Connect to DB
    influxdb_client.create_database(write_database_name) # Create DB, if none exist
    influxdb_client.switch_database(write_database_name) # Switch to the created DB
    app.logger.info('CONNECTING TO THE DATABASE SERVER SUCCESSFULLY')
    app.logger.info('STARTING TO FORMAT COLLECTED DATA FOR THE DATABASE...')
    timestamp = datetime.now(timezone.utc) # Get a Timestamp
    formated_data = [{
        'measurement': measurement_name,
        'time': timestamp,
        'tags': {
            'scriptVersion': version,
        },
        'fields': {
            'webRequestKey': key,
            'webRequestValue': value,
            'success': success,
            'statusCode': status_code
        }
    }]
    app.logger.debug(formated_data)
    app.logger.info('WRITE FORMATTED DATA TO THE DATABASE...')
    influxdb_client.write_points(formated_data)
    app.logger.info('WRITING TO THE DATABASE SERVER SUCCESSFULLY')
    influxdb_client.close() # Close connection


@app.route('/')
def index():
    """ Default domain decorator
    """
    return render_template("index.html") # Show a welcome screen, when call the default domain decorator


@app.route('/<key>/<value>', methods=["POST", "GET"])
def ifttt_web_request(key, value):
    """ Ifttt web request decorator

    :param string key: key parameter from ifttt web request
    :param string value: value parameter from ifttt web request
    """
    try:
        app.logger.info("WEB REQUEST WITH KEY '%s' AND VALUE '%s'" % (key, value))
        app.logger.info('TRANSLATE IFTTT WEB REQUEST TO OPENHAB REST API CALL...')
        response = requests.post(url="{}/items/{}".format(openhab_rest_api, key), data=value)
        # For successful API call, response code will be 200 (OK)
        if response.ok:
            success = True
            app.logger.info('TRANSLATE IFTTT WEB REQUEST TO OPENHAB COMMAND SUCCESSFULLY')
        # If response code is not ok (200), print the resulting http error code with description
        else:
            raise response.raise_for_status()
    except Exception as e:
        success = False
        app.logger.error('TRANSLATE IFTTT WEB REQUEST TO OPENHAB COMMAND FAILED: ' + str(e))
    finally:
        write_to_database(key, value, success, response.status_code) # No matter what, record the call
        return render_template("index.html") # Just for fun ~ unnecessary 


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000) # Start Flask Server
