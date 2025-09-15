@echo off
python -m PyInstaller --onefile --noconsole --icon=icon.ico --clean --strip main.py
exit
