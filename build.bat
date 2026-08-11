@echo off
REM ---------------------------------------------------------------------------
REM Build the Marvel Powers United VR Level Select Tool into a single .exe.
REM Run this on Windows with Python 3.10+ installed.
REM ---------------------------------------------------------------------------

echo Installing dependencies...
python -m pip install -r requirements.txt pyinstaller || goto :error

REM Prefer your own MPUVR.ico in the repo root; fall back to the generated one.
set ICON=assets\mpuvr.ico
if exist MPUVR.ico set ICON=MPUVR.ico

echo Building executable with icon %ICON% ...
python -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "MPUVR Level Select Tool" ^
    --icon "%ICON%" ^
    --collect-all customtkinter ^
    --add-data "assets;assets" ^
    run.py || goto :error

echo.
echo Done. The executable is in the "dist" folder.
echo IMPORTANT: place the built .exe next to the game's "WindowsNoEditor"
echo and "InjectUUU" folders (same layout as the original tool).
goto :eof

:error
echo.
echo Build failed. See the output above.
exit /b 1
