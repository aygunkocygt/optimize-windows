# What We Did (Windows 11 Optimizer - 25H2)

Bu doküman, `docs/NE_YAPTIK.md` + `docs/DEGISIKLIKLER.md` içeriklerini **tek dosyada** birleştirir. Amaç: kullanıcı ve geliştirici açısından “ne yaptık / ne değişti” bilgisini tek yerde toplamak.

## Goals (Hedefler)

- **Oyun odaklı**: input lag, stutter ve 1% low tarafını iyileştirmek için arka plan yükünü azaltmak.
- **Dev/daily bozmamak**: Docker/Node/Python/Go akışlarını olabildiğince korumak.
- **Tek profil / seçim yok**: kullanıcıya seçim yaptırmadan tek davranış.
- **Geri alınabilirlik**: mümkün olduğunca yedek al, restore ile geri dön.

## Measurement: “Optimization Rate” (Optimizasyon Oranı)

Bu proje FPS’i **otomatik benchmark etmez**. Onun yerine `check_changes.bat` kontrol ettiği maddeler için bir kapsama yüzdesi verir:

\[
\text{Optimizasyon Oranı} = \frac{\text{Başarılı}}{\text{Toplam}} \times 100
\]

Bu değer “optimizasyonların kaç tanesi aktif kaldı?” sorusunu cevaplar; FPS kazancı ise oyuna/sürücüye/sisteme göre değişir.

## Genel Mimari Prensipleri (docs/ARCHITECTURE.md’den)

- **Modüler yapı**: Windows’a dokunan her alan ayrı modülde (servis/registry/privacy/features/apps/startup/tasks/onedrive).
- **Geri alınabilirlik**: çalıştırma öncesi backup alınır, restore best-effort geri döndürür.

> Repo içinde Event-Driven / Plugin tabanlı yeni mimari de bulunur (`core/`, `plugins/`, `services/`, `application.py`).  
> Ancak EXE üretim akışı şu an `optimize.py` üzerinden ilerler (tek profil, hızlı).

## Runtime Akışı

1. **Admin kontrolü**
2. **Backup** (`backups/backup_*.json`)
3. **Optimizasyon modüllerinin sırayla çalıştırılması**
4. **Özet + restart gerekebilir notu**

## High-Level: Neleri Değiştiriyoruz?

### 1) Servisler (`modules/services.py`)
- Telemetry/Xbox/Widgets/Search gibi arka plan servisleri azaltılır.
- Not: “servis trimming” (daha agresif liste) koddadır ama tek profilde stabilite için devreye alınmaz.

### 2) Registry Tweaks (`modules/registry.py`)
- Oyun/pacing/input lag için bilinen policy/tweak’ler uygulanır.
- Registry backup deterministiktir: dokunulan tüm `(path,value)` ikilileri yedeklenir, restore eski haline döndürür.

### 3) Privacy + Kalıcılık (`modules/privacy.py`)
- Telemetry policy’leri set edilir; servisler stop/disable edilir.
- `TelemetryBlocker` scheduled task kurulabilir (restore bunu kaldırır).

### 4) Startup + Scheduled Tasks (`modules/startup_tasks.py`)
- Teams/OneDrive gibi istenmeyen Run girdileri kaldırılır.
- CEIP / Feedback / GameDVR / XblGameSave / OneDrive / WER vb. task’lar devre dışı bırakılır (safe set).
- Restore: önceki state’e göre enable etmeyi dener (best-effort).

### 5) Windows Optional Features (`modules/features.py`)
- Güvenli, düşük riskli optional feature kapatmaları yapılır.
- Backup: sadece dokunabileceğimiz feature’lar.

### 6) Uygulama kaldırma (`modules/apps_remover.py`)
- UWP bloat kaldırma (Phone Link, Xbox, Bing vb.).
- Store/Calculator/Terminal/Camera gibi temel şeyler korunur.

### 7) OneDrive (agresif) (`modules/onedrive_optimizer.py`)
- `OneDriveSetup.exe /uninstall` ile kaldırmayı dener.
- Restore: `OneDriveSetup.exe /install` ile geri kurmayı dener (**best-effort**).

