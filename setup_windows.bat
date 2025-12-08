@echo off
set VENV_DIR=venv

echo Activating venv...
call %VENV_DIR%\Scripts\activate

echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

echo Installing requirements...
pip install -r requirements.txt

echo Setup complete.
pause
