@echo off
SET PIP_FILE_URL=pip-installs-urls.txt
SET LOG_DIR=logs
SET LOG_FILE=%LOG_DIR%\%~n0.log

IF NOT EXIST %LOG_DIR% MKDIR %LOG_DIR%
IF EXIST %LOG_FILE% DEL %LOG_FILE%

SET YAML_FILE_DFLT="environment.yml"
SET PIP_FILE_DFLT="pip-installs.txt"
REM Ask the user for the yml file
SET "YAML_FILE="
SET /P YAML_FILE=Enter name of YAML file to create the environment from (default is %YAML_FILE_DFLT%):
IF "%YAML_FILE%"=="" SET YAML_FILE=environment.yml
REM Ask the user for the file that contains the pip installs
SET "PIP_FILE="
SET /P PIP_FILE=Enter name of file with pip installs (default is %PIP_FILE_DFLT%):
IF "%PIP_FILE%"=="" SET PIP_FILE=pip-installs.txt

REM Extract 'name' field from YAML using PowerShell (split across lines for clarity)
FOR /F "usebackq delims=" %%A IN (`powershell -NoProfile -Command "(Get-Content %YAML_FILE% | Where-Object { $_ -match '^\s*name\s*:\s*' }) -replace '^\s*name\s*:\s*',''"`) DO SET ENV_NAME=%%A
CALL :LogMessage "Creating environment '%ENV_NAME%' from '%YAML_FILE%'"

REM Check if environment exists
CALL conda env list | findstr /R /C:"^%ENV_NAME%[ ]" > nul
IF %ERRORLEVEL% NEQ 0 (
    echo.
    CALL :LogMessage "No previous version of the environment '%ENV_NAME%' exists, a NEW environment will be created."
) ELSE (
    echo.
    CALL :LogMessage "The environment '%ENV_NAME%' already exists."
    CHOICE /M "Are you sure you want to replace the existing environment?"
    IF ERRORLEVEL 2 (
        CALL :LogonlyMessage "The user has chosen NOT to replace the current environment."
        CALL :LogMessage "Nothing will be changed."
        pause
        REM If the user chose to change nothing we can exit
        exit /b
    ) ELSE (
        CALL :LogonlyMessage "The user has chosen to replace the current environment."
    )
    REM When we arrive here, we know an environment %ENV_NAME% exists and it will be removed
    REM The first step is to delete the old environment
    echo.
    CALL :LogEmptyLines
    CALL :LogMessage "Removing existing environment '%ENV_NAME%'..."
    CALL conda env remove -n %ENV_NAME% -y >> %LOG_FILE%
    CALL :LogMessage "The existing environment '%ENV_NAME%' has been removed."
)

REM Create the environment from the yml file
echo.
CALL :LogEmptyLines
CALL :LogMessage "Creating environment '%ENV_NAME%' from %YAML_FILE% ..."
CALL conda env create --file %YAML_FILE% >> %LOG_FILE%
IF %ERRORLEVEL% NEQ 0 (
    CALL :LogMessage "Failed to create environment '%ENV_NAME%' from %YAML_FILE% ."
    echo Please check %LOG_FILE% for details.
    pause
    exit /b
)

CALL :LogMessage "Environment '%ENV_NAME%' was created."
CALL conda list -n %ENV_NAME% >> %LOG_FILE%


REM Installing packages from %PIP_FILE% (which contains a list of pip packages)
echo.
CALL :LogEmptyLines
CALL :LogMessage "Installing packages in '%ENV_NAME%' with pip ..."
REM if additional index urls are defined, store them in variables
IF EXIST %PIP_FILE_URL% (
    CALL :LogMessage "  Loading additional index urls from %PIP_FILE_URL%"
    FOR /F "usebackq tokens=*" %%L IN ("%PIP_FILE_URL%") DO (
        CALL :PipExtractAdditionalURL "%%L"
    )
    CALL :LogMessage "  Finished loading additional index urls from %PIP_FILE_URL%"
)
REM Loop through each line of pip-installs.txt so we can check for each install whether an extra index url is needed
FOR /F "usebackq tokens=*" %%L IN ("%PIP_FILE%") DO (
    CALL :PipInstallPackage "%%L"
)

echo.
CALL :LogEmptyLines
CALL :LogMessage "Finished installing packages in '%ENV_NAME%' with pip"
CALL conda run -n %ENV_NAME% pip list >> %LOG_FILE%

CALL :LogEmptyLines
CALL :LogMessage "Finished creating environment '%ENV_NAME%' ."
ECHO If any errors occured, please consult %LOG_FILE% for details.

GOTO :EOF

