@echo off
REM Build script for WE-DAVIS that ensures offline compatibility
REM This script builds the executable with all necessary resources bundled

echo ======================================
echo Building WE-DAVIS for Offline Use
echo ======================================
echo.

echo Step 1: Cleaning previous build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Done.
echo.

echo Step 2: Building executable with PyInstaller...
echo This includes Plotly JavaScript files for offline operation.
pyinstaller WE-DAVIS.spec --clean --noconfirm
echo.

if %errorlevel% neq 0 (
    echo ERROR: Build failed!
    pause
    exit /b %errorlevel%
)

echo ======================================
echo Build completed successfully!
echo ======================================
echo.
echo The executable is located at: dist\WE-DAVIS\WE-DAVIS.exe
echo.
echo You can now transfer the entire dist\WE-DAVIS folder to your offline environment.
echo.
pause

