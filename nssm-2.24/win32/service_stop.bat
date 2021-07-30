:: -*- PingMyHealth -*-
:: Rik Wachner - 1720651 - PingMyHealth Project 2020 - IIT
@ECHO off
cd C:\PingMyHealth\nssm-2.24\win32
ECHO PingMyHome Proof of Concept Service Stopper [1.0]
ECHO.
ECHO Stop Grafana Service...
nssm stop grafana
ECHO.
ECHO Stop Flask Web Request Connector Service...
nssm stop flaskwebrequestconnector 
ECHO.
ECHO Stop OpenHAB Service...
nssm stop openhab
ECHO.
ECHO Stop PingMyHealth Checker Service...
nssm stop pingmyhealthchecker
timeout 1
ECHO.
ECHO Stop OpenWeatherMap Data Collector Service...
nssm stop openweathermapdatacollector
ECHO.
ECHO Stop Modbus Client Master Service...
nssm stop modbusclientmaster
ECHO.
ECHO Stop Modbus Server Slave Simulation Service...
nssm stop modbusserverslavesimulation
ECHO.
ECHO Stop InfluxDB Service...
nssm stop influxdb
timeout 3