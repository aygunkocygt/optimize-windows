@echo off
REM ========================================
REM Windows 11 Optimizer - Değişiklik Kontrolü
REM Yapılan optimizasyonların aktif olup olmadığını kontrol eder
REM ========================================

setlocal enabledelayedexpansion

REM Script'in bulunduğu dizine geç
cd /d "%~dp0" 2>nul

set "FAILED_COUNT=0"
set "TOTAL_COUNT=0"
set "FAILED_LIST="
set "REPORT_FILE=optimizasyon_raporu.txt"

echo.
echo ========================================
echo   Windows 11 Optimizer - Kontrol
echo ========================================
echo.

REM ========================================
REM 1. TELEMETRİ KONTROLLERİ
REM ========================================
echo [1/10] Telemetri kontrol ediliyor...
set /a TOTAL_COUNT+=1
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
        set /a FAILED_COUNT+=1
        set "FAILED_LIST=!FAILED_LIST!Telemetri (okunamadi)"
    ) else (
        echo    [!] Telemetri ACIK: !TELEMETRY!
        set /a FAILED_COUNT+=1
        set "FAILED_LIST=!FAILED_LIST!Telemetri (AciK: !TELEMETRY!)"
    )
)
echo.

REM ========================================
REM 2. GAME MODE
REM ========================================
echo [2/10] Game Mode kontrol ediliyor...
set /a TOTAL_COUNT+=1
reg query "HKCU\SOFTWARE\Microsoft\GameBar" /v AllowAutoGameMode >nul 2>&1
if errorlevel 1 (
    echo    [?] Game Mode ayari bulunamadi
    set /a FAILED_COUNT+=1
        set "FAILED_LIST=!FAILED_LIST! Game Mode (ayar bulunamadi)"
) else (
    set GAMEMODE=
    for /f "tokens=3" %%i in ('reg query "HKCU\SOFTWARE\Microsoft\GameBar" /v AllowAutoGameMode 2^>nul') do set GAMEMODE=%%i
    if "!GAMEMODE!"=="0x1" (
        echo    [OK] Game Mode AKTIF
    ) else if "!GAMEMODE!"=="" (
        echo    [?] Game Mode durumu okunamadi
        set /a FAILED_COUNT+=1
        set "FAILED_LIST=!FAILED_LIST! Game Mode (okunamadi)"
    ) else (
        echo    [!] Game Mode pasif: !GAMEMODE!
        set /a FAILED_COUNT+=1
        set "FAILED_LIST=!FAILED_LIST! Game Mode (pasif: !GAMEMODE!)"
    )
)
echo.

REM ========================================
REM 3. GPU SCHEDULING
REM ========================================
echo [3/10] GPU Scheduling kontrol ediliyor...
set /a TOTAL_COUNT+=1
reg query "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v HwSchMode >nul 2>&1
if errorlevel 1 (
    echo    [?] GPU Scheduling ayari bulunamadi
    set /a FAILED_COUNT+=1
    set "FAILED_LIST=!FAILED_LIST! GPU Scheduling (ayar bulunamadi)"
) else (
    set GPUSCH=
    for /f "tokens=3" %%i in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v HwSchMode 2^>nul') do set GPUSCH=%%i
    if "!GPUSCH!"=="0x2" (
        echo    [OK] GPU Scheduling AKTIF
    ) else if "!GPUSCH!"=="" (
        echo    [?] GPU Scheduling durumu okunamadi
        set /a FAILED_COUNT+=1
        set "FAILED_LIST=!FAILED_LIST! GPU Scheduling (okunamadi)"
    ) else (
        echo    [!] GPU Scheduling pasif: !GPUSCH!
        set /a FAILED_COUNT+=1
        set "FAILED_LIST=!FAILED_LIST! GPU Scheduling (pasif: !GPUSCH!)"
    )
)
echo.

REM ========================================
REM 4. TELEMETRİ SERVİSİ
REM ========================================
echo [4/10] Telemetri servisi kontrol ediliyor...
set /a TOTAL_COUNT+=1
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
            set /a FAILED_COUNT+=1
            set "FAILED_LIST=!FAILED_LIST! DiagTrack servisi (Calisiyor)"
        ) else (
            echo    [?] DiagTrack servisi durumu belirlenemedi
            set /a FAILED_COUNT+=1
            set "FAILED_LIST=!FAILED_LIST! DiagTrack servisi (belirlenemedi)"
        )
    )
)
echo.

REM ========================================
REM 5. GÜÇ PLANI
REM ========================================
echo [5/10] Güç plani kontrol ediliyor...
set /a TOTAL_COUNT+=1
set POWER_SCHEME=
for /f "tokens=*" %%i in ('powercfg /getactivescheme 2^>nul') do set POWER_SCHEME=%%i
if "!POWER_SCHEME!"=="" (
    echo    [?] Güç plani okunamadi
    set /a FAILED_COUNT+=1
    set "FAILED_LIST=!FAILED_LIST! Guc plani (okunamadi)"
) else (
    echo !POWER_SCHEME! | findstr /i "high performance" >nul
    if errorlevel 1 (
        echo    [!] High Performance plani aktif degil
        echo    Mevcut plan: !POWER_SCHEME!
        set /a FAILED_COUNT+=1
        set "FAILED_LIST=!FAILED_LIST! Guc plani (High Performance degil)"
    ) else (
        echo    [OK] High Performance plani AKTIF
    )
)
echo.

