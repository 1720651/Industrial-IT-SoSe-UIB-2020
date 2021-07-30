:: -*- PingMyHealth -*-
:: Rik Wachner - 1720651 - PingMyHealth Project 2020 - IIT
@ECHO off
ECHO PingMyHome Proof of Concept DEBUG MODE [1.0]
ECHO Call PingMyHome Proof of Concept Service Stopper...
cd C:\PingMyHealth\nssm-2.24\win32
CALL service_stop.bat
ECHO.
ECHO Start InfluxDB [DEBUG] Service...
START cmd /k "cd C:\PingMyHealth\influxdb-1.8.0-1 && influxd.exe"
timeout 3
ECHO Start InfluxDB [DEBUG] Terminal...
START cmd /k "cd C:\PingMyHealth\influxdb-1.8.0-1 && influx.exe"
timeout 3
ECHO.
ECHO Start Modbus Server Slave Simulation [DEBUG] Service...
START cmd /k "cd C:\PingMyHealth\service_oriented_architecture_python_modules\ModbusSimulation && python ModbusServerSlaveSimulation.py"
timeout 3
ECHO.
ECHO Start Modbus Client Master [DEBUG] Service...
START cmd /k "cd C:\PingMyHealth\service_oriented_architecture_python_modules\ModbusSimulation && python ModbusClientMaster.py"
timeout 3
ECHO.
ECHO Start OpenWeatherMap Data Collector [DEBUG] Service...
START cmd /k "cd C:\PingMyHealth\service_oriented_architecture_python_modules\OpenWeatherMapDataCollector && python OpenWeatherMapDataCollector.py"
timeout 3
ECHO.
ECHO Start PingMyHealth Checker [DEBUG] Service...
START cmd /k "cd C:\PingMyHealth\service_oriented_architecture_python_modules\PingMyHealthChecker && python PingMyHealthChecker.py"
timeout 3
ECHO.
ECHO Start MachineLearningEnvironmentConnector [DEBUG] Service...
START cmd /k "cd C:\PingMyHealth\service_oriented_architecture_python_modules\MachineLearningEnvironment && python MachineLearningEnvironmentConnector.py"
timeout 3
ECHO.
ECHO Start OpenHAB [DEBUG] Service...
START cmd /k "cd C:\PingMyHealth\openhab-2.5.5 && start_debug.bat"
timeout 3
ECHO.
ECHO Start Flask Web Request Connector Service...
START cmd /k "cd C:\PingMyHealth\service_oriented_architecture_python_modules\FlaskWebRequestConnector && python FlaskServerApp.py"
timeout 3
ECHO.
ECHO Start Grafana [DEBUG] Service...
START cmd /k "cd C:\PingMyHealth\grafana-7.0.1\bin && grafana-server.exe"
pause