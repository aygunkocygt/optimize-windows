@echo off
REM ========================================
REM Windows 11 Optimizer - All-in-One Build Script
REM Install kontrolü, build ve temizlik işlemleri
REM ========================================

setlocal enabledelayedexpansion

REM Script'in bulunduğu dizine geç
cd /d "%~dp0"

echo.
echo ========================================
echo   Windows 11 Optimizer - Build Script
echo ========================================
echo.
echo Calisma dizini: %CD%
echo.

REM Python kontrolü
echo [1/4] Python kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo    [X] Python bulunamadi!
    echo.
    echo    Lutfen Python 3.8+ yukleyin:
    echo    https://www.python.org/downloads/
    echo.
    echo    Kurulum sirasinda "Add Python to PATH" secenegini isaretleyin!
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo    [OK] Python bulundu: !PYTHON_VERSION!
echo.

REM Pip kontrolü ve paket yükleme
echo [2/4] Paketler kontrol ediliyor...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo    [X] pip bulunamadi! Yükleniyor...
    python -m ensurepip --upgrade
)

echo    [OK] pip hazir

REM requirements.txt kontrolü
if not exist "requirements.txt" (
    echo    [X] requirements.txt dosyasi bulunamadi!
    echo    Mevcut dizin: %CD%
    echo    Lutfen build.bat dosyasini proje klasorunde calistirin.
    pause
    exit /b 1
)

echo    Paketler yukleniyor...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo    [X] Paket yukleme basarisiz!
    echo    Manuel olarak deneyin: python -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo    [OK] Tum paketler yuklendi
echo.

REM PyInstaller kontrolü
echo [3/4] PyInstaller kontrol ediliyor...
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo    [X] PyInstaller bulunamadi! Yükleniyor...
    python -m pip install pyinstaller --quiet
)

echo    [OK] PyInstaller hazir
echo.

REM Build işlemi
echo [4/4] EXE dosyalari olusturuluyor...
echo.

REM optimize.py ve restore.py kontrolü
if not exist "optimize.py" (
    echo    [X] optimize.py dosyasi bulunamadi!
    echo    Mevcut dizin: %CD%
    pause
    exit /b 1
)

REM Eski build dosyalarını temizle
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec 2>nul

echo    [1/2] Windows11Optimizer.exe olusturuluyor...
python -m PyInstaller --onefile --console --name Windows11Optimizer --clean --noconfirm --add-data "modules;modules" optimize.py >nul 2>&1

if errorlevel 1 (
    echo    [X] Windows11Optimizer.exe olusturulamadi!
    echo    Hata detaylari icin: python -m PyInstaller --onefile --console --name Windows11Optimizer --add-data "modules;modules" optimize.py
    pause
    exit /b 1
)

echo    [OK] Windows11Optimizer.exe olusturuldu
echo.

if not exist "restore.py" (
    echo    [X] restore.py dosyasi bulunamadi! Atlaniyor...
) else (
    echo    [2/2] Windows11Restore.exe olusturuluyor...
    python -m PyInstaller --onefile --console --name Windows11Restore --clean --noconfirm restore.py >nul 2>&1
    
    if errorlevel 1 (
        echo    [X] Windows11Restore.exe olusturulamadi!
        echo    Hata detaylari icin: python -m PyInstaller --onefile --console --name Windows11Restore restore.py
    ) else (
        echo    [OK] Windows11Restore.exe olusturuldu
    )
    echo.
)

if errorlevel 1 (
    echo    [X] Windows11Restore.exe olusturulamadi!
    echo    Hata detaylari icin: python -m PyInstaller --onefile --console --name Windows11Restore restore.py
    pause
    exit /b 1
)

echo    [OK] Windows11Restore.exe olusturuldu
echo.

REM Geçici dosyaları temizle
if exist build rmdir /s /q build
if exist *.spec del /q *.spec 2>nul

REM Dosya boyutlarını göster
echo ========================================
echo   Build Tamamlandi!
echo ========================================
echo.
echo EXE dosyalari 'dist' klasorunde:
echo.

if exist "dist\Windows11Optimizer.exe" (
    for %%A in ("dist\Windows11Optimizer.exe") do (
        set /a SIZE=%%~zA/1024/1024
        echo    Windows11Optimizer.exe ^(!SIZE! MB^)
    )
)

if exist "dist\Windows11Restore.exe" (
    for %%A in ("dist\Windows11Restore.exe") do (
        set /a SIZE=%%~zA/1024/1024
        echo    Windows11Restore.exe ^(!SIZE! MB^)
    )
)

echo.
echo KULLANIM:
echo    1. dist\Windows11Optimizer.exe dosyasini yonetici olarak calistirin
echo    2. dist\Windows11Restore.exe ile degisiklikleri geri alabilirsiniz
echo.
echo NOT: EXE dosyalarini yonetici haklariyla calistirmaniz gerekir!
echo.
pause
