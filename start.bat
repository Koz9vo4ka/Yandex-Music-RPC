@echo off

cd source

if exist *config.ini* (
  py yandex_presence.py
) else (
  cd ../
  get_yandex_token.bat
)

pause
