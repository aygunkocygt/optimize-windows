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
        """Telemetriyi kapat"""
        try:
            import winreg
            
            # Telemetri seviyesini 0 yap (Security)
            key_paths = [
                "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection",
                "SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection",
            ]
            
            for key_path in key_paths:
                try:
                    key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                    winreg.SetValueEx(key, "AllowTelemetry", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(key)
                except:
                    pass
            
            self.changes.append("Telemetri kapatıldı")
            return True
        except Exception as e:
            print(f"      ⚠️  Telemetri: {e}")
        return False
    
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
        
        return changes

