IF "$2"=="" (
    echo Using existing tag
) ELSE (
    echo tagging with $2
    git tag $2
    IF $? != 0 (
        echo Failed creating Tag
        echo $?$
    )
)

echo copying scipy hook modifier
copy "src\main\python\hook-scipy.py" "venv\Lib\site-packages\PyInstaller\hooks\hook-scipy.py"
IF $? != 0 (
    echo "copy task failed"
    echo $?
)

echo cleaning build directory
fbs clean
IF $? != 0 (
    echo fbs failed
    echo $?
)

echo freezing application
fbs freeze
IF $? != 0 (
    echo fbs failed
    echo $?
)

echo creating installer
fbs installer
IF $? != 0 (
    echo fbs failed
    echo $?
)

echo cleaning up old archives
del ".\target\UNote_linux.zip"

echo zipping application
zip ".\target\UNote_linux.zip" -r ".\target\UNote"
IF $? != 0 (
    echo Failed Zipping application
    echo $?
)

echo copying application to server
copy ".\target\UNoteSetup.exe" "X:\website-stroblme\server\unote\htdocs\archives\linux\UNoteSetup.exe"
IF $? != 0 (
    echo Copying to server failed
    echo $?
)

echo Passed