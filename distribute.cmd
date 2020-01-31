@echo off

echo tagging with %2
git tag %2
IF %ERRORLEVEL% NEQ 0 (
    echo Failed creating Tag
    echo %ERRORLEVEL%
    GOTO FAIL
)

echo freezing application
fbs freeze
IF %ERRORLEVEL% NEQ 0 (
    echo fbs failed
    echo %ERRORLEVEL%
    GOTO FAIL
)

echo zipping application
7z a ".\target\UNote.zip" ".\target\UNote\"
IF %ERRORLEVEL% NEQ 0 (
    echo Failed Zipping application
    echo %ERRORLEVEL%
    GOTO FAIL
)

REM echo copying application to server
REM copy ".\target\UNote.zip" "%1"
REM IF %ERRORLEVEL% NEQ 0 (
REM     echo Copying to server failed
REM     echo %ERRORLEVEL%
REM     GOTO FAIL
REM )

REM echo removing local zip
REM rd /s /q ".\target\UNote.zip"
REM IF %ERRORLEVEL% NEQ 0 (
REM     echo Failed deleting local zip
REM     echo %ERRORLEVEL%
REM     GOTO FAIL
REM )

GOTO PASS

:FAIL
echo !!!!!!!! Building RegCon Failed !!!!!!!!

:PASS
echo Pass