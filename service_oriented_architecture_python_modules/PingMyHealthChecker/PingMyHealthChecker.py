# !DOCUMENTATION SPHINX STYLE

# -*- PingMyHealth -*-
# Rik Wachner - 1720651 - PingMyHealth Project 2020 - IIT

"""
PingMyHealth Checker
----------------------------------------------------------------------------

Simple checker to proof the integration of an monitoring service

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
influxdb_server_host, influxdb_server_port = "localhost", 8086
modbus_server_host, modbus_server_port = "localhost", 502
write_database_name = "pingmyhealth_overwatch_db"
read_database_name = "modbus_i_o_db"
measurement_name = "overwatch"
only_triggered_rules = True # Only the triggered or all checked rules shoud be stored
data_sampling_rate = 10
data_sampling_rate_between_health_data_check = 0.5
health_data_field = 'value'
health_data_check = {
    # Machine
    "fitnessband_input_register": {
        # When this rule trigger:
        # Measurement: ((operator, operand),
        # ... then do this modbus register call:
        #              (register, adresse), (operator, operand, register, adresse, scale))
        "Blood heat": ((('<', 3700), ("=", 2442, 3, 102, 100)),
                       (('>', 3700), ("=", 2032, 3, 102, 100)),
                       )
        # When this rule trigger:
        # Measurement: ((operator, operand),
        # ... then do this modbus register call:
        #              (register, adresse), operator, operand, register, adresse, scale))
        #"Arterial oxygen saturation": ((('>', 95), ("=", 100, 3, 0, 1)),
        #                               (('<', 95), ("=", 50, 3, 0, 1))
        #                               )
    }
}
operator_lookup_table = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    '*': lambda x, y: x * y,
    '%': lambda x, y: x % y,
    '<': lambda x, y: x < y,
    '<=': lambda x, y: x <= y,
    '>': lambda x, y: x > y,
    '>=': lambda x, y: x >= y,
    '==': lambda x, y: x == y,
    '!=': lambda x, y: x != y,
    '=': lambda x, y: y
}


def database_connection():
    """ Connect to the database
    """
    client = InfluxDBClient(influxdb_server_host, influxdb_server_port)
    client.create_database(write_database_name)
    return client


def run_server():
    """Start the machine learning environment server
    """
    try:
        log.info('CONNECTING TO THE DATABASE SERVER...')
        influxdb_client = database_connection()
        log.info('CONNECTING TO THE DATABASE SERVER SUCCESSFULLY')

        log.info('CONNECTING TO THE MODBUS SERVER...')
        modbus_client = ModbusClient("localhost", 502)
        log.info('CONNECTING TO THE MODBUS SERVER SUCCESSFULLY')

        while True:
            log.info('READ DATABASE DATA...')
            for measurement in health_data_check:
                for description in health_data_check[measurement]:
                    influxdb_client.switch_database(read_database_name)
                    # Default InfluxDB database call
                    python_generator_iterator = influxdb_client.query(
                        "SELECT * FROM " + measurement + " GROUP BY * ORDER BY DESC LIMIT 1").get_points(
                        tags={'description': description})
                    log.info('READ DATABASE DATA SUCCESSFULLY')
                    influxdb_client.switch_database(write_database_name) # Change database
                    log.info('CHECK RULES...')
                    # You need a for loop, also if the select query only contains one value
                    for value in python_generator_iterator:
                        # Check now all rules
                        for rules in health_data_check[measurement][description]:
                            rule_operator = rules[0][0]
                            threshold = rules[0][1]
                            database_value = value[health_data_field]
                            change_operator = rules[1][0]
                            change_operand = rules[1][1]
                            register = rules[1][2]
                            address = rules[1][3]
                            scale = rules[1][4]
                            old_value, new_value = None, None
                            # Check, if the rule triggered
                            rule_bool = operator_lookup_table[rule_operator](threshold, database_value)
                            log.debug('%s %s %s = %s' % (threshold, rule_operator, database_value, rule_bool))
                            log.info('CHECK RULE SUCCESSFULLY')
                            log.info('SELECT MODBUS REGISTER...')
                            modbus_client.connect()
                            # get the old values
                            if register in (2, 'co'):
                                log.info('SELECT COIL REGISTER (WRITE-ONLY)')
                                old_value = modbus_client.read_coils(address).registers
                                # if the rule triggered, send the event
                                if rule_bool:
                                    new_value = operator_lookup_table[change_operator](old_value[0], change_operand)
                                    modbus_client.write_coils(address, [new_value])
                            # get the old values
                            elif register in (3, 'hr'):
                                log.info('SELECT HOLDING REGISTER (READ AND WRITE)')
                                old_value = modbus_client.read_holding_registers(address).registers
                                # if the rule triggered, send the event
                                if rule_bool:
                                    new_value = operator_lookup_table[change_operator](old_value[0], change_operand)
                                    modbus_client.write_registers(address, new_value)
                            else:
                                raise ValueError('%s IS NOT A VALID REGISTER NUMBER TO WRITE TO' % register)

                            modbus_client.close()
                            log.info('WRITE INTO MODBUS REGISTER SUCCESSFULLY')
                            modbus_client.close()
                            # In the params list you can desiced, if only the triggered or all checked rules shoud be stored 
                            if only_triggered_rules is False or only_triggered_rules and rule_bool:
                                log.info('FORMAT MONITORING DATA FOR THE DATABASE...')
                                timestamp = datetime.now(timezone.utc)
                                monitoring_data = [{
                                    'measurement': measurement_name,
                                    'time': timestamp,
                                    'tags': {
                                        'scriptVersion': version,
                                    },
                                    'fields': {
                                        'checkValueRegister': measurement,
                                        'checkValueDescription': description,
                                        'threshold': threshold,
                                        'ruleOperator': rule_operator,
                                        'databaseValue': database_value,
                                        'ruleTriggered': rule_bool,
                                        'changeRegister': register,
                                        'changeAddress': address,
                                        'oldRegisterValue': None if old_value is None else old_value[0],
                                        'changeOperator': change_operator,
                                        'changeOperand': change_operand,
                                        'newRegisterValue': new_value,
                                        'newRegisterValueScaled': None if new_value is None else new_value / scale
                                    }
                                }]
                                log.info('FORMAT RESULT DATA FOR THE DATABASE SUCCESSFULLY')
                                log.debug(monitoring_data)
                                log.info('WRITE FORMATED DATA TO THE DATABASE...')
                                influxdb_client.write_points(monitoring_data)
                                log.info('WRITING TO THE DATABASE SERVER SUCCESSFULLY')
                            time.sleep(data_sampling_rate_between_health_data_check)

            time.sleep(data_sampling_rate)

    except Exception as e:
        log.error('SERVER FATAL ERROR: ' + str(e))


if __name__ == "__main__":
    run_server()
