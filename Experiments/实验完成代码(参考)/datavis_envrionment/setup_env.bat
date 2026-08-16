@echo off
echo =================================
echo datavisualization environment setup
echo =================================

echo creating virtual environment...
py -3.10 -m pip install virtualenv
py -3.10 -m virtualenv venv
echo activating environment...
call venv\Scripts\activate
echo installing libraries...
pip install -r requirements.txt
echo testing environment...
python test_env.py

echo =================================
echo setup finished
echo =================================

pause