:PipInstallPackage
    REM Install the package with pip
    SETLOCAL ENABLEDELAYEDEXPANSION
    SET "PKG=%~1"
    CALL :LogMessage "  Installing !PKG!..."
    REM Installing the package ...
    CALL conda run -n %ENV_NAME% pip install !PKG! >> %LOG_FILE% 2>&1
    REM If an error occurs, check if an additional index url is available and retry
    IF !ERRORLEVEL! NEQ 0 (
        CALL :LogMessage "    Install of !PKG! failed."
        REM Retry package with extra index
        CALL :CleanPackageName "!PKG!" PACKAGE_CLEAN_NAME
        REM Get the value of the dynamic variable name URL_...
        SET "VAR_NAME=URL_!PACKAGE_CLEAN_NAME!"
        FOR /F "tokens=* delims=" %%I IN (
            'CALL echo %%!VAR_NAME!%%'
        ) DO (
            SET "ADDITIONAL_INDEX_URL=%%I"
        )
        CALL :LogMessage "    Retrying pip install of !PKG! with additional index URL !ADDITIONAL_INDEX_URL!."
        CALL conda run -n %ENV_NAME% pip install !PKG! --extra-index-url !ADDITIONAL_INDEX_URL! >> %LOG_FILE% 2>&1
        IF !ERRORLEVEL! NEQ 0 (
            CALL :LogMessage "    Pip install of package !PKG! with additional index URL (!ADDITIONAL_INDEX_URL!) has failed."
            echo Please check %LOG_FILE% for details.
            echo. >> %LOG_FILE%
        ) ELSE (
            CALL :LogMessage "  !PKG! was installed successfully from !ADDITIONAL_INDEX_URL!."
        )
    ) ELSE (
        CALL :LogonlyMessage "    Installed !PKG!."
    )
    GOTO :EOF

:PipExtractAdditionalURL
    REM If a package requires an additional index url, it can be found in a separate textfile
    REM We store the URL's in their own variable
    SETLOCAL EnableDelayedExpansion
    SET "LINE=%~1"

    set "LEN=0"
    set "POS=-1"

    REM Find position of last '=='
    :SEARCH
    set /a NEXT=LEN+1
    set "CHR1=!LINE:~%LEN%,1!"
    set "CHR2=!LINE:~%NEXT%,1!"
    REM Search as long as there is a 'next' character (i.e. a second of the two we want to check)
    if defined CHR2 (
        if "!CHR1!!CHR2!"=="==" (
            REM if CHR1 and CHR2 are both = then adapt the position
            set "POS=%LEN%"
        )
        set /a LEN+=1
        goto :SEARCH
    )
    REM for lines without ==
    if "!POS!"=="-1" (
        REM No '==' found in line.
        ENDLOCAL
        GOTO :EOF
    )
    REM The part of the input string before == ends at this position
    set /a BEFORE_LEN=POS
    REM The part of the input string after == starts at this position
    set /a AFTER_START=POS+2

    REM Split the input file
    CALL SET "PACKAGE=!LINE:~0,%BEFORE_LEN%!"
    CALL SET "URL=!LINE:~%AFTER_START%!"
    CALL :CleanPackageName "!PACKAGE!" PACKAGE_CLEAN_NAME
    SET "TMP_NAME=!PACKAGE_CLEAN_NAME!"
    SET "TMP_URL=!URL!"
    CALL :LogonlyMessage "   - Package '!TMP_NAME!' has additional index url '!TMP_URL!'"
    ENDLOCAL & CALL SET "URL_%TMP_NAME%=%TMP_URL%"
    GOTO :EOF

:CleanPackageName
    REM Replaces all non alphanumeric characters with '_'
    SETLOCAL EnableDelayedExpansion
    SET "INPUT=%~1"
    SET "SAFE_NAME="

    FOR /L %%I IN (0,1,1023) DO (
        SET "CHR=!INPUT:~%%I,1!"
        IF "!CHR!"=="" GOTO DONE

        REM Use character class check manually
        SET "CHAR=!CHR!"
        FOR %%A IN (
            A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
            a b c d e f g h i j k l m n o p q r s t u v w x y z
            0 1 2 3 4 5 6 7 8 9 _
        ) DO (
            IF "!CHAR!"=="%%A" (
                SET "SAFE_NAME=!SAFE_NAME!!CHAR!"
                SET "FOUND=1"
            )
        )
        IF NOT DEFINED FOUND (
            SET "SAFE_NAME=!SAFE_NAME!_"
        )
        SET "FOUND="
    )
:DONE
    ENDLOCAL & SET "%~2=%SAFE_NAME%"
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