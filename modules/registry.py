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
        # Opt-in flags (optimize.py tarafında set edilebilir)
        self.apply_scheduler_tweaks = False

    def _get_optimizations(self, include_scheduler: bool):
        """Uygulanacak registry değişikliklerini tek yerden üret (backup/restore için)"""
        import winreg

        base = [
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

            # Windows Update UX
            ("HKLM\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings",
             "UxOption", winreg.REG_DWORD, 1),

            # Windows Update Delivery Optimization (P2P - veri hortumlama)
            ("HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\DeliveryOptimization\\Config",
             "DODownloadMode", winreg.REG_DWORD, 0),
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DeliveryOptimization",
             "DODownloadMode", winreg.REG_DWORD, 0),

            # Activity History (Timeline)
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System",
             "EnableActivityFeed", winreg.REG_DWORD, 0),
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System",
             "PublishUserActivities", winreg.REG_DWORD, 0),
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System",
             "UploadUserActivities", winreg.REG_DWORD, 0),

            # Game Mode
            ("HKCU\\SOFTWARE\\Microsoft\\GameBar",
             "AllowAutoGameMode", winreg.REG_DWORD, 1),
            ("HKCU\\SOFTWARE\\Microsoft\\GameBar",
             "AutoGameModeEnabled", winreg.REG_DWORD, 1),

            # GPU Scheduling
            ("HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers",
             "HwSchMode", winreg.REG_DWORD, 2),

            # Windows Search start type (manual)
            ("HKLM\\SYSTEM\\CurrentControlSet\\Services\\WSearch",
             "Start", winreg.REG_DWORD, 3),

            # Prefetch (SSD için)
            ("HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters",
             "EnableSuperfetch", winreg.REG_DWORD, 0),
            ("HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters",
             "EnablePrefetcher", winreg.REG_DWORD, 0),

            # Advertising ID
            ("HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo",
             "Enabled", winreg.REG_DWORD, 0),
            ("HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo",
             "Enabled", winreg.REG_DWORD, 0),

            # Location consent
            ("HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\location",
             "Value", winreg.REG_SZ, "Deny"),

            # Network throttling kapatma (oyun)
            ("HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile",
             "NetworkThrottlingIndex", winreg.REG_DWORD, 0xFFFFFFFF),

            # Timer resolution requests
            ("HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\kernel",
             "GlobalTimerResolutionRequests", winreg.REG_DWORD, 1),

            # Fast startup kapatma
            ("HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power",
             "HiberbootEnabled", winreg.REG_DWORD, 0),

            # GameDVR/Capture kapatma (clip kullanmıyorsanız)
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\GameDVR",
             "AllowGameDVR", winreg.REG_DWORD, 0),
            ("HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\GameDVR",
             "AppCaptureEnabled", winreg.REG_DWORD, 0),
            ("HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\GameDVR",
             "AudioCaptureEnabled", winreg.REG_DWORD, 0),
            ("HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\GameDVR",
             "CursorCaptureEnabled", winreg.REG_DWORD, 0),
            ("HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\GameDVR",
             "HistoricalCaptureEnabled", winreg.REG_DWORD, 0),
            ("HKCU\\SYSTEM\\GameConfigStore",
             "GameDVR_Enabled", winreg.REG_DWORD, 0),

            # Background apps policy
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\AppPrivacy",
             "LetAppsRunInBackground", winreg.REG_DWORD, 2),

            # OneDrive sync kapatma (policy)
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\OneDrive",
             "DisableFileSyncNGSC", winreg.REG_DWORD, 1),

            # Xbox Game Bar UI/overlay disable (kayıt/clip kullanılmıyorsa)
            ("HKCU\\SOFTWARE\\Microsoft\\GameBar",
             "ShowStartupPanel", winreg.REG_DWORD, 0),
            ("HKCU\\SOFTWARE\\Microsoft\\GameBar",
             "UseNexusForGameBarEnabled", winreg.REG_DWORD, 0),
            ("HKCU\\SOFTWARE\\Microsoft\\GameBar",
             "GamePanelStartupTipIndex", winreg.REG_DWORD, 3),

            # Bildirim/toast kapatma (agresif)
            ("HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\PushNotifications",
             "ToastEnabled", winreg.REG_DWORD, 0),

            # Focus Assist (Quiet Hours) - agresif şekilde kapalı/otomatik sessiz mod
            ("HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings",
             "NOC_GLOBAL_SETTING_TOASTS_ENABLED", winreg.REG_DWORD, 0),

            # UI: transparanlık/animasyon kapatma
            ("HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
             "EnableTransparency", winreg.REG_DWORD, 0),
            ("HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
             "TaskbarAnimations", winreg.REG_DWORD, 0),

            # Search: web/bing arama kapatma (arka plan/network azaltır)
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search",
             "DisableWebSearch", winreg.REG_DWORD, 1),
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search",
             "ConnectedSearchUseWeb", winreg.REG_DWORD, 0),
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search",
             "ConnectedSearchPrivacy", winreg.REG_DWORD, 3),
            ("HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Search",
             "BingSearchEnabled", winreg.REG_DWORD, 0),
        ]

        if not include_scheduler:
            return base

        scheduler = [
            ("HKLM\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl",
             "Win32PrioritySeparation", winreg.REG_DWORD, 0x26),
            ("HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile",
             "SystemResponsiveness", winreg.REG_DWORD, 10),
            ("HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games",
             "Scheduling Category", winreg.REG_SZ, "High"),
            ("HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games",
             "SFIO Priority", winreg.REG_SZ, "High"),
            ("HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games",
             "Priority", winreg.REG_DWORD, 6),
            ("HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games",
             "GPU Priority", winreg.REG_DWORD, 8),
        ]
        return base + scheduler

    def _read_registry_value(self, key_path: str, value_name: str):
        """Mevcut değeri oku. (exists, type, data) döndürür."""
        import winreg
        if key_path.startswith("HKLM\\"):
            hkey = winreg.HKEY_LOCAL_MACHINE
            subkey = key_path[5:]
        elif key_path.startswith("HKCU\\"):
            hkey = winreg.HKEY_CURRENT_USER
            subkey = key_path[5:]
        else:
            return (False, None, None)
        try:
            key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ)
            data, vtype = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return (True, vtype, data)
        except FileNotFoundError:
            return (False, None, None)
        except OSError:
            return (False, None, None)
    
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
        # Scheduler flag'inden bağımsız olarak tüm olası dokunacağımız değerleri yedekle
        backup_items = []
        for key_path, value_name, _value_type, _value_data in self._get_optimizations(include_scheduler=True):
            exists, vtype, data = self._read_registry_value(key_path, value_name)
            backup_items.append({
                "path": key_path,
                "value": value_name,
                "exists": bool(exists),
                "type": int(vtype) if vtype is not None else None,
                "data": data if exists else None,
            })
        self.registry_backup = {
            "items": backup_items
        }
        return self.registry_backup
    
    def optimize(self):
        """Kayıt defteri optimizasyonlarını uygula"""
        import winreg
        changes = []
        
        print("   📋 Kayıt defteri ayarları uygulanıyor...")
        optimizations = self._get_optimizations(include_scheduler=bool(self.apply_scheduler_tweaks))
        
        for key_path, value_name, value_type, value_data in optimizations:
            try:
                if self.set_registry_value(key_path, value_name, value_type, value_data):
                    changes.append(f"{key_path}\\{value_name} = {value_data}")
                    print(f"      ✅ {key_path}\\{value_name}")
            except Exception as e:
                print(f"      ⚠️  {key_path}\\{value_name}: {e}")
        
        return changes

