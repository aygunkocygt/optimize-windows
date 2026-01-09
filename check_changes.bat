@echo off
REM ========================================
REM Windows 11 Optimizer - Değişiklik Kontrolü (GÜNCEL)
REM Amaç: optimizer'ın uyguladığı ayarların aktif olup olmadığını hızlıca raporlamak
REM Not: Bu script SADECE kontrol eder, sistemde değişiklik yapmaz.
REM ========================================

setlocal enabledelayedexpansion
cd /d "%~dp0" 2>nul

set "FAILED_COUNT=0"
set "TOTAL_COUNT=0"
set "FAILED_LIST="
set "REPORT_FILE=optimizasyon_raporu.txt"
set "CHECKS_TOTAL=19"

echo.
echo ========================================
echo   Windows 11 Optimizer - Kontrol
echo ========================================
echo.

REM ------------------------------------------------
REM 1) Telemetry registry (AllowTelemetry + MaxTelemetryAllowed)
REM ------------------------------------------------
echo [1/%CHECKS_TOTAL%] Telemetry (registry) kontrol ediliyor...
set /a TOTAL_COUNT+=1
call :CheckRegDword "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" "AllowTelemetry" "0x0" "AllowTelemetry (Policies\DataCollection)"
call :CheckRegDword "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" "AllowTelemetry" "0x0" "AllowTelemetry (Policies\Microsoft\Windows\DataCollection)"
call :CheckRegDword "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" "MaxTelemetryAllowed" "0x0" "MaxTelemetryAllowed"
call :CheckRegDword "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" "MaxTelemetryAllowed" "0x0" "MaxTelemetryAllowed (Policies)"
echo.

REM ------------------------------------------------
REM 2) Telemetry services (stopped + disabled)
REM ------------------------------------------------
echo [2/%CHECKS_TOTAL%] Telemetry servisleri kontrol ediliyor...
set /a TOTAL_COUNT+=1
call :CheckServiceStoppedDisabled "DiagTrack" "DiagTrack"
call :CheckServiceStoppedDisabled "dmwappushservice" "dmwappushservice"
call :CheckServiceStoppedDisabled "wisvc" "wisvc"
echo.

REM ------------------------------------------------
REM 3) TelemetryBlocker scheduled task (persistence)
REM ------------------------------------------------
echo [3/%CHECKS_TOTAL%] TelemetryBlocker task kontrol ediliyor...
set /a TOTAL_COUNT+=1
schtasks /Query /TN "TelemetryBlocker" >nul 2>&1
if errorlevel 1 (
    echo    [!] TelemetryBlocker task YOK (kalıcılık daha zayıf)
    set /a FAILED_COUNT+=1
    call :AddFail "TelemetryBlocker task (yok)"
) else (
    echo    [OK] TelemetryBlocker task VAR
)
echo.

REM ------------------------------------------------
REM 4) Game Mode
REM ------------------------------------------------
echo [4/%CHECKS_TOTAL%] Game Mode kontrol ediliyor...
set /a TOTAL_COUNT+=1
call :CheckRegDword "HKCU\SOFTWARE\Microsoft\GameBar" "AllowAutoGameMode" "0x1" "Game Mode"
echo.

REM ------------------------------------------------
REM 5) GPU Scheduling (HAGS)
REM ------------------------------------------------
echo [5/%CHECKS_TOTAL%] GPU Scheduling kontrol ediliyor...
set /a TOTAL_COUNT+=1
call :CheckRegDword "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" "HwSchMode" "0x2" "GPU Scheduling (HwSchMode)"
echo.

REM ------------------------------------------------
REM 6) Power plan (GUID-based, locale-safe)
REM ------------------------------------------------
echo [6/%CHECKS_TOTAL%] Güç planı kontrol ediliyor...
set /a TOTAL_COUNT+=1
set "POWER_SCHEME="
for /f "tokens=*" %%i in ('powercfg /getactivescheme 2^>nul') do set "POWER_SCHEME=%%i"
if "!POWER_SCHEME!"=="" (
    echo    [!] Güç planı okunamadı
    set /a FAILED_COUNT+=1
    call :AddFail "Güç planı (okunamadı)"
) else (
    echo !POWER_SCHEME! | findstr /i "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c" >nul
    if errorlevel 1 (
        echo    [!] High Performance (GUID) aktif değil
        echo    Mevcut: !POWER_SCHEME!
        set /a FAILED_COUNT+=1
        call :AddFail "Güç planı (High Performance değil)"
    ) else (
        echo    [OK] High Performance (GUID) aktif
    )
)
echo.

