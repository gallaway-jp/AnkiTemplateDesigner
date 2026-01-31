@echo off
setlocal enabledelayedexpansion

REM Add Node.js to PATH
set "PATH=C:\Program Files\nodejs;%PATH%"

REM Change to web directory
cd /d "d:\Development\Python\AnkiTemplateDesigner\web"

REM Start the dev server
call npm run dev

pause
