@echo off
REM — Base folder where this script lives
set "BASEDIR=%~dp0"

REM before starting backand server:
REM poetry env use "[full path to]\python310\python.exe"
REM >poetry add https://download.pytorch.org/whl/cu118/torch-2.6.0%2Bcu118-cp310-cp310-win_amd64.whl
REM poetry install --no-root
REM --------------------------------------------------------------------------------------------------
REM — Start Backend in its own window, working dir set to WritingAssistantBackend
start "Backend Server" /D "%BASEDIR%WritingAssistantBackend" cmd /k ^
   "poetry install --no-root && poetry run python app.py"

REM — Start Frontend in its own window, working dir set to WritingAssistantInterface
start "Frontend Server" /D "%BASEDIR%WritingAssistantInterface" cmd /k ^
    "poetry install --no-root && poetry run python app.py"

exit /b
