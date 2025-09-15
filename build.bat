@echo off
pip install -r requirements.txt
python -m PyInstaller --onefile --noconsole --icon=icon.ico --clean --strip main.py
exit