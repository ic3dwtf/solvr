@echo off
pip install -r requirements.txt
python -m PyInstaller --onefile --noconsole --icon=icon.ico --clean --strip main.py --add-data "icon.ico;." --add-data "version.txt;." --add-data "images;images"
exit