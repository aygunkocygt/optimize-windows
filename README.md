# Windows 11 Optimizer - Balanced Edition

Windows 11 25H2 için dengeli optimizasyon aracı. Atlas OS benzeri optimizasyonlar sunar ancak oyun performansı ve yazılım geliştirme uyumluluğunu dengeler.

## 🚀 Hızlı Başlangıç

### Kurulum

**Tek komutla kurulum ve build:**
```powershell
.\build.bat
```

Bu script otomatik olarak:
- Python kurulumunu kontrol eder
- Gerekli paketleri yükler
- EXE dosyalarını oluşturur

**Manuel kurulum:**
```powershell
python -m pip install -r requirements.txt
```

**Not:** Eğer `pip` komutu tanınmıyorsa, `python -m pip` kullanın!

### Python Bulunamadı?

1. Python'u yükleyin: https://www.python.org/downloads/
2. Kurulum sırasında **"Add Python to PATH"** seçeneğini işaretleyin
3. PowerShell'i yeniden başlatın

### Kullanım

**ÖNEMLİ:** Bu script yönetici haklarıyla çalıştırılmalıdır!

```powershell
# Yeni mimari ile (önerilen)
python application.py

# Eski kod ile (hala çalışıyor)
python optimize.py

# Geri yükleme
python restore.py
```

## ✨ Özellikler

- ✅ Gereksiz Windows servislerini devre dışı bırakma
- ✅ Telemetri ve veri toplama özelliklerini kapatma
- ✅ Performans optimizasyonları (gaming + development)
- ✅ Kayıt defteri optimizasyonları
- ✅ Windows özelliklerini optimize etme
- ✅ Güvenlik ayarlarını koruma (yazılım geliştirme için gerekli)
- ✅ Event-driven architecture (senior-level)
- ✅ Plugin system (kolay genişletilebilirlik)
- ✅ Renkli UI ve ilerleme göstergeleri

## 📋 Yapılan Değişiklikler

### Servisler (19 servis devre dışı)
- **Telemetri:** DiagTrack, dmwappushservice, wisvc
- **Xbox:** Tüm Xbox servisleri (XblAuthManager, XblGameSave, vb.)
- **Gereksiz:** Windows Search, Remote Registry, Print Spooler, SysMain (Superfetch), vb.

**Korunan Servisler:**
- Windows Update, WSL2, Hyper-V, temel sistem servisleri

### Kayıt Defteri (18+ ayar)
- **Oyun:** Game Mode aktif, GPU Scheduling aktif, Network throttling kapatıldı
- **Performans:** Prefetch/Superfetch kapatıldı (SSD için), Fast startup kapatıldı
- **Gizlilik:** Telemetri kapatıldı, Reklam ID devre dışı, Konum servisleri kapatıldı

### Performans Ayarları
- High Performance güç planı aktif
- USB ve PCIe güç yönetimi kapatıldı
- Görsel efektler optimize edildi

