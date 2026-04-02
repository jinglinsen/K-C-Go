@echo off
echo Starting K-C-go Community Hub...

start cmd /k "call start_backend.bat"
start cmd /k "call start_frontend.bat"

echo All services are starting up!
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:5173 (or check console)
pause
