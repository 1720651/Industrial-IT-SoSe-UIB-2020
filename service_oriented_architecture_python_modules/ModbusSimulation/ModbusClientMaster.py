# !DOCUMENTATION SPHINX STYLE

# -*- PingMyHealth -*-
# Rik Wachner - 1720651 - PingMyHealth Project 2020 - IIT

"""
PingMyHealth synchronous pymodbus client
----------------------------------------------------------------------------

Simple modbus client (pymodbus) for reading server data

"""
from influxdb import InfluxDBClient
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from datetime import datetime, timezone
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
modbus_server_host, modbus_server_port = "localhost", 502 # Modbus Server adress
influxdb_server_host, influxdb_server_port = "localhost", 8086 # InfluxDB adress
write_database_name = "modbus_i_o_db" # Modbus database name
data_sampling_rate = 10 # Rate when the Modbus Server data should be polled

# ----------------------------------------------------------------------- #
# MODBUS COILS REGISTER                                                   #
# ----------------------------------------------------------------------- #
# modbus_coils_registers = None

# ----------------------------------------------------------------------- #
# MODBUS DISCRETE INPUTS REGISTER                                         #
# ----------------------------------------------------------------------- #
# modbus_discrete_inputs_registers = None

# ----------------------------------------------------------------------- #
# MODBUS INPUT REGISTER                                                   #
# ----------------------------------------------------------------------- #
modbus_input_registers = {
    # ----------------------------------------------------------------------- #
    # NILAN IIT-SERIES COMPACT X MODBUS INPUT REGISTER (30000-30249)          #
    # ----------------------------------------------------------------------- #
    # (adress, name, scale)
    "nilan_input_register": [
        (0, "Outlet temperature", 100),
        (1, "Room temperature", 100),
        (100, "Relative Room Humidity", 1),
        (200, "CO2 level", 1),
        (201, "Summer State", 1)
    ],
    # ----------------------------------------------------------------------- #
    # KOERPERFETTWAAGE IIT-SERIES ONE MODBUS INPUT REGISTER (30250-30499)     #
    # ----------------------------------------------------------------------- #
    # (adress, name, scale)
    "koerperfettwaage_input_register": [
        (250, "Body mass index", 100),
        (251, "Bodyweight", 100),
        (252, "Body fat percentage", 100),
        (253, "Fat-free mass", 100),
        (254, "Fat-free mass index", 100),
        (255, "Muscle percentage", 100)
    ],
    # ----------------------------------------------------------------------- #
    # FITNESSBAND IIT-SERIES RUNNER24 MODBUS INPUT REGISTER (30500-30749)     #
    # ----------------------------------------------------------------------- #
    # (adress, name, scale)
    "fitnessband_input_register": [
        (500, "Age", 1),
        (501, "Sex", 1),
        (600, "Arterial oxygen saturation", 1),
        (601, "Pulse", 1),
        (602, "Systolic blood pressure value", 1),
        (603, "Diastolic blood pressure value", 1),
        (604, "Blood heat", 100)
    ],
    # ----------------------------------------------------------------------- #
    # CHOLESTERIN FASTCHECKER IIT-SERIES MODBUS INPUT REGISTER (30750-30999)  #
    # ----------------------------------------------------------------------- #
    # (adress, name, scale)
    "cholesterin_fastchecker_input_register": [
        (750, "Cholesterin", 1)
    ]
}

# ----------------------------------------------------------------------- #
# MODBUS HOLDING REGISTER                                                 #
# ----------------------------------------------------------------------- #
modbus_holding_registers = {
    # ----------------------------------------------------------------------- #
    # NILAN IIT-SERIES COMPACT X MODBUS HOLDING REGISTER (40001-40249)        #
    # ----------------------------------------------------------------------- #
    # (adress, name, scale)
    "nilan_holding_register": [
        (0, "Fan Speed", 1),
        (100, "Minimum room temperature", 100),
        (101, "Maximum room temperature", 100),
        (102, "Wanted room temperature", 100),
        (103, "Minimum water temperature", 100),
        (104, "Maximum water temperature", 100),
        (105, "Wanted water temperature", 100),
        (200, "Allow active cooling", 1),
        (201, "Electrical supplement heater", 1),
        (202, "Cooling and heating at the same time", 1),
        (203, "Fire Alarm", 1)
    ]
}


def database_connection():
    """ Connect to the database
    """
    client = InfluxDBClient(influxdb_server_host, influxdb_server_port) # Connect to DB
    client.create_database(write_database_name) # Create DB, if none exist
    client.switch_database(write_database_name) # Switch to the created DB
    return client


def run_synchronous_client():
    """Start the synchronous modbus server via pymodbus
    """
    try:
        log.info('CONNECT TO MODBUS SERVER...')
        modbus_client = ModbusClient(modbus_server_host, modbus_server_port) # Create Connection
        modbus_client.connect() # Connect to the Modbus Server
        log.info('CONNECT TO MODBUS SERVER SUCCESSFULLY')
        log.info('CONNECTING TO THE DATABASE SERVER...')
        influxdb_client = database_connection() # Connect to the InfluxDB Server
        log.info('CONNECTING TO THE DATABASE SERVER SUCCESSFULLY')
        result = {}
        while True:
            # log.info('READ WHOLE COIL REGISTER...')
            # read whole coil register
            # result.update = {registers: {register: modbus_client.read_coils(register[0]).registers for register in
            #                       modbus_coils_registers[registers]} for registers in modbus_coils_registers}
            # log.info('READ WHOLE COIL REGISTER SUCCESSFULLY')
            # log.info('READ WHOLE DISCRETE INPUTS REGISTER...')
            # read whole discrete inputs register
            # result.update = {registers: {register: modbus_client.read_discrete_inputs(register[0]).registers for register in
            #                       modbus_discrete_inputs_registers[registers]} for registers in modbus_discrete_inputs_registers}
            # log.info('READ WHOLE DISCRETE INPUTS SUCCESSFULLY')
            log.info('READ WHOLE INPUT REGISTER...')
            # read whole input register
            result = {registers: {register: modbus_client.read_input_registers(register[0]).registers for register in
                                  modbus_input_registers[registers]} for registers in modbus_input_registers}
            log.info('READ WHOLE INPUT REGISTER SUCCESSFULLY')
            log.info('READ WHOLE HOLDING REGISTER...')
            # read whole holding register
            result.update(
                {registers: {register: modbus_client.read_holding_registers(register[0]).registers for register in modbus_holding_registers[registers]} for registers in modbus_holding_registers})
            log.info('READ WHOLE HOLDING REGISTER SUCCESSFULLY')
            timestamp = datetime.now(timezone.utc)
            log.info('STARTING TO FORMAT COLLECTED DATA FOR THE DATABASE...')
            formated_data = []
            for register in result:
                formated_data += [{
                    'measurement': register,
                    'time': timestamp,
                    'tags': {
                        'scriptVersion': version,
                        'register': register_entry_details[0],
                        'description': register_entry_details[1],
                    },
                    'fields': {
                        'value': result[register][register_entry_details][0],
                        'valueScaled': result[register][register_entry_details][0] / register_entry_details[2]
                    }
                } for register_entry_details in result[register]]
            log.debug(formated_data)
            log.info('WRITE FORMATED DATA TO THE DATABASE...')
            influxdb_client.write_points(formated_data)
            log.info('WRITING TO THE DATABASE SERVER SUCCESSFULLY')
            time.sleep(data_sampling_rate)
    except Exception as e:
        log.error('MODBUS CLIENT CONNECTION FATAL ERROR: ' + str(e))


if __name__ == "__main__":
    run_synchronous_client()
