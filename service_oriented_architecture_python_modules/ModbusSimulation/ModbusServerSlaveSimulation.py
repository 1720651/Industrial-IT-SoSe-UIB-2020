# !DOCUMENTATION SPHINX STYLE

# -*- PingMyHealth -*-
# Rik Wachner - 1720651 - PingMyHealth Project 2020 - IIT

"""
PingMyHealth asynchronous pymodbus Server with updating Thread
--------------------------------------------------------------------------

Simple modbus server (pymodbus) with entries in the register to simulate data and having a background thread
updating the context while the server is operating

"""

from pymodbus.server.asynchronous import StartTcpServer
# from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from twisted.internet.task import LoopingCall
import random

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
# version = "1.0.0"
modbus_server_host, modbus_server_port = "localhost", 502
update_rate = 10 # Data simulation update rate

# ----------------------------------------------------------------------- #
# MODBUS REGISTER                                                         #
# ----------------------------------------------------------------------- #
modbus_input_registers = [
    # ----------------------------------------------------------------------- #
    # NILAN IIT-SERIES COMPACT X MODBUS INPUT REGISTER (30000-30249)          #
    # ----------------------------------------------------------------------- #
    # Register type, adresse, initial value, fluctuations (min, max), default threshold X<=value<=Y (min, max)
    (4, 0, 2600, (2250, 2800), (0, 5000)),
    (4, 1, 2400, (2000, 2500), (0, 6000)),
    (4, 100, 50, (45, 55), (0, 100)),
    (4, 200, 1000, (990, 1010), (0, 9999)),
    (4, 201, 1, None, (0, 1)),
    # ----------------------------------------------------------------------- #
    # KOERPERFETTWAAGE IIT-SERIES ONE MODBUS INPUT REGISTER (30250-30499)     #
    # ----------------------------------------------------------------------- #
    # Register type, adresse, initial value, fluctuations (min, max), default threshold X<=value<=Y (min, max)
    (4, 250, 2768, None, (0, 9999)),
    (4, 251, 8000, None, (0, 9999)),
    (4, 252, 2343, None, (0, 9999)),
    (4, 253, 6126, None, (0, 9999)),
    (4, 254, 1901, None, (0, 9999)),
    (4, 255, 2712, None, (0, 9999)),
    # ----------------------------------------------------------------------- #
    # FITNESSBAND IIT-SERIES RUNNER24 MODBUS INPUT REGISTER (30500-30749)     #
    # ----------------------------------------------------------------------- #
    # Register type, adresse, initial value, fluctuations (min, max), default threshold X<=value<=Y (min, max)
    (4, 500, 23, None, (0, 200)),
    (4, 501, 0, None, (0, 1)),
    (4, 600, 94, (90, 99), (0, 100)),
    (4, 601, 81, (80, 95), (0, 300)),
    (4, 602, 123, (120, 130), (0, 300)),
    (4, 603, 77, (75, 85), (0, 200)),
    (4, 604, 3633, (3690, 3710), (0, 7000)),
    # ----------------------------------------------------------------------- #
    # CHOLESTERIN FASTCHECKER IIT-SERIES MODBUS INPUT REGISTER (30750-30999)  #
    # ----------------------------------------------------------------------- #
    # Register type, adresse, initial value, fluctuations (min, max), default threshold X<=value<=Y (min, max)
    (4, 750, 125, (120, 130), (0, 500))
]
modbus_holding_registers = [
    # ----------------------------------------------------------------------- #
    # NILAN IIT-SERIES COMPACT X MODBUS HOLDING REGISTER (40000-40249)        #
    # ----------------------------------------------------------------------- #
    # Register type, adresse, initial value, fluctuations (min, max), default threshold X<=value<=Y (min, max)
    (3, 0, 75, None, (0, 100)),
    (3, 100, 1434, None, (0, 3999)),
    (3, 101, 2934, None, (0, 3999)),
    (3, 102, 2233, None, (0, 3999)),
    (3, 103, 3021, None, (1000, 3999)),
    (3, 104, 3345, None, (1000, 3999)),
    (3, 105, 3123, None, (0, 3999)),
    (3, 200, 1, None, (0, 1)),
    (3, 201, 1, None, (0, 1)),
    (3, 202, 1, None, (0, 1)),
    (3, 203, 0, None, (0, 1))
]

registers = modbus_input_registers + modbus_holding_registers # Merge registers


def updating_writer(arguments):
    """ A worker process that runs every so often and
    updates live values of the context, to simulation a
    fluctuation only for the Proof of Concept. It should
    be noted that there is a race condition for the update

    :param arguments: The input arguments to the call
    """
    log.debug("CHECK RULES AND CHANGE CONTEXT...")
    context = arguments[0]
    register_call = (None, None) #
    for register in registers:
        # Check, if register value is in default threshold range (min, max)
        if register[4][0] <= context[0].getValues(register[0], register[1])[0] <= register[4][1]:
            # Check, if fluctuations specified for that register value
            if register[3] is not None:
                log.debug("UPDATING THE CONTEXT...")
                # New "random" value / fluctuation
                context[0].setValues(register[0], register[1], [random.randint(register[3][0], register[3][1])])
                log.debug("UPDATING THE CONTEXT SUCCESSFULLY")
        else:
            # If the value is out of default threshold bounce -> reset it to the default value
            context[0].setValues(register[0], register[1], [register[2]])
    log.debug("CHECK RULES AND CHANGE CONTEXT SUCCESSFULLY")


def run_updating_server():
    """Start the asynchronous modbus server via pymodbus
    """
    log.info('SET UP REGISTER...')
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0] * 10000),
        co=ModbusSequentialDataBlock(0, [0] * 10000),
        hr=ModbusSequentialDataBlock(0, [0] * 10000),
        ir=ModbusSequentialDataBlock(0, [0] * 10000))
    context = ModbusServerContext(slaves=store, single=True)
    for register in registers:
        context[0].setValues(register[0], register[1], [register[2]])

    log.info('SET UP REGISTER SUCCESSFULLY')

    # log.info('INITIALIZE THE SERVER INFORMATION...')
    # identity = ModbusDeviceIdentification()
    # identity.VendorName = 'PingMyHealth'
    # identity.ProductCode = 'IITSoSe2020'
    # identity.VendorUrl = 'https://www.hs-mannheim.de/'
    # identity.ProductName = 'PyModbusServer'
    # identity.ModelName = 'IIT-SERIES'
    # identity.MajorMinorRevision = version
    # log.info('INITIALIZE THE SERVER INFORMATION SUCCESSFULLY')

    log.info('SET UP LOOP CONDITION...')
    log.debug('SECONDS DELAY / UPDATE TIME SET')
    time = update_rate
    loop = LoopingCall(f=updating_writer, arguments=(context,))
    log.debug('INITIALLY DELAY / UPDATE TIME BY TIME SET')
    loop.start(time, now=False)
    log.info('SET UP LOOP CONDITION SUCCESSFULLY')
    log.info('START SERVER AND UPDATE DATA FOR CLIENT CONNECTION...')
    # StartTcpServer(context, identity=identity, address=(host, port))
    StartTcpServer(context, address=(modbus_server_host, modbus_server_port))


if __name__ == "__main__":
    run_updating_server()
