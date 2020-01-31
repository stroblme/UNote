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
7z a ".\target\out.zip" ".\target\UNote\"
IF %ERRORLEVEL% NEQ 0 (
    echo Failed Zipping application
    echo %ERRORLEVEL%
    GOTO FAIL
)

echo copying application to server
copy ".\target\out.zip" "%1"
IF %ERRORLEVEL% NEQ 0 (
    echo Copying to server failed
    echo %ERRORLEVEL%
    GOTO FAIL
)

echo removing local zip
rd /s /q ".\target\out.zip"
IF %ERRORLEVEL% NEQ 0 (
    echo Failed deleting local zip
    echo %ERRORLEVEL%
    GOTO FAIL
)

GOTO PASS

:FAIL
echo !!!!!!!! Building RegCon Failed !!!!!!!!

:PASS
echo Pass