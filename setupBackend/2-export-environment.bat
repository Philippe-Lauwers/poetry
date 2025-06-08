@echo off
REM We will extract the default environment name from the original yml file
REM but prompt the user to ask for the environment name later
SET YAML_FILE_IN=environment-top-level.yml
SET LOG_DIR=logs
SET LOG_FILE=%LOG_DIR%\%~n0.log

IF NOT EXIST %LOG_DIR% MKDIR %LOG_DIR%
IF EXIST %LOG_FILE% DEL %LOG_FILE%

SET "ENV_NAME_DFLT="
SET "ENV_NAME="
REM Ask the user which environment to export
:ASK_DFLT_ENV
  SET /P ENV_NAME_DFLT=Enter name of the environment you want to export:
  IF "%ENV_NAME_DFLT%"=="" GOTO :ASK_DFLT_ENV
  REM check if %ENV_NAME_DFLT% exists; if not, offer to quit or re-prompt
  CALL conda env list | findstr /R /C:"^%ENV_NAME_DFLT%[ ]" > nul
  IF %ERRORLEVEL% NEQ 0 (
    CALL :LogMessage "The environment '%ENV_NAME_DFLT%' does not exist."
    CHOICE /M "Environment '%ENV_NAME_DFLT%' not found. Do you want to quit?"
    IF ERRORLEVEL 2 GOTO :ASK_DFLT_ENV
    REM ELSE
    CALL :LogonlyMessage "The user entered an invalid name ('%ENV_NAME_DFLT%') and chose not to continue."
    GOTO :EOF
  )
REM Ask the user for the value of the name-field in the YAML-file
SET /P ENV_NAME=Enter name of the new environment (default is %ENV_NAME_DFLT%):
IF "%ENV_NAME%"=="" SET ENV_NAME=%ENV_NAME_DFLT%

REM Ask the user which yml file to export to
SET "YAML_FILE_OUT="
SET /P YAML_FILE_OUT=Enter name of YAML export file (default is %ENV_NAME%.yml):
IF "%YAML_FILE_OUT%"=="" SET YAML_FILE_OUT=%ENV_NAME%.yml
IF EXIST %YAML_FILE_OUT% DEL %YAML_FILE_OUT%
REM Ask the user which pip export file to export to
SET "PIP_FILE="
SET /P PIP_FILE=Enter name of pip export file (default is %ENV_NAME%-pip.txt):
IF "%PIP_FILE%"=="" SET PIP_FILE=%ENV_NAME%-pip.txt
SET PIP_FILE_tmp=pip-installs_tmp.txt
IF EXIST %PIP_FILE% DEL %PIP_FILE%

CALL :LogMessage "Exporting %YAML_FILE_OUT% and %PIP_FILE% from '%ENV_NAME_DFLT%' to create environment '%ENV_NAME%'"
CALL :LogEmptyLines

CALL :LogMessage "Exporting %YAML_FILE_OUT% ..."
SET "TMP_FILE=%~dp0YAML_FILE_OUT_tmp.yml"
IF EXIST "%YAML_FILE_OUT%" DEL "%YAML_FILE_OUT%"
IF EXIST "%TMP_FILE%" DEL "%TMP_FILE%"
CALL cmd /c "conda env export -n %ENV_NAME_DFLT% --no-builds > %YAML_FILE_OUT%"
IF %ERRORLEVEL% NEQ 0 (
    CALL :LogMessage " - %YAML_FILE_OUT% was not created successfully."
    GOTO :PIP_INSTALLS
)
CALL :LogMessage " - %YAML_FILE_OUT% was created successfully."
REM If the user wants to export the file to create another environment, replace name: OLD with name: NEW
IF /I NOT "%ENV_NAME%"=="%ENV_NAME_DFLT%" (
    CALL :LogMessage "Replacing '%ENV_NAME_DFLT%' with '%ENV_NAME%' in %YAML_FILE_OUT%"
    CALL :YMLReplaceEnvName "%YAML_FILE_OUT%" "%ENV_NAME%" "%ENV_NAME_DFLT%"
)
IF %ERRORLEVEL% EQU 0 (
    CALL :LogMessage " - 'name: %ENV_NAME_DFLT%' successfully replaced with 'name: %ENV_NAME%' in %YAML_FILE_OUT%"
) ELSE (
    CALL :LogMessage " - 'name: %ENV_NAME_DFLT%' was not replaced with 'name: %ENV_NAME%' in %YAML_FILE_OUT%"
)
echo.
CALL :LogEmptyLines

REM Remove pip section to create environment.yml
CALL :LogMessage "Removing pip installs from %YAML_FILE_OUT%"
REM Remove pip installs from %YAML_FILE_OUT%
powershell -NoProfile -Command ^
    "$inBlock = $false; Get-Content '%YAML_FILE_OUT%' | ForEach-Object { if ($_ -match '^\s*- pip:\s*$') { $inBlock = $true } elseif ($inBlock -and ($_ -match '^\s+-')) { return } else { $inBlock = $false; $_ } } | Set-Content '%TMP_FILE%'"
IF %ERRORLEVEL% EQU 0 (
    REM %TMP_FILE% will be the correct version, remove %YAML_FILE_OUT% and rename %TMP_FILE% to %YAML_FILE_OUT%
    DEL "%YAML_FILE_OUT%"
    REN "%TMP_FILE%" "%YAML_FILE_OUT%"
    CALL :LogMessage " - pip installs were successfully removed from %YAML_FILE_OUT%."
) ELSE (
    REM If removing the pip section did not succeed, we prompt/log an error message and keep %YAML_FILE_OUT%
    REM (which will most likely still contain pip installs)
    IF EXIST "%TMP_FILE%" DEL "%TMP_FILE%"
    CALL :LogMessage " - pip installs were not successfully removed from %YAML_FILE_OUT%."
)
echo.
CALL :LogEmptyLines

