#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows Kayıt Defteri Optimizasyonu
Performans ve gizlilik için kayıt defteri ayarları
"""

# winreg modülü optimize() fonksiyonunda import ediliyor

class RegistryOptimizer:
    """Kayıt defteri optimizasyonu"""
    
    def __init__(self):
        self.changes = []
        self.registry_backup = {}
    
    def set_registry_value(self, key_path, value_name, value_type, value_data):
        """Kayıt defteri değeri ayarla"""
        try:
            import winreg
            
            # HKEY_LOCAL_MACHINE için
            if key_path.startswith("HKLM\\"):
                hkey = winreg.HKEY_LOCAL_MACHINE
                subkey = key_path[5:]  # "HKLM\\" kısmını kaldır
            elif key_path.startswith("HKCU\\"):
                hkey = winreg.HKEY_CURRENT_USER
                subkey = key_path[5:]  # "HKCU\\" kısmını kaldır
            else:
                return False
            
            # Anahtarı aç veya oluştur
            try:
                key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_WRITE)
            except FileNotFoundError:
                # Anahtar yoksa oluştur
                key_parts = subkey.split("\\")
                for i in range(1, len(key_parts) + 1):
                    partial_path = "\\".join(key_parts[:i])
                    try:
                        winreg.OpenKey(hkey, partial_path, 0, winreg.KEY_WRITE)
                    except FileNotFoundError:
                        winreg.CreateKey(hkey, partial_path)
                key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_WRITE)
            
            # Değeri yaz
            winreg.SetValueEx(key, value_name, 0, value_type, value_data)
            winreg.CloseKey(key)
            
            self.changes.append({
                "type": "registry",
                "path": key_path,
                "value": value_name,
                "data": value_data
            })
            return True
        except Exception as e:
            print(f"      ⚠️  {key_path}\\{value_name}: {e}")
            return False
    
    def backup_registry(self):
        """Kayıt defteri değerlerini yedekle"""
        return self.registry_backup
    
    def optimize(self):
        """Kayıt defteri optimizasyonlarını uygula"""
        import winreg
        changes = []
        
        print("   📋 Kayıt defteri ayarları uygulanıyor...")
        
        # Performans optimizasyonları
        optimizations = [
            # Telemetri kapatma (tüm konumlar - Windows'un tekrar açmasını engellemek için)
            ("HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection", 
             "AllowTelemetry", winreg.REG_DWORD, 0),
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection", 
             "AllowTelemetry", winreg.REG_DWORD, 0),
            ("HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection", 
             "MaxTelemetryAllowed", winreg.REG_DWORD, 0),
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection", 
             "MaxTelemetryAllowed", winreg.REG_DWORD, 0),
            ("HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection", 
             "DoNotShowFeedbackNotifications", winreg.REG_DWORD, 1),
            ("HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Privacy", 
             "TailoredExperiencesWithDiagnosticDataEnabled", winreg.REG_DWORD, 0),
            ("HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Privacy", 
             "AllowInputPersonalization", winreg.REG_DWORD, 0),
            
            # Windows Update optimizasyonu
            ("HKLM\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings", 
             "UxOption", winreg.REG_DWORD, 1),
            
            # Windows Update Delivery Optimization (P2P - veri hortumlama)
            ("HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\DeliveryOptimization\\Config", 
             "DODownloadMode", winreg.REG_DWORD, 0),  # 0 = Disabled
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DeliveryOptimization", 
             "DODownloadMode", winreg.REG_DWORD, 0),
            
            # Activity History (Timeline) - veri toplama
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System", 
             "EnableActivityFeed", winreg.REG_DWORD, 0),
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System", 
             "PublishUserActivities", winreg.REG_DWORD, 0),
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System", 
             "UploadUserActivities", winreg.REG_DWORD, 0),
            
            # Game Mode aktif
            ("HKCU\\SOFTWARE\\Microsoft\\GameBar", 
             "AllowAutoGameMode", winreg.REG_DWORD, 1),
            ("HKCU\\SOFTWARE\\Microsoft\\GameBar", 
             "AutoGameModeEnabled", winreg.REG_DWORD, 1),
            
            # GPU performansı
            ("HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers", 
             "HwSchMode", winreg.REG_DWORD, 2),  # GPU Scheduling
            
            # Windows Search optimizasyonu
            ("HKLM\\SYSTEM\\CurrentControlSet\\Services\\WSearch", 
             "Start", winreg.REG_DWORD, 3),  # Manual
            
            # Prefetch optimizasyonu (SSD için)
            ("HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters", 
             "EnableSuperfetch", winreg.REG_DWORD, 0),
            ("HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters", 
             "EnablePrefetcher", winreg.REG_DWORD, 0),
            
            # Gizlilik ayarları
            ("HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo", 
             "Enabled", winreg.REG_DWORD, 0),
            ("HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo", 
             "Enabled", winreg.REG_DWORD, 0),
            
            # Konum servisleri
            ("HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\location", 
             "Value", winreg.REG_SZ, "Deny"),
            
            # Windows Defender real-time protection (isteğe bağlı - yazılım geliştirme için açık bırakılabilir)
            # ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender\\Real-Time Protection", 
            #  "DisableRealtimeMonitoring", winreg.REG_DWORD, 0),  # Açık bırakıyoruz
            
            # Network throttling kapatma (oyun için)
            ("HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile", 
             "NetworkThrottlingIndex", winreg.REG_DWORD, 0xFFFFFFFF),
            
            # Timer resolution (oyun için)
            ("HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\kernel", 
             "GlobalTimerResolutionRequests", winreg.REG_DWORD, 1),
            
            # Windows Update otomatik restart kapatma
            ("HKLM\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings", 
             "UxOption", winreg.REG_DWORD, 1),
            
            # Fast startup kapatma (bazı sorunları önler)
            ("HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power", 
             "HiberbootEnabled", winreg.REG_DWORD, 0),
        ]
        
        for key_path, value_name, value_type, value_data in optimizations:
            try:
                if self.set_registry_value(key_path, value_name, value_type, value_data):
                    changes.append(f"{key_path}\\{value_name} = {value_data}")
                    print(f"      ✅ {key_path}\\{value_name}")
            except Exception as e:
                print(f"      ⚠️  {key_path}\\{value_name}: {e}")
        
        return changes