REM ========================================
REM 6. COPILOT (Windows 11 25H2)
REM ========================================
echo [6/10] Copilot kontrol ediliyor...
set /a TOTAL_COUNT+=1
reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v ShowCopilotButton >nul 2>&1
if errorlevel 1 (
    echo    [?] Copilot ayari bulunamadi
    set /a FAILED_COUNT+=1
    set "FAILED_LIST=!FAILED_LIST! Copilot (ayar bulunamadi)"
) else (
    set COPILOT=
    for /f "tokens=3" %%i in ('reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v ShowCopilotButton 2^>nul') do set COPILOT=%%i
    if "!COPILOT!"=="0x0" (
        echo    [OK] Copilot KAPALI
    ) else (
        echo    [!] Copilot ACIK: !COPILOT!
        set /a FAILED_COUNT+=1
        set "FAILED_LIST=!FAILED_LIST! Copilot (AciK: !COPILOT!)"
    )
)
echo.

REM ========================================
REM 7. WIDGETS
REM ========================================
echo [7/10] Widgets kontrol ediliyor...
set /a TOTAL_COUNT+=1
REM Windows 11'de WidgetsService farklı isimlerle olabilir
sc query WidgetsService >nul 2>&1
if errorlevel 1 (
    REM Alternatif servis isimlerini kontrol et
    sc query "WidgetsService" >nul 2>&1
    if errorlevel 1 (
        sc query "widgets" >nul 2>&1
        if errorlevel 1 (
            REM Servis bulunamadı - kayıt defterinden kontrol et
            reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarDa >nul 2>&1
            if errorlevel 1 (
                echo    [OK] Widgets servisi bulunamadi (muhtemelen kapatilmis)
            ) else (
                set WIDGETS_REG=
                for /f "tokens=3" %%i in ('reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarDa 2^>nul') do set WIDGETS_REG=%%i
                if "!WIDGETS_REG!"=="0x0" (
                    echo    [OK] Widgets KAPALI (kayit defteri)
                ) else (
                    echo    [!] Widgets ACIK (kayit defteri: !WIDGETS_REG!)
                    set /a FAILED_COUNT+=1
                    set "FAILED_LIST=!FAILED_LIST! Widgets (AciK: !WIDGETS_REG!)"
                )
            )
        ) else (
            REM widgets servisi bulundu
            sc query "widgets" 2>nul | findstr /I /C:"STOPPED" >nul
            if not errorlevel 1 (
                echo    [OK] Widgets servisi DURDURULMUS
            ) else (
                sc query "widgets" 2>nul | findstr /I /C:"RUNNING" >nul
                if not errorlevel 1 (
                    echo    [!] Widgets servisi CALISIYOR
                    set /a FAILED_COUNT+=1
                    set "FAILED_LIST=!FAILED_LIST! Widgets (Calisiyor)"
                ) else (
                    echo    [OK] Widgets servisi durumu belirlenemedi ama muhtemelen kapali
                )
            )
        )
    ) else (
        REM WidgetsService bulundu
        sc query "WidgetsService" 2>nul | findstr /I /C:"STOPPED" >nul
        if not errorlevel 1 (
            echo    [OK] WidgetsService servisi DURDURULMUS
        ) else (
            sc query "WidgetsService" 2>nul | findstr /I /C:"RUNNING" >nul
            if not errorlevel 1 (
                echo    [!] WidgetsService servisi CALISIYOR
                set /a FAILED_COUNT+=1
                set "FAILED_LIST=!FAILED_LIST! WidgetsService (Calisiyor)"
            ) else (
                echo    [OK] WidgetsService durumu belirlenemedi ama muhtemelen kapali
            )
        )
    )
) else (
    REM WidgetsService bulundu
    sc query WidgetsService 2>nul | findstr /I /C:"STOPPED" >nul
    if not errorlevel 1 (
        echo    [OK] WidgetsService servisi DURDURULMUS
    ) else (
        sc query WidgetsService 2>nul | findstr /I /C:"RUNNING" >nul
        if not errorlevel 1 (
            echo    [!] WidgetsService servisi CALISIYOR
            set /a FAILED_COUNT+=1
            set "FAILED_LIST=!FAILED_LIST! WidgetsService (Calisiyor)"
        ) else (
            echo    [OK] WidgetsService durumu belirlenemedi ama muhtemelen kapali
        )
    )
)
echo.