REM Remove prefix line from %YAML_FILE_OUT%
CALL :LogMessage "Removing prefix from %YAML_FILE_OUT%"
SET "TMP_FILE_PREFIX=%~dp0%YAML_FILE_OUT%_noprefix.yml"
powershell -NoProfile -Command ^
  "Get-Content '%YAML_FILE_OUT%' | Where-Object { -not ($_ -match '^prefix:') } | Set-Content '%TMP_FILE_PREFIX%'"
IF %ERRORLEVEL% EQU 0 (
  DEL "%YAML_FILE_OUT%"
  REN "%TMP_FILE_PREFIX%" "%YAML_FILE_OUT%"
  CALL :LogMessage " - prefix removed successfully from %YAML_FILE_OUT%."
) ELSE (
  IF EXIST "%TMP_FILE_PREFIX%" DEL "%TMP_FILE_PREFIX%"
  CALL :LogMessage " - failed to remove prefix from %YAML_FILE_OUT%."
)
echo.
CALL :LogEmptyLines


:PIP_INSTALLS
echo.
CALL :LogEmptyLines
CALL :LogMessage "Exporting %PIP_FILE% ..."
IF EXIST %PIP_FILE_tmp% DEL %PIP_FILE_tmp%
IF EXIST %PIP_FILE% DEL %PIP_FILE%
REM Save the pip-installs of the existing environment into a temp file
CALL conda run -n %ENV_NAME_DFLT% pip freeze > %PIP_FILE_tmp%
IF %ERRORLEVEL% EQU 0 (
    CALL :LogMessage " - %PIP_FILE% was created successfully."
) ELSE (
    IF EXIST %PIP_FILE_tmp% DEL %PIP_FILE_tmp%
    CALL :LogMessage " - %PIP_FILE% was not created successfully."
    GOTO :EOF
)
REM Cleaning up %PIP_FILE_tmp%
SETLOCAL EnableDelayedExpansion
FOR /F "usebackq delims=" %%L IN (`type "%PIP_FILE_tmp%"`) DO (
    CALL :CleanPipName "%%L" CLEANED_LINE
    IF NOT "!CLEANED_LINE!"=="" (
        >> %PIP_FILE% echo(!CLEANED_LINE!
    ) ELSE (
        CALL :LogMessage "Line omitted from %PIP_FILE%: %%L"
    )
)
ENDLOCAL
IF %ERRORLEVEL% EQU 0 (
    CALL :LogMessage " - %PIP_FILE% was successfully cleaned."
) ELSE (
    DEL %PIP_FILE%
    REN %PIP_FILE_tmp% %PIP_FILE%
    CALL :LogMessage " - %PIP_FILE% was not successfully cleaned. Please check the contents of %PIP_FILE%"
    GOTO :EOF
)
IF EXIST %PIP_FILE_tmp% DEL %PIP_FILE_tmp%

echo.
CALL :LogEmptyLines
CALL :LogMessage "Finished exporting environment '%ENV_NAME_DFLT%', creating:"
CALL :LogMessage "  - %YAML_FILE_OUT%"
CALL :LogMessage "  - %PIP_FILE%"
CALL :LogMessage "to create %ENV_NAME."
ECHO If any errors occured, please consult %LOG_FILE% for details.


GOTO :EOF

:YMLReplaceEnvName
    REM In the specified %YML_FILE% "name: %OLD_NAME%" will be replaced with "name: NEW_NAME"
    SETLOCAL
    SET "YML_FILE=%~1"
    SET "NEW_NAME=%~2"
    SET "OLD_NAME=%~3"
    powershell -Command "(Get-Content '%YML_FILE%') -replace '^name:\s*%OLD_NAME%', 'name: %NEW_NAME%' | Set-Content '%YML_FILE%'"
    ENDLOCAL
    GOTO :EOF

:CleanPipName
    REM Usage: CALL :CleanPipName "raw line" returnVarName
    REM Example: CALL :CleanPipName "typing_extensions @ file:///some/path" CLEANED_LINE
    SETLOCAL ENABLEDELAYEDEXPANSION
    SET "INPUT=%~1"
    SET "RESULT="
    REM Strip anything after '@'
    FOR /F "delims=@ tokens=1*" %%A IN ("!INPUT!") DO SET "RESULT=%%A"
    REM Trim both leading and trailing whitespace (using PowerShell for safety)
    FOR /F "delims=" %%T IN ('powershell -NoProfile -Command "('%RESULT%' -replace '^\s+|\s+$','')"') DO SET "RESULT=%%T"
    ENDLOCAL & SET "%~2=%RESULT%"
    GOTO :EOF

:LogMessage
    CALL :LogonlyMessage %*
    SETLOCAL
    SET MSG=%~1
    echo %MSG%
    ENDLOCAL
    GOTO :EOF
:LogonlyMessage
    SETLOCAL
    SET MSG=%~1
    echo [%DATE% %TIME%] %MSG% >> %LOG_FILE%
    ENDLOCAL
    GOTO :EOF

:LogEmptyLines
    echo. >> %LOG_FILE%
    echo ------------------------------------------------------------------------------------------------- >> %LOG_FILE%
    echo. >> %LOG_FILE%
    GOTO :EOF