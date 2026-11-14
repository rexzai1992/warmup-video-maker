@echo off
cd /d "%~dp0"
echo Installing Python packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo Installing the hidden Chrome used for rendering...
python -m playwright install chromium
echo Installing the natural voice (Kokoro)...
call tools\setup_voice.bat
where ffmpeg >nul 2>nul || (echo !! ffmpeg not found. Run:  winget install Gyan.FFmpeg   then reopen this window.)
echo.
echo Setup finished.
pause
