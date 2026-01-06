# Scriptin Yaptığı Değişiklikler - Detaylı Liste

## 📋 1. SERVİS DEĞİŞİKLİKLERİ (19 Servis Devre Dışı)

### Telemetri ve Veri Toplama Servisleri
- **DiagTrack** - Connected User Experiences and Telemetry (Windows telemetri)
- **dmwappushservice** - WAP Push Message Routing Service (reklam bildirimleri)
- **wisvc** - Windows Insider Service (Windows Insider programı)

### Xbox Servisleri
- **XblAuthManager** - Xbox Live Auth Manager
- **XblGameSave** - Xbox Live Game Save
- **XboxGipSvc** - Xbox Accessory Management Service
- **XboxNetApiSvc** - Xbox Live Networking Service

### Gereksiz Windows Servisleri
- **WSearch** - Windows Search (arama servisi - performans için)
- **RetailDemo** - Retail Demo Service (mağaza demo servisi)
- **RemoteRegistry** - Remote Registry (uzaktan kayıt defteri erişimi)
- **RemoteAccess** - Routing and Remote Access (uzaktan erişim)
- **Spooler** - Print Spooler (yazıcı servisi - yazıcı kullanmıyorsanız)
- **TabletInputService** - Touch Keyboard and Handwriting Panel Service
- **WbioSrvc** - Windows Biometric Service (parmak izi/yüz tanıma)
- **WerSvc** - Windows Error Reporting Service (hata raporlama)
- **WMPNetworkSvc** - Windows Media Player Network Sharing Service
- **WpcMonSvc** - Parental Controls (ebeveyn kontrolü)
- **WpnService** - Windows Push Notifications Service (bildirim servisi)
- **SysMain** - SysMain (Superfetch) - SSD için gereksiz, RAM kullanımını azaltır

### ✅ KORUNAN SERVİSLER (Yazılım Geliştirme İçin)
- Windows Update (wuauserv)
- WSL2 ve Hyper-V servisleri
- Windows Remote Management (WinRM)
- Volume Shadow Copy (VSS)
- Event Log, DNS, DHCP, vb. temel servisler
- Themes (bazı uygulamalar için gerekli)

---

## 🔧 2. KAYIT DEFTERİ DEĞİŞİKLİKLERİ (18+ Ayar)

### Telemetri ve Gizlilik
- **AllowTelemetry = 0** (2 farklı konumda)
  - `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection`
  - `HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection`

### Oyun Optimizasyonları
- **Game Mode Aktif**
  - `HKCU\SOFTWARE\Microsoft\GameBar\AllowAutoGameMode = 1`
  - `HKCU\SOFTWARE\Microsoft\GameBar\AutoGameModeEnabled = 1`

- **GPU Scheduling Aktif** (RTX 3070 için)
  - `HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\HwSchMode = 2`

- **Network Throttling Kapatıldı** (oyun gecikmesini azaltır)
  - `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\NetworkThrottlingIndex = 0xFFFFFFFF`

- **Timer Resolution Optimize Edildi** (daha düşük gecikme)
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\kernel\GlobalTimerResolutionRequests = 1`

### Performans Optimizasyonları
- **Windows Search Manuel** (otomatik başlamaz)
  - `HKLM\SYSTEM\CurrentControlSet\Services\WSearch\Start = 3`

- **Prefetch/Superfetch Kapatıldı** (SSD için gereksiz)
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters\EnableSuperfetch = 0`
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters\EnablePrefetcher = 0`

- **Fast Startup Kapatıldı** (bazı sorunları önler)
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power\HiberbootEnabled = 0`

### Gizlilik Ayarları
- **Reklam ID Devre Dışı**
  - `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo\Enabled = 0`
  - `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo\Enabled = 0`

- **Konum Servisleri Kapatıldı**
  - `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location\Value = "Deny"`

### Windows Update
- **Windows Update UX Ayarları**
  - `HKLM\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings\UxOption = 1` (otomatik restart kontrolü)

---

## ⚡ 3. PERFORMANS AYARLARI

### Güç Planı
- **High Performance Planı Aktif Edildi**
  - GUID: `8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c`
  - Maksimum performans için CPU ve GPU'yu tam güçte tutar

### Güç Ayarları Optimizasyonları
- **USB Selective Suspend Kapatıldı**
  - USB cihazların uyku moduna geçmesi engellendi (performans için)

- **PCI Express Link State Power Management Kapatıldı**
  - GPU ve diğer PCIe cihazların güç tasarrufu modu kapatıldı (oyun performansı için)

### Görsel Efektler
- **Görsel Efektler Optimize Edildi**
  - `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects\VisualFXSetting = 2`
  - "Best performance" modu aktif (animasyonlar ve efektler azaltıldı)

---

## 🔒 4. GİZLİLİK AYARLARI

### Telemetri
- Windows Telemetry tamamen kapatıldı (2 farklı kayıt defteri konumunda)

### Reklam ve Takip
- Reklam ID'si devre dışı bırakıldı
- Windows reklamları ve kişiselleştirilmiş içerik kapatıldı

### Konum Servisleri
- Konum takibi tamamen kapatıldı

### Cortana
- Cortana devre dışı bırakıldı
  - `HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search\AllowCortana = 0`

---

## 🎯 5. WINDOWS ÖZELLİKLERİ

### Kapatılan Özellikler
- **MicrosoftWindowsPowerShellV2Root** - PowerShell 2.0 (eski, güvenlik açığı riski)
- **WorkFolders-Client** - Work Folders Client (kullanılmıyorsa)
- **MediaPlayback** - Media Features (isteğe bağlı)

### ✅ KORUNAN ÖZELLİKLER (Yazılım Geliştirme İçin)
- **Microsoft-Windows-Subsystem-Linux** - WSL2 (Linux alt sistemi)
- **Microsoft-Hyper-V-All** - Hyper-V (sanal makine desteği)
- **Containers** - Windows Containers
- **VirtualMachinePlatform** - Virtual Machine Platform

---

## 📊 ÖZET İSTATİSTİKLER

- **Toplam Servis Değişikliği:** ~19 servis devre dışı
- **Toplam Kayıt Defteri Değişikliği:** ~18+ ayar
- **Performans Optimizasyonları:** 5+ ayar
- **Gizlilik Optimizasyonları:** 4+ ayar
- **Windows Özellikleri:** 3 özellik kapatıldı

---

## ⚠️ ÖNEMLİ NOTLAR

### Korunan Özellikler
- ✅ Windows Defender (güvenlik için açık)
- ✅ Windows Update (güncellemeler için açık)
- ✅ WSL2 ve Hyper-V (yazılım geliştirme için)
- ✅ Temel sistem servisleri (DNS, DHCP, Event Log, vb.)

### Etkilenmeyen Özellikler
- Windows Defender Real-Time Protection açık kalır
- Yazılım geliştirme araçları çalışmaya devam eder
- Oyunlar ve uygulamalar normal çalışır
- Sistem güvenliği korunur

### Potansiyel Etkiler
- Windows Search kapatıldığı için dosya arama yavaşlayabilir (performans için)
- Yazıcı servisi kapatıldığı için yazıcı kullanımı için manuel açmanız gerekebilir
- Bazı Xbox özellikleri çalışmayabilir (Xbox kullanmıyorsanız sorun değil)

---

## 🔄 GERİ ALMA

Tüm değişiklikler `backups/` klasörüne yedeklenir. Geri almak için:

```powershell
python restore.py
```

