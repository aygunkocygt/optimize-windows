#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows Uygulamaları Kaldırma/Kapatma
Gereksiz Microsoft uygulamalarını kaldırır veya devre dışı bırakır
"""

import subprocess
import winreg
import json
from typing import List, Dict


class AppsRemover:
    """Windows uygulamalarını kaldırma/kapatma"""
    
    # Kaldırılacak/kapatılacak uygulamalar (Package Name)
    APPS_TO_REMOVE = [
        # Phone Link ve ilgili uygulamalar
        "Microsoft.YourPhone",                    # Phone Link
        "Microsoft.Phone",                        # Phone (eski)
        
        # Xbox uygulamaları
        "Microsoft.XboxApp",                      # Xbox App
        "Microsoft.XboxGameOverlay",              # Xbox Game Bar
        "Microsoft.XboxGamingOverlay",            # Xbox Gaming Overlay
        "Microsoft.XboxIdentityProvider",        # Xbox Identity Provider
        "Microsoft.XboxSpeechToTextOverlay",      # Xbox Speech to Text
        
        # Gereksiz Microsoft uygulamaları
        "Microsoft.GetHelp",                      # Get Help
        "Microsoft.Getstarted",                   # Get Started
        "Microsoft.Microsoft3DViewer",           # 3D Viewer
        "Microsoft.MicrosoftOfficeHub",          # Office Hub
        "Microsoft.MicrosoftSolitaireCollection", # Solitaire Collection
        "Microsoft.MixedReality.Portal",         # Mixed Reality Portal
        "Microsoft.People",                      # People
        "Microsoft.SkypeApp",                    # Skype
        "Microsoft.StorePurchaseApp",             # Store Purchase App
        "Microsoft.Todos",                       # Microsoft To Do
        "Microsoft.Wallet",                      # Wallet
        "Microsoft.WindowsAlarms",               # Alarms & Clock
        "Microsoft.WindowsCamera",               # Camera
        "Microsoft.WindowsFeedbackHub",          # Feedback Hub
        "Microsoft.WindowsMaps",                 # Maps
        "Microsoft.WindowsSoundRecorder",        # Voice Recorder
        "Microsoft.Xbox.TCUI",                   # Xbox TCUI
        "Microsoft.ZuneMusic",                   # Groove Music
        "Microsoft.ZuneVideo",                   # Movies & TV
        
        # Bing ve Cortana
        "Microsoft.BingNews",                    # Bing News
        "Microsoft.BingWeather",                 # Bing Weather
        "Microsoft.BingFinance",                 # Bing Finance
        "Microsoft.BingSports",                 # Bing Sports
        "Microsoft.BingTravel",                 # Bing Travel
        
        # Diğer gereksiz uygulamalar
        "Microsoft.Windows.Photos",               # Photos (isteğe bağlı)
        "Microsoft.WindowsCalculator",           # Calculator (isteğe bağlı - yazılım geliştirme için gerekli olabilir)
        "Microsoft.WindowsStore",                # Microsoft Store (isteğe bağlı - yazılım geliştirme için gerekli olabilir)
    ]
    
    # Korunacak uygulamalar (yazılım geliştirme için gerekli)
    APPS_TO_KEEP = [
        "Microsoft.WindowsStore",                # Microsoft Store (gerekli olabilir)
        "Microsoft.WindowsCalculator",           # Calculator (gerekli olabilir)
        "Microsoft.WindowsTerminal",            # Windows Terminal
        "Microsoft.VisualStudioCode",            # VS Code (eğer yüklüyse)
    ]
    
    def __init__(self):
        self.changes = []
        self.apps_backup = {}
    
    def remove_app(self, app_name: str) -> bool:
        """Uygulamayı kaldır"""
        try:
            # PowerShell komutu ile uygulamayı kaldır
            cmd = f'Get-AppxPackage -Name "{app_name}" | Remove-AppxPackage -ErrorAction SilentlyContinue'
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Başarılı olup olmadığını kontrol et
            if result.returncode == 0 or "Remove-AppxPackage" in result.stdout:
                self.changes.append({
                    "type": "app_remove",
                    "app": app_name,
                    "action": "removed"
                })
                return True
            return False
        except Exception as e:
            print(f"      ⚠️  {app_name}: {e}")
            return False
    
    def disable_app(self, app_name: str) -> bool:
        """Uygulamayı devre dışı bırak (kaldırmadan)"""
        try:
            # PowerShell komutu ile uygulamayı devre dışı bırak
            cmd = f'Get-AppxPackage -Name "{app_name}" | Set-AppxPackage -DisableDevelopmentMode -ErrorAction SilentlyContinue'
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Alternatif: Kayıt defteri ile devre dışı bırak
            try:
                key = winreg.CreateKey(
                    winreg.HKEY_CURRENT_USER,
                    f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Appx\\AppxAllUserStore\\Deprovisioned\\{app_name}"
                )
                winreg.SetValueEx(key, "Disabled", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)
            except:
                pass
            
            self.changes.append({
                "type": "app_disable",
                "app": app_name,
                "action": "disabled"
            })
            return True
        except Exception as e:
            print(f"      ⚠️  {app_name}: {e}")
            return False
    
    def backup_apps(self) -> Dict[str, str]:
        """Mevcut uygulamaları yedekle"""
        try:
            cmd = 'Get-AppxPackage | Select-Object Name, PackageFullName | ConvertTo-Json'
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                apps = json.loads(result.stdout)
                if isinstance(apps, dict):
                    apps = [apps]
                return {app["Name"]: app["PackageFullName"] for app in apps if isinstance(app, dict)}
        except:
            pass
        return {}
    
    def optimize(self, remove_mode: bool = True) -> List[str]:
        """
        Uygulamaları optimize et
        
        Args:
            remove_mode: True ise kaldır, False ise sadece devre dışı bırak
        """
        changes = []
        
        print("   📋 Gereksiz uygulamalar kontrol ediliyor...")
        
        # Yedekle
        self.apps_backup = self.backup_apps()
        
        for app in self.APPS_TO_REMOVE:
            if app in self.APPS_TO_KEEP:
                continue  # Korunacak uygulamaları atla
            
            try:
                # Uygulamanın yüklü olup olmadığını kontrol et
                check_cmd = f'Get-AppxPackage -Name "{app}" -ErrorAction SilentlyContinue'
                check_result = subprocess.run(
                    ["powershell", "-Command", check_cmd],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if check_result.returncode == 0 and app in check_result.stdout:
                    # Uygulama yüklü, kaldır veya devre dışı bırak
                    if remove_mode:
                        if self.remove_app(app):
                            changes.append(f"Uygulama kaldırıldı: {app}")
                            print(f"      ✅ {app} kaldırıldı")
                    else:
                        if self.disable_app(app):
                            changes.append(f"Uygulama devre dışı: {app}")
                            print(f"      ✅ {app} devre dışı bırakıldı")
            except Exception as e:
                print(f"      ⚠️  {app}: {str(e)}")
        
        return changes

