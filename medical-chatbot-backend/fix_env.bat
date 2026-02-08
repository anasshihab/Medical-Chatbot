@echo off
echo Cleaning up greenlet...
pip uninstall -y greenlet
echo.
echo Reinstalling greenlet and dependencies...
pip install greenlet --no-cache-dir --force-reinstall
pip install -r requirements.txt
echo.
echo Fix complete. Please try running the server again.
pause