REM ========================================
REM 8. ACTIVITY HISTORY (TIMELINE)
REM ========================================
echo [8/10] Activity History kontrol ediliyor...
set /a TOTAL_COUNT+=1
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v EnableActivityFeed >nul 2>&1
if errorlevel 1 (
    echo    [?] Activity History ayari bulunamadi
    set /a FAILED_COUNT+=1
    set "FAILED_LIST=!FAILED_LIST! Activity History (ayar bulunamadi)"
) else (
    set ACTIVITY=
    for /f "tokens=3" %%i in ('reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v EnableActivityFeed 2^>nul') do set ACTIVITY=%%i
    if "!ACTIVITY!"=="0x0" (
        echo    [OK] Activity History KAPALI
    ) else (
        echo    [!] Activity History ACIK: !ACTIVITY!
        set /a FAILED_COUNT+=1
        set "FAILED_LIST=!FAILED_LIST! Activity History (AciK: !ACTIVITY!)"
    )
)
echo.

REM ========================================
REM 9. WINDOWS UPDATE DELIVERY OPTIMIZATION (P2P)
REM ========================================
echo [9/10] Windows Update P2P kontrol ediliyor...
set /a TOTAL_COUNT+=1
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\DeliveryOptimization\Config" /v DODownloadMode >nul 2>&1
if errorlevel 1 (
    echo    [?] P2P Update ayari bulunamadi
    set /a FAILED_COUNT+=1
    set "FAILED_LIST=!FAILED_LIST! P2P Update (ayar bulunamadi)"
) else (
    set P2P=
    for /f "tokens=3" %%i in ('reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\DeliveryOptimization\Config" /v DODownloadMode 2^>nul') do set P2P=%%i
    if "!P2P!"=="0x0" (
        echo    [OK] P2P Update Sharing KAPALI
    ) else (
        echo    [!] P2P Update Sharing ACIK: !P2P!
        set /a FAILED_COUNT+=1
        set "FAILED_LIST=!FAILED_LIST! P2P Update Sharing (AciK: !P2P!)"
    )
)
echo.

REM ========================================
REM 10. START MENU SUGGESTIONS
REM ========================================
echo [10/10] Start Menu Suggestions kontrol ediliyor...
set /a TOTAL_COUNT+=1
reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SystemPaneSuggestionsEnabled >nul 2>&1
if errorlevel 1 (
    echo    [?] Start Menu Suggestions ayari bulunamadi
    set /a FAILED_COUNT+=1
    set "FAILED_LIST=!FAILED_LIST! Start Menu Suggestions (ayar bulunamadi)"
) else (
    set SUGGESTIONS=
    for /f "tokens=3" %%i in ('reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SystemPaneSuggestionsEnabled 2^>nul') do set SUGGESTIONS=%%i
    if "!SUGGESTIONS!"=="0x0" (
        echo    [OK] Start Menu Suggestions KAPALI
    ) else (
        echo    [!] Start Menu Suggestions ACIK: !SUGGESTIONS!
        set /a FAILED_COUNT+=1
        set "FAILED_LIST=!FAILED_LIST! Start Menu Suggestions (AciK: !SUGGESTIONS!)"
    )
)
echo.

REM ========================================
REM ÖZET VE RAPOR
REM ========================================
echo ========================================
echo   Kontrol Tamamlandi
echo ========================================
echo.
echo Toplam kontrol edilen: %TOTAL_COUNT%
echo Basarisiz/Uygulanmamis: %FAILED_COUNT%
echo Basarili: %TOTAL_COUNT% - %FAILED_COUNT%
echo.

if %FAILED_COUNT% GTR 0 (
    echo [!] %FAILED_COUNT% ozellik uygulanmamis veya geri alinmis!
    echo.
    echo Uygulanmayan ozellikler:
    echo !FAILED_LIST!
    echo.
    
    REM Dosyaya yaz
    set "REPORT_FILE=optimizasyon_raporu.txt"
    (
        echo ========================================
        echo   Windows 11 Optimizer - Uygulanmayan Ozellikler
        echo   Tarih: %DATE% %TIME%
        echo ========================================
        echo.
        echo Toplam kontrol edilen: %TOTAL_COUNT%
        echo Basarisiz/Uygulanmamis: %FAILED_COUNT%
        echo Basarili: %TOTAL_COUNT% - %FAILED_COUNT%
        echo.
        echo UYGULANMAYAN OZELLIKLER:
        echo.
        echo !FAILED_LIST!
        echo.
        echo NOT: Bu ozellikleri tekrar uygulamak icin
        echo Windows11Optimizer.exe dosyasini yonetici olarak calistirin.
    ) > "%REPORT_FILE%"
    
    echo Rapor dosyasi olusturuldu: %REPORT_FILE%
    echo.
    echo NOT: Eger [!] isaretli maddeler varsa, Windows Update
    echo bazı ayarlari geri almış olabilir. Bu durumda optimize.exe
    echo dosyasini tekrar calistirabilirsiniz.
) else (
    echo [OK] Tum ozellikler basariyla uygulanmis!
    echo.
)

echo.
echo Devam etmek icin bir tusa basin...
pause
exit /b 0
