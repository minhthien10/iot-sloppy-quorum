@echo off
echo Starting IoT Sensor Hub Gateway...
cd /d "%~dp0"
python -m src.gateway.main
pause