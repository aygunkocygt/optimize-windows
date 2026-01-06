#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gizlilik Optimizasyonları
Windows telemetri ve veri toplama özelliklerini kapatır
"""

import subprocess
import winreg

class PrivacyOptimizer:
    """Gizlilik optimizasyonu"""
    
    def __init__(self):
        self.changes = []
    
    def disable_telemetry(self):
        """Telemetriyi kalıcı olarak kapat - Windows'un tekrar açmasını engelle"""
        try:
            import winreg
            import subprocess
            import tempfile
            from pathlib import Path
            
            # Tüm telemetri kayıt defteri konumları
            telemetry_paths = [
                # Standart konumlar
                ("HKLM", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection", "AllowTelemetry"),
                ("HKLM", "SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection", "AllowTelemetry"),
                
                # Ek konumlar (Windows'un tekrar açmasını engellemek için)
                ("HKLM", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection", "DoNotShowFeedbackNotifications"),
                ("HKLM", "SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection", "DoNotShowFeedbackNotifications"),
                ("HKLM", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection", "MaxTelemetryAllowed"),
                ("HKLM", "SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection", "MaxTelemetryAllowed"),
                
                # User level
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Privacy", "TailoredExperiencesWithDiagnosticDataEnabled"),
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Privacy", "AllowInputPersonalization"),
            ]
            
            changes_count = 0
            for hkey_name, key_path, value_name in telemetry_paths:
                try:
                    hkey = winreg.HKEY_LOCAL_MACHINE if hkey_name == "HKLM" else winreg.HKEY_CURRENT_USER
                    
                    # Anahtarı oluştur veya aç
                    try:
                        key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_WRITE)
                    except FileNotFoundError:
                        # Anahtar yoksa oluştur
                        key_parts = key_path.split("\\")
                        current_key = hkey
                        for part in key_parts:
                            try:
                                current_key = winreg.OpenKey(current_key, part, 0, winreg.KEY_WRITE)
                            except FileNotFoundError:
                                current_key = winreg.CreateKey(current_key, part)
                        key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_WRITE)
                    
                    # Değeri ayarla
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(key)
                    changes_count += 1
                except Exception as e:
                    pass  # Bazı konumlar olmayabilir, devam et
            
            # Telemetri servislerini de durdur
            telemetry_services = ["DiagTrack", "dmwappushservice", "wisvc"]
            for service in telemetry_services:
                try:
                    subprocess.run(["sc", "stop", service], capture_output=True, timeout=5, check=False)
                    subprocess.run(["sc", "config", service, "start=", "disabled"], capture_output=True, timeout=5, check=False)
                except:
                    pass
            
            # Scheduled task oluştur (Windows'un tekrar açmasını engellemek için)
            self._setup_telemetry_blocker_task()
            
            self.changes.append(f"Telemetri kalıcı olarak kapatıldı ({changes_count} konum + scheduled task)")
            return True
        except Exception as e:
            print(f"      ⚠️  Telemetri: {e}")
        return False
    
    def _setup_telemetry_blocker_task(self):
        """Telemetri blocker scheduled task oluştur"""
        try:
            import subprocess
            import tempfile
            from pathlib import Path
            
            # Geçici script oluştur
            script_content = '''@echo off
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection" /v MaxTelemetryAllowed /t REG_DWORD /d 0 /f >nul 2>&1
sc stop DiagTrack >nul 2>&1
sc config DiagTrack start= disabled >nul 2>&1
sc stop dmwappushservice >nul 2>&1
sc config dmwappushservice start= disabled >nul 2>&1
'''
            
            script_path = Path(tempfile.gettempdir()) / 'telemetry_blocker.bat'
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Mevcut task'ı kaldır (varsa)
            subprocess.run(['schtasks', '/Delete', '/TN', 'TelemetryBlocker', '/F'], 
                         capture_output=True, timeout=10, check=False)
            
            # Yeni task oluştur (her 5 dakikada bir)
            result = subprocess.run(
                ['schtasks', '/Create', '/TN', 'TelemetryBlocker', '/TR', f'"{script_path}"',
                 '/SC', 'MINUTE', '/MO', '5', '/RU', 'SYSTEM', '/F'],
                capture_output=True,
                timeout=30,
                check=False
            )
            
            return result.returncode == 0
        except:
            return False  # Hata olursa sessizce devam et
    
    def disable_advertising_id(self):
        """Reklam ID'sini kapat"""
        try:
            import winreg
            
            key_paths = [
                "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo",
                "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Privacy",
            ]
            
            for key_path in key_paths:
                try:
                    key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                    winreg.SetValueEx(key, "Enabled", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(key)
                except:
                    pass
            
            self.changes.append("Reklam ID kapatıldı")
            return True
        except Exception as e:
            print(f"      ⚠️  Reklam ID: {e}")
        return False
    
    def disable_location_services(self):
        """Konum servislerini kapat"""
        try:
            import winreg
            
            key = winreg.CreateKey(
                winreg.HKEY_LOCAL_MACHINE,
                "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\location"
            )
            winreg.SetValueEx(key, "Value", 0, winreg.REG_SZ, "Deny")
            winreg.CloseKey(key)
            
            self.changes.append("Konum servisleri kapatıldı")
            return True
        except Exception as e:
            print(f"      ⚠️  Konum servisleri: {e}")
        return False
    
    def disable_cortana(self):
        """Cortana'yı kapat"""
        try:
            import winreg
            
            key = winreg.CreateKey(
                winreg.HKEY_LOCAL_MACHINE,
                "SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search"
            )
            winreg.SetValueEx(key, "AllowCortana", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            
            self.changes.append("Cortana kapatıldı")
            return True
        except Exception as e:
            print(f"      ⚠️  Cortana: {e}")
        return False
    
    def disable_copilot(self):
        """Windows 11 25H2 Copilot'u kapat"""
        try:
            import winreg
            
            # Copilot'u devre dışı bırak
            copilot_paths = [
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "ShowCopilotButton"),
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "CopilotTaskbarIcon"),
                ("HKLM", "SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsCopilot", "TurnOffWindowsCopilot"),
            ]
            
            changes_count = 0
            for hkey_name, key_path, value_name in copilot_paths:
                try:
                    hkey = winreg.HKEY_LOCAL_MACHINE if hkey_name == "HKLM" else winreg.HKEY_CURRENT_USER
                    
                    try:
                        key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_WRITE)
                    except FileNotFoundError:
                        key_parts = key_path.split("\\")
                        current_key = hkey
                        for part in key_parts:
                            try:
                                current_key = winreg.OpenKey(current_key, part, 0, winreg.KEY_WRITE)
                            except FileNotFoundError:
                                current_key = winreg.CreateKey(current_key, part)
                        key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_WRITE)
                    
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(key)
                    changes_count += 1
                except:
                    pass
            
            self.changes.append(f"Copilot kapatıldı ({changes_count} konum)")
            return True
        except Exception as e:
            print(f"      ⚠️  Copilot: {e}")
        return False
    
    def disable_background_data_collection(self):
        """Arka plan veri toplama özelliklerini kapat"""
        try:
            import winreg
            
            # Arka plan veri toplama ayarları
            background_paths = [
                # Activity History (Timeline)
                ("HKLM", "SOFTWARE\\Policies\\Microsoft\\Windows\\System", "EnableActivityFeed"),
                ("HKLM", "SOFTWARE\\Policies\\Microsoft\\Windows\\System", "PublishUserActivities"),
                ("HKLM", "SOFTWARE\\Policies\\Microsoft\\Windows\\System", "UploadUserActivities"),
                
                # App launch tracking
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "Start_TrackProgs"),
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "Start_IrisRecommendations"),
                
                # Start menu suggestions
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager", "SystemPaneSuggestionsEnabled"),
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager", "PreInstalledAppsEnabled"),
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager", "PreInstalledAppsEverEnabled"),
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager", "SubscribedContentEnabled"),
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager", "SubscribedContent-338393Enabled"),
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager", "SubscribedContent-338388Enabled"),
                
                # Windows Spotlight
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager", "RotatingLockScreenEnabled"),
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager", "RotatingLockScreenOverlayEnabled"),
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager", "SoftLandingEnabled"),
                
                # Lock screen suggestions
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager", "SubscribedContent-310093Enabled"),
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager", "SubscribedContent-338389Enabled"),
                
                # Tips & tricks
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\UserProfileEngagement", "ScoobeSystemSettingEnabled"),
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\UserProfileEngagement", "ScoobeSystemSettingEnabled"),
                
                # Background apps
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications", "GlobalUserDisabled"),
                
                # Speech recognition
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Privacy", "AllowInputPersonalization"),
                
                # Inking & typing personalization
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Privacy", "AllowInputPersonalization"),
                
                # Error reporting
                ("HKLM", "SOFTWARE\\Microsoft\\Windows\\Windows Error Reporting", "Disabled"),
                ("HKLM", "SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Error Reporting", "Disabled"),
                
                # Diagnostic data
                ("HKLM", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection", "AllowDeviceNameInTelemetry"),
                ("HKLM", "SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection", "AllowDeviceNameInTelemetry"),
                
                # Windows Update Delivery Optimization (P2P)
                ("HKLM", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\DeliveryOptimization\\Config", "DODownloadMode"),
                ("HKLM", "SOFTWARE\\Policies\\Microsoft\\Windows\\DeliveryOptimization", "DODownloadMode"),
                
                # Widgets (Windows 11)
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "TaskbarDa"),
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "TaskbarMn"),
                
                # Feedback & suggestions
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\UserProfileEngagement", "ScoobeSystemSettingEnabled"),
            ]
            
            changes_count = 0
            for hkey_name, key_path, value_name in background_paths:
                try:
                    hkey = winreg.HKEY_LOCAL_MACHINE if hkey_name == "HKLM" else winreg.HKEY_CURRENT_USER
                    
                    try:
                        key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_WRITE)
                    except FileNotFoundError:
                        key_parts = key_path.split("\\")
                        current_key = hkey
                        for part in key_parts:
                            try:
                                current_key = winreg.OpenKey(current_key, part, 0, winreg.KEY_WRITE)
                            except FileNotFoundError:
                                current_key = winreg.CreateKey(current_key, part)
                        key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_WRITE)
                    
                    # Değer tipine göre ayarla
                    if "DODownloadMode" in value_name:
                        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 0)  # 0 = Disabled
                    elif "Disabled" in value_name or "Enabled" in value_name:
                        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 1 if "Disabled" in value_name else 0)
                    else:
                        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 0)
                    
                    winreg.CloseKey(key)
                    changes_count += 1
                except:
                    pass
            
            self.changes.append(f"Arka plan veri toplama kapatıldı ({changes_count} ayar)")
            return True
        except Exception as e:
            print(f"      ⚠️  Arka plan veri toplama: {e}")
        return False
    
    def disable_widgets(self):
        """Windows 11 Widgets'ı kapat"""
        try:
            import winreg
            import subprocess
            
            # Widgets servisini durdur
            try:
                subprocess.run(["sc", "stop", "WidgetsService"], capture_output=True, timeout=5, check=False)
                subprocess.run(["sc", "config", "WidgetsService", "start=", "disabled"], capture_output=True, timeout=5, check=False)
            except:
                pass
            
            # Widgets kayıt defteri ayarları
            widgets_paths = [
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "TaskbarDa"),
                ("HKCU", "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "TaskbarMn"),
            ]
            
            changes_count = 0
            for hkey_name, key_path, value_name in widgets_paths:
                try:
                    hkey = winreg.HKEY_CURRENT_USER
                    key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_WRITE)
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(key)
                    changes_count += 1
                except:
                    pass
            
            self.changes.append(f"Widgets kapatıldı ({changes_count} ayar)")
            return True
        except Exception as e:
            print(f"      ⚠️  Widgets: {e}")
        return False
    
    def optimize(self):
        """Gizlilik optimizasyonlarını uygula"""
        changes = []
        
        print("   📋 Gizlilik ayarları uygulanıyor...")
        
        if self.disable_telemetry():
            changes.append("Telemetri kapatıldı")
            print("      ✅ Telemetri kapatıldı")
        
        if self.disable_advertising_id():
            changes.append("Reklam ID kapatıldı")
            print("      ✅ Reklam ID kapatıldı")
        
        if self.disable_location_services():
            changes.append("Konum servisleri kapatıldı")
            print("      ✅ Konum servisleri kapatıldı")
        
        if self.disable_cortana():
            changes.append("Cortana kapatıldı")
            print("      ✅ Cortana kapatıldı")
        
        if self.disable_copilot():
            changes.append("Copilot kapatıldı")
            print("      ✅ Copilot (Windows 11 25H2) kapatıldı")
        
        if self.disable_background_data_collection():
            changes.append("Arka plan veri toplama kapatıldı")
            print("      ✅ Arka plan veri toplama özellikleri kapatıldı")
        
        if self.disable_widgets():
            changes.append("Widgets kapatıldı")
            print("      ✅ Widgets kapatıldı")
        
        return changes

