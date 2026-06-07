@echo off
echo Starting Sensor Simulator...
cd /d "%~dp0"
python -m src.sensor.sensor_client
pause