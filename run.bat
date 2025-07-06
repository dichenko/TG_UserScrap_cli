@echo off
echo ========================================
echo    Telegram Chat Exporter
echo ========================================
echo.

REM Проверяем существование виртуального окружения
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Активируем виртуальное окружение
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Проверяем установлены ли зависимости
echo Checking dependencies...
pip show telethon >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting Telegram Chat Exporter...
echo ========================================
echo.

REM Запускаем программу
python main.py

echo.
echo ========================================
echo Program finished. Press any key to exit...
pause >nul 