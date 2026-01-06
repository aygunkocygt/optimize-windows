@echo off
REM ========================================
REM Windows 11 Optimizer - Değişiklik Kontrolü
REM Yapılan optimizasyonların aktif olup olmadığını kontrol eder
REM ========================================

setlocal enabledelayedexpansion

REM Script'in bulunduğu dizine geç
cd /d "%~dp0" 2>nul

echo.
echo ========================================
echo   Windows 11 Optimizer - Kontrol
echo ========================================
echo.

REM Telemetri kontrolü
echo [1/5] Telemetri kontrol ediliyor...
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" /v AllowTelemetry >nul 2>&1
if errorlevel 1 (
    echo    [?] Telemetri ayari bulunamadi (muhtemelen kapatilmis)
) else (
    set TELEMETRY=
    for /f "tokens=3" %%i in ('reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" /v AllowTelemetry 2^>nul') do set TELEMETRY=%%i
    if "!TELEMETRY!"=="0x0" (
        echo    [OK] Telemetri KAPALI
    ) else if "!TELEMETRY!"=="" (
        echo    [?] Telemetri durumu okunamadi
    ) else (
        echo    [!] Telemetri ACIK: !TELEMETRY!
    )
)
echo.

REM Game Mode kontrolü
echo [2/5] Game Mode kontrol ediliyor...
reg query "HKCU\SOFTWARE\Microsoft\GameBar" /v AllowAutoGameMode >nul 2>&1
if errorlevel 1 (
    echo    [?] Game Mode ayari bulunamadi
) else (
    set GAMEMODE=
    for /f "tokens=3" %%i in ('reg query "HKCU\SOFTWARE\Microsoft\GameBar" /v AllowAutoGameMode 2^>nul') do set GAMEMODE=%%i
    if "!GAMEMODE!"=="0x1" (
        echo    [OK] Game Mode AKTIF
    ) else if "!GAMEMODE!"=="" (
        echo    [?] Game Mode durumu okunamadi
    ) else (
        echo    [!] Game Mode pasif: !GAMEMODE!
    )
)
echo.

REM GPU Scheduling kontrolü
echo [3/5] GPU Scheduling kontrol ediliyor...
reg query "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v HwSchMode >nul 2>&1
if errorlevel 1 (
    echo    [?] GPU Scheduling ayari bulunamadi
) else (
    set GPUSCH=
    for /f "tokens=3" %%i in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v HwSchMode 2^>nul') do set GPUSCH=%%i
    if "!GPUSCH!"=="0x2" (
        echo    [OK] GPU Scheduling AKTIF
    ) else if "!GPUSCH!"=="" (
        echo    [?] GPU Scheduling durumu okunamadi
    ) else (
        echo    [!] GPU Scheduling pasif: !GPUSCH!
    )
)
echo.

REM Servis kontrolü (DiagTrack - Telemetri servisi)
echo [4/5] Telemetri servisi kontrol ediliyor...
sc query DiagTrack >nul 2>&1
if errorlevel 1 (
    echo    [OK] DiagTrack servisi bulunamadi (muhtemelen kapatilmis)
) else (
    sc query DiagTrack 2>nul | findstr /I /C:"STOPPED" >nul
    if not errorlevel 1 (
        echo    [OK] DiagTrack servisi DURDURULMUS
    ) else (
        sc query DiagTrack 2>nul | findstr /I /C:"RUNNING" >nul
        if not errorlevel 1 (
            echo    [!] DiagTrack servisi CALISIYOR
            echo    NOT: Windows restart sonrasi bu servis otomatik baslatilmis olabilir.
            echo    Servisi durdurmak icin optimize.exe dosyasini tekrar calistirin.
        ) else (
            echo    [?] DiagTrack servisi durumu belirlenemedi
        )
    )
)
echo.

REM Güç planı kontrolü
echo [5/5] Güç plani kontrol ediliyor...
set POWER_SCHEME=
for /f "tokens=*" %%i in ('powercfg /getactivescheme 2^>nul') do set POWER_SCHEME=%%i
if "!POWER_SCHEME!"=="" (
    echo    [?] Güç plani okunamadi
) else (
    echo !POWER_SCHEME! | findstr /i "high performance" >nul
    if errorlevel 1 (
        echo    [!] High Performance plani aktif degil
        echo    Mevcut plan: !POWER_SCHEME!
    ) else (
        echo    [OK] High Performance plani AKTIF
    )
)
echo.

REM Özet
echo ========================================
echo   Kontrol Tamamlandi
echo ========================================
echo.
echo NOT: Eger [!] isaretli maddeler varsa, Windows Update
echo bazı ayarlari geri almış olabilir. Bu durumda optimize.exe
echo dosyasini tekrar calistirabilirsiniz.
echo.
echo.
echo Devam etmek icin bir tusa basin...
pause
exit /b 0