### 8) Core Isolation / VBS / HVCI / Credential Guard (`modules/security_virtualization.py`)
- Core Isolation (Memory Integrity/HVCI) + VBS + Credential Guard kapatılır.
- `bcdedit hypervisorlaunchtype off` **kullanılmaz** (Docker/dev bozulmasın).

## Detailed Change List (Detaylı Liste)

### 1) Servis Değişiklikleri

#### Telemetri ve Veri Toplama Servisleri
- **DiagTrack** - Connected User Experiences and Telemetry
- **dmwappushservice** - WAP Push Message Routing Service
- **wisvc** - Windows Insider Service

#### Xbox Servisleri
- **XblAuthManager** - Xbox Live Auth Manager
- **XblGameSave** - Xbox Live Game Save
- **XboxGipSvc** - Xbox Accessory Management Service
- **XboxNetApiSvc** - Xbox Live Networking Service

#### Diğer Gereksiz Servisler
- **WSearch** - Windows Search
- **RetailDemo** - Retail Demo Service
- **RemoteRegistry** - Remote Registry
- **RemoteAccess** - Routing and Remote Access
- **Spooler** - Print Spooler (printer yoksa)
- **TabletInputService** - Touch Keyboard and Handwriting Panel
- **WbioSrvc** - Windows Biometric Service
- **WerSvc** - Windows Error Reporting Service
- **WMPNetworkSvc** - WMP Network Sharing
- **WpcMonSvc** - Parental Controls
- **WpnService** - Push Notifications
- **SysMain** - SysMain (Superfetch)

#### Korunanlar (dev/daily için)
- Windows Update (wuauserv), temel sistem servisleri, WSL2/Hyper-V altyapısı, vb.

### 2) Registry Değişiklikleri (Örnekler)

#### Oyun
- Game Mode (HKCU\...\GameBar)
- GPU Scheduling / HAGS (`HwSchMode = 2`)
- NetworkThrottlingIndex = `0xFFFFFFFF`
- GlobalTimerResolutionRequests = `1`
- GameDVR/capture kapatma + Game Bar UI kapatma
- Toast/notification kapatma
- Bing/Web search kapatma

#### Gizlilik / veri toplama
- Telemetry policy’leri (AllowTelemetry/MaxTelemetryAllowed/...)
- Timeline/Activity History kapatma
- Delivery Optimization (P2P) kapatma
- Advertising ID kapatma
- Location consent “Deny”

#### OneDrive
- OneDrive policy: `DisableFileSyncNGSC = 1`

### 3) Performans Ayarları
- High Performance power plan (GUID: `8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c`)
- USB Selective Suspend kapatma
- PCIe Link State Power Management kapatma
- VisualFX “Best performance”

### 4) Gizlilik (Windows 11 25H2)
- Copilot kapatma
- Widgets kapatma
- Arka plan veri toplama azaltmaları (Timeline, Suggestions, Spotlight, vb.)

### 5) Windows Optional Features
- PowerShell v2 / WorkFolders / Media/IE optional kapatma (güvenli liste)

### 6) Kaldırılan Uygulamalar (UWP)
- Phone Link, Xbox app/overlay, Bing apps, Feedback Hub, Maps vb.
- Kamera gibi gerekli uygulamalar korunur.

## Restore (Geri Alma) Nasıl Çalışır?

`restore.py`:
- Servis start type’ları geri yazar
- Registry değerlerini eski haline döndürür (yoksa siler)
- Optional feature’ları eski state’e döndürür
- Disabled task’ları enable eder (best-effort)
- TelemetryBlocker task’ını kaldırır
- OneDrive geri kurmayı dener (best-effort)

## Bilinçli Olarak Dokunmadıklarımız

- **NVIDIA Overlay / GFE overlay**: kullanıcı isteğiyle dokunmuyoruz.
- **WSL2/Hyper-V boot-level kapatma**: `bcdedit` ile hypervisor kapatma yapılmaz (Docker/dev kırar).


