@echo off

IF "%2"=="" (
    echo Using existing tag
) ELSE (
    echo tagging with %2
    git tag %2
    IF %ERRORLEVEL% NEQ 0 (
        echo Failed creating Tag
        echo %ERRORLEVEL%
        GOTO FAIL
    )
)

echo copying scipy hook modifier
copy "src\main\python\hook-scipy.py" "venv\Lib\site-packages\PyInstaller\hooks\hook-scipy.py"
IF %ERRORLEVEL% NEQ 0 (
    echo "copy task failed"
    echo %ERRORLEVEL%
    GOTO FAIL
)

echo cleaning build directory
fbs clean
IF %ERRORLEVEL% NEQ 0 (
    echo fbs failed
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

echo creating installer
fbs installer
IF %ERRORLEVEL% NEQ 0 (
    echo fbs failed
    echo %ERRORLEVEL%
    GOTO FAIL
)

echo cleaning up old archives
del ".\target\UNote_windows.zip"

echo zipping application
zip ".\target\UNote_windows.zip" -r ".\target\UNote"
IF %ERRORLEVEL% NEQ 0 (
    echo Failed Zipping application
    echo %ERRORLEVEL%
    GOTO FAIL
)

echo copying application to server
copy ".\target\UNoteSetup.exe" "X:\website-stroblme\server\unote\htdocs\archives\windows\UNoteSetup.exe"
IF %ERRORLEVEL% NEQ 0 (
    echo Copying to server failed
    echo %ERRORLEVEL%
    GOTO FAIL
)

GOTO PASS

:FAIL
echo !!!!!!!! Building UNote Failed !!!!!!!!

:PASS
echo Pass