### Gizlilik ve Veri Toplama Engelleme
- **Windows Telemetry** kalıcı olarak kapatıldı (Windows'un tekrar açması engellenir)
- **Scheduled Task** ile sürekli kontrol (her 5 dakikada bir)
- **Copilot (Windows 11 25H2)** kapatıldı
- **Widgets** kapatıldı
- **Activity History (Timeline)** kapatıldı
- **App Launch Tracking** kapatıldı
- **Start Menu Suggestions** kapatıldı
- **Windows Spotlight** kapatıldı
- **Windows Update Delivery Optimization (P2P)** kapatıldı
- **Error Reporting** kapatıldı
- **Background Apps Tracking** kapatıldı
- **Tips & Tricks** kapatıldı
- Reklam ID devre dışı
- Cortana kapatıldı
- Konum servisleri kapatıldı

Detaylı liste için: [DEGISIKLIKLER.md](DEGISIKLIKLER.md)

## 🏗️ Mimari

Proje **Senior-Level Event-Driven Architecture** kullanır:

```
core/              # Infrastructure (Events, Config, Logging, DI)
plugins/           # Plugin System (Base, Registry, Loader)
optimizers/        # Optimizer Plugins
services/          # Application Services
application.py     # Main Application
```

### Design Patterns
- **Observer:** EventBus subscribers
- **Strategy:** Optimizer plugins
- **Factory:** Plugin/Service creation
- **Repository:** Backup/Config storage
- **Singleton:** Core services

### Yeni Optimizer Ekleme

```python
from plugins.base import OptimizerPlugin, OptimizationResult, OptimizationStatus
from core.config import Config

class MyOptimizer(OptimizerPlugin):
    def __init__(self):
        super().__init__("MyOptimizer", "Description")
        self.priority = 5
    
    def optimize(self, config: Config) -> OptimizationResult:
        result = OptimizationResult(
            plugin_name=self.name,
            status=OptimizationStatus.RUNNING
        )
        # Your code here
        result.status = OptimizationStatus.SUCCESS
        return result
    
    def can_optimize(self, config: Config) -> bool:
        return True
```

`optimizers/` klasörüne ekleyin, otomatik yüklenecektir!

## 📦 EXE Dosyası Oluşturma

**Tek komutla her şey:**

```powershell
.\build.bat
```

Bu script otomatik olarak:
1. ✅ Python kurulumunu kontrol eder
2. ✅ Gerekli paketleri yükler (yoksa)
3. ✅ PyInstaller'ı yükler (yoksa)
4. ✅ EXE dosyalarını oluşturur
5. ✅ Geçici dosyaları temizler

EXE dosyaları `dist` klasöründe oluşturulur:
- `Windows11Optimizer.exe` (~10-15 MB)
- `Windows11Restore.exe` (~5-10 MB)

**ÖNEMLİ:** EXE dosyalarını da yönetici haklarıyla çalıştırın!

## 🎨 UX İyileştirmeleri

- **Renkli çıktılar:** Başarı (yeşil), hata (kırmızı), uyarı (sarı), bilgi (mavi)
- **İlerleme göstergeleri:** Adım sayısı ve yüzde
- **Animasyonlar:** Yükleme sırasında görsel geri bildirim
- **Açıklayıcı mesajlar:** Her adımda ne yapıldığı belirtiliyor

## 🔧 Sorun Giderme

### "python komutu bulunamadı"
1. Python'u yükleyin: https://www.python.org/downloads/
2. Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin
3. PowerShell'i yeniden başlatın

### "pip komutu bulunamadı"
```powershell
python -m pip install -r requirements.txt
```

### "Permission denied" hatası
PowerShell'i **Yönetici olarak çalıştırın** veya:
```powershell
python -m pip install --user -r requirements.txt
```

### EXE çalışmıyor
- Yönetici haklarıyla çalıştırdığınızdan emin olun
- Windows Defender uyarısı çıkabilir (normaldir, "Yine de çalıştır")

### Restart sonrası değişiklikler geri alındı mı?
Restart sırasında Windows'un loader göstermesi **normaldir**. 

**Kontrol için:**
```powershell
.\check_changes.bat
```

Bu script şunları kontrol eder:
- Telemetri durumu
- Game Mode durumu
- GPU Scheduling durumu
- Servis durumları (DiagTrack, WidgetsService)
- Güç planı
- Copilot (Windows 11 25H2)
- Widgets
- Activity History
- P2P Update Sharing
- Start Menu Suggestions

**Otomatik rapor:**
- Eğer uygulanmayan özellikler varsa, `optimizasyon_raporu.txt` dosyası oluşturulur
- Dosya aynı klasörde bulunur
- İçinde uygulanmayan özelliklerin listesi vardır

**Telemetri için özel çözüm:**
- Optimize script'i otomatik olarak scheduled task oluşturur
- Her 5 dakikada bir telemetriyi kontrol edip kapatır
- Windows'un tekrar açmasını engeller

Eğer bazı ayarlar geri alınmışsa, `Windows11Optimizer.exe` dosyasını tekrar çalıştırabilirsiniz.

## 🛡️ Windows Defender Hakkında

**Atlas OS neden Defender'ı kaldırıyor?**
- Kernel seviyesinde değişiklikler yapması (Defender engelleyebilir)
- Maksimum performans hedefi (%2-5 CPU, ~100-200 MB RAM)
- Oyun odaklı yaklaşım

**Bizim yaklaşımımız:**
- ✅ Defender açık bırakılıyor (güvenlik için)
- ✅ Kernel seviyesinde değişiklik yapmıyoruz
- ✅ Dengeli yaklaşım (oyun + güvenlik)

**Defender'ı kapatmak isterseniz:**
`config.json` dosyasında `security.disable_windows_defender: true` yapın.

Detaylı bilgi için: [DEFENDER_NOTLAR.md](DEFENDER_NOTLAR.md)

## ⚠️ Uyarılar

- Bu script sistem ayarlarını değiştirir
- Kullanmadan önce sistem yedeği alın
- Bazı değişiklikler için sistem yeniden başlatma gerekebilir
- Windows Update bazı ayarları geri alabilir
- Windows Defender'ı kapatırsanız alternatif antivirus kullanın

## 📚 Dokümantasyon

- **DEGISIKLIKLER.md** - Yapılan tüm değişikliklerin detaylı listesi
- **ARCHITECTURE.md** - Mimari dokümantasyonu (detaylı)

## 📝 Lisans

MIT License
