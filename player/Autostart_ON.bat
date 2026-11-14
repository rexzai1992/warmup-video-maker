@echo off
REM Start the warm-up video automatically when this PC turns on (Windows Startup folder).
REM Run again with "japan" to switch:  Autostart_ON.bat japan
cd /d "%~dp0"
set "WHICH=Start_Warmup.bat"
if /i "%~1"=="japan" set "WHICH=Start_Warmup_Japan.bat"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
(
  echo @echo off
  echo timeout /t 20 /nobreak ^>nul
  echo call "%~dp0%WHICH%"
) > "%STARTUP%\WarmUp_Video.bat"
echo Auto-start is ON: %WHICH% will play 20 seconds after Windows starts.
echo To turn it off, run Autostart_OFF.bat
pause
