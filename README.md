# Windows 11 Optimizer (25H2)

Oyun performansı odaklı, **tek profil** çalışan Windows 11 optimizasyon aracı. Amaç: **input lag ve 1% low** tarafını iyileştirmek için arka plan yükünü azaltmak; **Docker/Node/Python/Go** gibi geliştirme akışlarını bozmadan.

### Kurulum + EXE Build (tek komut)

```powershell
.\build.bat
```

### Kullanım

```powershell
# Optimizasyon (Yönetici)
.\dist\Windows11Optimizer.exe

# Geri yükleme (Yönetici)
.\dist\Windows11Restore.exe
```

### Doğrulama + “Optimizasyon Oranı” (%)

```powershell
.\check_changes.bat
```

`check_changes.bat` çıktısındaki **Optimizasyon Oranı**, kontrol edilen maddelerin başarı oranıdır:
\[
\text{Optimizasyon Oranı} = \frac{\text{Başarılı}}{\text{Toplam}} \times 100
\]

> Not: Bu yüzde **FPS benchmark** değildir. Gerçek FPS/1% low kazancı oyuna ve sisteme göre değişir.

## Kapatılan / Kaldırılanlar (Tablo)

| Kategori | Aksiyon | Örnekler |
|---|---|---|
| **Servisler** | Devre dışı | Telemetry/Xbox/Widgets/Search vb. (`DiagTrack`, `dmwappushservice`, `wisvc`, `Xbl*`, `Xbox*`, `SysMain`, `WidgetsService`, `WSearch` ...) |
| **Registry** | Oyun + gizlilik tweak | Game Mode, HAGS, NetworkThrottlingIndex, Timer request, GameDVR/capture kapatma, Game Bar UI kapatma, Bing/Web search kapatma, toast/notification kapatma, OneDrive policy, P2P/Timeline/Telemetry policy |
| **Scheduled Tasks** | Devre dışı | CEIP / Application Experience / Feedback / GameDVR / XblGameSave / OneDrive / Windows Error Reporting task’ları |
| **Windows Optional Features** | Devre dışı | PowerShell v2, WorkFolders, Media/IE optional (güvenli liste) |
| **Uygulamalar** | Kaldır | Phone Link, Xbox app/overlay, Bing apps, Feedback Hub, Maps vb. + **OneDrive (OneDriveSetup.exe /uninstall)** |

## Restore (Geri Alma)

`Windows11Restore.exe` şunları geri alır:
- Servis start type (yedekten)
- Registry değerleri (yedekten eski haline)
- Windows Optional Features (sadece dokunulan feature’lar)
- Startup (Run) girdileri + disabled scheduled task’lar (yedekten)
- TelemetryBlocker task’ı (silinir)
- OneDrive (mümkünse yeniden kurmayı dener, **best-effort**)

## Detaylı “Ne yaptık / Neden” dokümanı

Kısa README yerine detaylar burada:
- `docs/WHAT_WE_DID.md`
- `docs/ARCHITECTURE.md`
