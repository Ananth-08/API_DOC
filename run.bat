@echo off
echo ===================================================
echo   Starting REST API Designer Project
echo ===================================================
echo.

echo [1/2] Starting Backend Service (FastAPI) in a new window...
start "FastAPI Backend" cmd /k "cd backend && python main.py"

echo [2/2] Starting Frontend Service (Vite + React) in a new window...
start "Vite Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ===================================================
echo   Services are starting up!
echo   - Backend API: http://localhost:8000
echo   - Frontend UI: http://localhost:3000
echo.
echo   Keep this window or the newly opened windows open.
echo   Press any key to close this launcher window...
echo ===================================================
pause > nul