REM ------------------------------------------------
REM 7) Copilot (taskbar icon)
REM ------------------------------------------------
echo [7/%CHECKS_TOTAL%] Copilot kontrol ediliyor...
set /a TOTAL_COUNT+=1
call :CheckRegDword "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" "ShowCopilotButton" "0x0" "Copilot (ShowCopilotButton)"
call :CheckRegDwordOptional "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" "CopilotTaskbarIcon" "0x0" "Copilot (CopilotTaskbarIcon)"
echo.

REM ------------------------------------------------
REM 8) Widgets (registry)
REM ------------------------------------------------
echo [8/%CHECKS_TOTAL%] Widgets kontrol ediliyor...
set /a TOTAL_COUNT+=1
call :CheckRegDwordOptional "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" "TaskbarDa" "0x0" "Widgets (TaskbarDa)"
echo.

REM ------------------------------------------------
REM 9) Activity History (Timeline)
REM ------------------------------------------------
echo [9/%CHECKS_TOTAL%] Activity History kontrol ediliyor...
set /a TOTAL_COUNT+=1
call :CheckRegDword "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" "EnableActivityFeed" "0x0" "Activity History"
call :CheckRegDwordOptional "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" "PublishUserActivities" "0x0" "PublishUserActivities"
call :CheckRegDwordOptional "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" "UploadUserActivities" "0x0" "UploadUserActivities"
echo.

REM ------------------------------------------------
REM 10) Delivery Optimization (P2P)
REM ------------------------------------------------
echo [10/%CHECKS_TOTAL%] Windows Update P2P kontrol ediliyor...
set /a TOTAL_COUNT+=1
call :CheckRegDword "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\DeliveryOptimization\Config" "DODownloadMode" "0x0" "P2P (DODownloadMode)"
echo.

REM ------------------------------------------------
REM 11) Start Menu Suggestions
REM ------------------------------------------------
echo [11/%CHECKS_TOTAL%] Start Menu Suggestions kontrol ediliyor...
set /a TOTAL_COUNT+=1
call :CheckRegDword "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" "SystemPaneSuggestionsEnabled" "0x0" "Start Menu Suggestions"
echo.

REM ------------------------------------------------
REM 12) GameDVR / Capture (Xbox capture kapalı)
REM ------------------------------------------------
echo [12/%CHECKS_TOTAL%] GameDVR/Capture kontrol ediliyor...
set /a TOTAL_COUNT+=1
call :CheckRegDword "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" "AllowGameDVR" "0x0" "AllowGameDVR"
call :CheckRegDword "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR" "AppCaptureEnabled" "0x0" "AppCaptureEnabled"
call :CheckRegDwordOptional "HKCU\SYSTEM\GameConfigStore" "GameDVR_Enabled" "0x0" "GameDVR_Enabled"
echo.

REM ------------------------------------------------
REM 13) Web Search (Bing) kapalı
REM ------------------------------------------------
echo [13/%CHECKS_TOTAL%] Web/Bing Search kontrol ediliyor...
set /a TOTAL_COUNT+=1
call :CheckRegDword "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" "DisableWebSearch" "0x1" "DisableWebSearch"
call :CheckRegDwordOptional "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" "ConnectedSearchUseWeb" "0x0" "ConnectedSearchUseWeb"
call :CheckRegDwordOptional "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Search" "BingSearchEnabled" "0x0" "BingSearchEnabled"
echo.

REM ------------------------------------------------
REM 14) Notifications/Toasts kapalı
REM ------------------------------------------------
echo [14/%CHECKS_TOTAL%] Bildirim (Toast) kontrol ediliyor...
set /a TOTAL_COUNT+=1
call :CheckRegDwordOptional "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\PushNotifications" "ToastEnabled" "0x0" "ToastEnabled"
echo.

