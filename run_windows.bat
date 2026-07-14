@echo off
echo Starting Smile Detection Project...
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
python app.py
pause
