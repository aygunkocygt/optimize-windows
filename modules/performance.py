#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performans Optimizasyonları
Oyun ve yazılım geliştirme için performans ayarları
"""

import subprocess
import winreg

class PerformanceOptimizer:
    """Performans optimizasyonu"""
    
    def __init__(self):
        self.changes = []
    
    def set_power_plan(self, plan_name="High performance"):
        """Güç planını ayarla"""
        try:
            # Mevcut planları listele
            cmd = 'powercfg /list'
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True
            )
            
            # High performance planını aktif et
            cmd = 'powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'  # High performance GUID
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.changes.append("Güç planı: High performance")
                return True
        except Exception as e:
            print(f"      ⚠️  Güç planı: {e}")
        return False
    
    def optimize_power_settings(self):
        """Güç ayarlarını optimize et"""
        try:
            # USB selective suspend kapat
            subprocess.run(
                ["powercfg", "/setacvalueindex", "SCHEME_CURRENT", 
                 "2a737441-1930-4402-8d77-b2bebba308a3", 
                 "48e6b7a6-50f5-4782-a5d4-53bb8f07e226", "0"],
                check=False
            )
            
            # PCI Express Link State Power Management kapat
            subprocess.run(
                ["powercfg", "/setacvalueindex", "SCHEME_CURRENT",
                 "501a4d13-42af-4429-9fd1-a8218c268e20",
                 "ee12f906-d277-404b-b6da-e5fa1a576df5", "0"],
                check=False
            )
            
            # Planı aktif et
            subprocess.run(["powercfg", "/setactive", "SCHEME_CURRENT"], check=False)
            
            self.changes.append("Güç ayarları optimize edildi")
            return True
        except Exception as e:
            print(f"      ⚠️  Güç ayarları: {e}")
        return False
    
    def set_visual_effects(self):
        """Görsel efektleri optimize et"""
        try:
            import winreg
            
            # Performans için görsel efektleri ayarla
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects",
                0,
                winreg.KEY_WRITE
            )
            
            # VisualFXSetting = 2 (Best performance)
            winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
            winreg.CloseKey(key)
            
            self.changes.append("Görsel efektler optimize edildi")
            return True
        except Exception as e:
            print(f"      ⚠️  Görsel efektler: {e}")
        return False
    
    def optimize(self):
        """Performans optimizasyonlarını uygula"""
        changes = []
        
        print("   📋 Performans ayarları uygulanıyor...")
        
        # Güç planı
        if self.set_power_plan():
            changes.append("Güç planı: High performance")
            print("      ✅ Güç planı: High performance")
        
        # Güç ayarları
        if self.optimize_power_settings():
            changes.append("Güç ayarları optimize edildi")
            print("      ✅ Güç ayarları optimize edildi")
        
        # Görsel efektler
        if self.set_visual_effects():
            changes.append("Görsel efektler optimize edildi")
            print("      ✅ Görsel efektler optimize edildi")
        
        return changes