REM ------------------------------------------------
REM 15) UI Effects (Transparency/Taskbar animations)
REM ------------------------------------------------
echo [15/%CHECKS_TOTAL%] UI efektleri kontrol ediliyor...
set /a TOTAL_COUNT+=1
call :CheckRegDwordOptional "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize" "EnableTransparency" "0x0" "EnableTransparency"
call :CheckRegDwordOptional "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" "TaskbarAnimations" "0x0" "TaskbarAnimations"
echo.

REM ------------------------------------------------
REM 16) Background apps policy
REM ------------------------------------------------
echo [16/%CHECKS_TOTAL%] Background apps policy kontrol ediliyor...
set /a TOTAL_COUNT+=1
call :CheckRegDword "HKLM\SOFTWARE\Policies\Microsoft\Windows\AppPrivacy" "LetAppsRunInBackground" "0x2" "LetAppsRunInBackground"
echo.

REM ------------------------------------------------
REM 17) OneDrive policy (sync kapalı)
REM ------------------------------------------------
echo [17/%CHECKS_TOTAL%] OneDrive policy kontrol ediliyor...
set /a TOTAL_COUNT+=1
call :CheckRegDword "HKLM\SOFTWARE\Policies\Microsoft\Windows\OneDrive" "DisableFileSyncNGSC" "0x1" "DisableFileSyncNGSC"
echo.

REM ------------------------------------------------
REM 18) Scheduler tweaks (Multimedia\SystemProfile)
REM ------------------------------------------------
echo [18/%CHECKS_TOTAL%] Scheduler tweak'leri kontrol ediliyor...
set /a TOTAL_COUNT+=1
call :CheckRegDword "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" "Win32PrioritySeparation" "0x26" "Win32PrioritySeparation"
call :CheckRegDword "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" "SystemResponsiveness" "0xa" "SystemResponsiveness"
call :CheckRegDwordOptional "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" "Priority" "0x6" "Games Priority"
echo.

REM ------------------------------------------------
REM 19) Core Isolation / VBS / HVCI / Credential Guard
REM ------------------------------------------------
echo [19/%CHECKS_TOTAL%] VBS/HVCI/Credential Guard kontrol ediliyor...
set /a TOTAL_COUNT+=1
call :CheckRegDwordOptional "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard" "EnableVirtualizationBasedSecurity" "0x0" "VBS"
call :CheckRegDwordOptional "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity" "Enabled" "0x0" "HVCI"
call :CheckRegDwordOptional "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" "LsaCfgFlags" "0x0" "Credential Guard"
echo.

REM ========================================
REM ÖZET VE RAPOR
REM ========================================
echo ========================================
echo   Kontrol Tamamlandi
echo ========================================
echo.
set /a SUCCESS_COUNT=%TOTAL_COUNT%-%FAILED_COUNT%
if %TOTAL_COUNT% GTR 0 (
    set /a OPT_PERCENT=SUCCESS_COUNT*100/TOTAL_COUNT
) else (
    set /a OPT_PERCENT=0
)
echo Toplam kontrol edilen: %TOTAL_COUNT%
echo Basarisiz/Uygulanmamis: %FAILED_COUNT%
echo Basarili: %SUCCESS_COUNT%
echo Optimizasyon Orani: %OPT_PERCENT%%%
echo.

