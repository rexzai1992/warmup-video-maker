@echo off
REM ==========================================================
REM  Warm-Up video - auto play FULL SCREEN, on repeat
REM  Double-click to start. To close the video: press Alt + F4
REM  Choose which video below (file name inside the output folder):
REM ==========================================================
set "VIDEO=BackToSchool_WarmUp_15min.mp4"
REM set "VIDEO=Hana_Japan_WarmUp_15min.mp4"

set "HERE=%~dp0"
set "PAGE=file:///%HERE:\=/%player.html?v=../output/%VIDEO%"
set "FLAGS=--kiosk --autoplay-policy=no-user-gesture-required --disable-session-crashed-bubble --noerrdialogs --no-first-run --user-data-dir=%TEMP%\warmup_player"

set "BROWSER="
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "BROWSER=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not defined BROWSER if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "BROWSER=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if not defined BROWSER if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" set "BROWSER=%LocalAppData%\Google\Chrome\Application\chrome.exe"
if not defined BROWSER if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" set "BROWSER=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
if not defined BROWSER if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" set "BROWSER=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"

if not defined BROWSER (
  echo Chrome or Edge not found. Opening with the default video player instead...
  start "" "%HERE%..\output\%VIDEO%"
  exit /b
)

start "" "%BROWSER%" %FLAGS% "%PAGE%"
exit /b
