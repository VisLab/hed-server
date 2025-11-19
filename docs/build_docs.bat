@echo off
REM Build HED Web Tools documentation with Sphinx
REM This script should be run from the docs directory

echo Building HED Web Tools documentation with Sphinx...

REM Check if we're in the docs directory
if not exist "conf.py" (
    echo Error: conf.py not found. Please run this script from the docs directory.
    echo Alternatively, use the build_docs.py script from the project root.
    pause
    exit /b 1
)

REM Install requirements
echo Installing documentation requirements...
pip install -r requirements.txt

REM Build the documentation
echo Building documentation...
sphinx-build -b html . _build/html

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Documentation built successfully!
    echo Open _build/html/index.html in your browser to view the documentation.
) else (
    echo.
    echo Error building documentation!
)

pause