if %FAILED_COUNT% GTR 0 (
    echo [!] %FAILED_COUNT% madde uygulanmamis veya geri alinmis gorunuyor.
    echo.
    echo Uygulanmayanlar:
    echo !FAILED_LIST!
    echo.
    
    REM Dosyaya yaz
    set "REPORT_FILE=optimizasyon_raporu.txt"
    (
        echo ========================================
        echo   Windows 11 Optimizer - Uygulanmayanlar
        echo   Tarih: %DATE% %TIME%
        echo ========================================
        echo.
        echo Toplam kontrol edilen: %TOTAL_COUNT%
        echo Basarisiz/Uygulanmamis: %FAILED_COUNT%
        echo Basarili: %SUCCESS_COUNT%
        echo Optimizasyon Orani: %OPT_PERCENT%%%
        echo.
        echo UYGULANMAYANLAR:
        echo.
        echo !FAILED_LIST!
        echo.
        echo NOT: Yeniden uygulamak icin Windows11Optimizer.exe'yi yonetici olarak calistirin.
    ) > "%REPORT_FILE%"
    
    echo Rapor dosyasi olusturuldu: %REPORT_FILE%
    echo.
    echo NOT: Eger [!] isaretli maddeler varsa, Windows Update bazi ayarlari geri almis olabilir.
) else (
    echo [OK] Tum kontroller basarili gorunuyor.
    echo.
)

echo.
echo Devam etmek icin bir tusa basin...
pause
exit /b 0

REM ========================================
REM Helpers
REM ========================================
:AddFail
set "ITEM=%~1"
if "!FAILED_LIST!"=="" (
    set "FAILED_LIST=%ITEM%"
) else (
    set "FAILED_LIST=!FAILED_LIST! ^| %ITEM%"
)
exit /b 0

:CheckRegDword
set "KEY=%~1"
set "VAL=%~2"
set "EXPECT=%~3"
set "LABEL=%~4"
set "DATA="
for /f "tokens=3" %%i in ('reg query "%KEY%" /v "%VAL%" 2^>nul') do set "DATA=%%i"
if "!DATA!"=="" (
    echo    [!] !LABEL! okunamadi / yok
    set /a FAILED_COUNT+=1
    call :AddFail "!LABEL! (yok)"
    exit /b 0
)
if /i "!DATA!"=="%EXPECT%" (
    echo    [OK] !LABEL!
) else (
    echo    [!] !LABEL! beklenen=%EXPECT% mevcut=!DATA!
    set /a FAILED_COUNT+=1
    call :AddFail "!LABEL! (!DATA!)"
)
exit /b 0

:CheckRegDwordOptional
set "KEY=%~1"
set "VAL=%~2"
set "EXPECT=%~3"
set "LABEL=%~4"
set "DATA="
for /f "tokens=3" %%i in ('reg query "%KEY%" /v "%VAL%" 2^>nul') do set "DATA=%%i"
if "!DATA!"=="" (
    echo    [?] !LABEL! bulunamadi (opsiyonel)
    exit /b 0
)
if /i "!DATA!"=="%EXPECT%" (
    echo    [OK] !LABEL!
) else (
    echo    [!] !LABEL! beklenen=%EXPECT% mevcut=!DATA!
    set /a FAILED_COUNT+=1
    call :AddFail "!LABEL! (!DATA!)"
)
exit /b 0

:CheckServiceStoppedDisabled
set "SVC=%~1"
set "LABEL=%~2"
sc query "%SVC%" >nul 2>&1
if errorlevel 1 (
    echo    [?] %LABEL% servisi bulunamadi
    exit /b 0
)
set "RUNSTATE="
sc query "%SVC%" 2>nul | findstr /I /C:"STOPPED" >nul && set "RUNSTATE=STOPPED"
if not defined RUNSTATE (
    sc query "%SVC%" 2>nul | findstr /I /C:"RUNNING" >nul && set "RUNSTATE=RUNNING"
)
set "STARTTYPE="
for /f "tokens=4" %%i in ('sc qc "%SVC%" 2^>nul ^| findstr /I "START_TYPE"') do set "STARTTYPE=%%i"
if /i "!RUNSTATE!"=="STOPPED" (
    if "!STARTTYPE!"=="4" (
        echo    [OK] %LABEL% STOPPED + DISABLED
    ) else (
        echo    [!] %LABEL% STOPPED ama start_type=%STARTTYPE%
        set /a FAILED_COUNT+=1
        call :AddFail "%LABEL% (start_type=%STARTTYPE%)"
    )
) else (
    echo    [!] %LABEL% RUNNING
    set /a FAILED_COUNT+=1
    call :AddFail "%LABEL% (running)"
)
exit /b 0
