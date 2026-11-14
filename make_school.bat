@echo off
cd /d "%~dp0"
python make_video.py school
echo.
echo Video is in the output folder.
pause
