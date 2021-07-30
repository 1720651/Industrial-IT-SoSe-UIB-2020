:: -*- PingMyHealth -*-
:: Rik Wachner - 1720651 - PingMyHealth Project 2020 - IIT
@ECHO off
cd C:\PingMyHealth\nssm-2.24\win32
ECHO PingMyHome Proof of Concept Service Starter [1.0]
ECHO.
ECHO Start InfluxDB Service...
nssm start influxdb
timeout 2
ECHO.
ECHO Start Modbus Server Slave Simulation Service...
nssm start modbusserverslavesimulation
timeout 2
ECHO.
ECHO Start Modbus Client Master Service...
nssm start modbusclientmaster
timeout 1
ECHO.
ECHO Start OpenWeatherMap Data Collector Service...
nssm start openweathermapdatacollector
timeout 1
ECHO.
ECHO Start PingMyHealth Checker Service...
nssm start pingmyhealthchecker
timeout 1
ECHO.
ECHO Start OpenHAB Service...
nssm start openhab
timeout 1
ECHO.
ECHO Start Flask Web Request Connector Service...
nssm start flaskwebrequestconnector 
timeout 1
ECHO.
ECHO Start Grafana Service...
nssm start grafana
pause