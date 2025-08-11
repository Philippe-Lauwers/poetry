@echo off
REM — Base folder where this script lives
set "BASEDIR=%~dp0"

REM Ensure Poetry creates in-project venvs from now on
poetry config virtualenvs.in-project true

REM — Hard-code your ports here (or read them from .env into these vars)
set "BACKEND_PORT=5050"
set "INTERFACE_PORT=5000"

REM — Start Backend Server
start "Backend Server" cmd /k ^
    cd /d %BASEDIR%WritingAssistantBackend ^&^& ^
    poetry install --no-root ^&^& ^
    set FLASK_APP=manage:app ^&^& ^
    set FLASK_ENV=development ^&^& ^
    set FLASK_RUN_PORT=%BACKEND_PORT% ^&^& ^
    poetry run flask run

REM — Start Frontend Server
start "Frontend Server" cmd /k ^
    cd /d %BASEDIR%WritingAssistantInterface ^&^& ^
    poetry install --no-root ^&^& ^
    set FLASK_APP=app ^&^& ^
    set FLASK_ENV=development ^&^& ^
    set INTERFACE_PORT=%INTERFACE_PORT% ^&^& ^
    poetry run python app.py

exit /b
