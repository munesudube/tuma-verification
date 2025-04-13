@echo off
call env\Scripts\activate
waitress-serve --host 0.0.0.0 --port 5000 --threads 2 app:app
pause