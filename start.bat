@echo off
chcp 65001 >nul
setlocal
title Anonim Ask Bot
cd /d "%~dp0"
set PYTHONUTF8=1

echo.
echo ================= Anonim Ask Bot =================
echo.

rem ---------- Python qidiriladi ----------
set "PY="
where py.exe >nul 2>nul && set "PY=py -3"
if not defined PY where python.exe >nul 2>nul && set "PY=python"
if not defined PY goto NOPYTHON

rem ---------- .env tekshiriladi ----------
if not exist ".env" goto MAKEENV
goto CHECKVENV

:MAKEENV
echo [!] .env fayli topilmadi, .env.example dan nusxa olinyapti...
copy /Y ".env.example" ".env" >nul
echo.
echo [!] Hozir Notepad ochiladi.
echo     BOT_TOKEN= dan keyin @BotFather bergan tokenni qo'ying,
echo     Ctrl+S bosib SAQLANG, oynani yoping va bu yerda ENTER bosing.
echo.
notepad ".env"
echo.
pause

:CHECKVENV
if exist ".venv\Scripts\python.exe" goto DEPS

echo [*] Virtual muhit yaratilmoqda (bir marta)...
%PY% -m venv .venv
if not exist ".venv\Scripts\python.exe" goto VENVFAIL

:DEPS
echo [*] Kutubxonalar tekshirilmoqda (birinchi safar 1-2 daqiqa ketadi)...
".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet --disable-pip-version-check
".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 goto PIPFAIL

echo.
echo [*] Bot ishga tushyapti. To'xtatish uchun Ctrl+C bosing.
echo.
".venv\Scripts\python.exe" bot.py
echo.
echo [*] Bot to'xtadi.
pause
exit /b

:NOPYTHON
echo [XATO] Python topilmadi!
echo.
echo   1) https://www.python.org/downloads dan Python 3.10+ ni yuklab oling
echo   2) O'rnatishda "Add python.exe to PATH" katagini BELGILANG
echo   3) Kompyuterni qayta ishga tushiring va start.bat ni yana bosing
echo.
pause
exit /b

:VENVFAIL
echo [XATO] Virtual muhit yaratilmadi.
echo        Python to'liq o'rnatilganini tekshiring.
echo.
pause
exit /b

:PIPFAIL
echo [XATO] Kutubxonalarni o'rnatib bo'lmadi.
echo        Internet aloqasini tekshiring va qaytadan urinib ko'ring.
echo.
pause
exit /b
