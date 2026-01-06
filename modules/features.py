#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows Özellikleri Optimizasyonu
Gereksiz Windows özelliklerini kapatır
"""

import subprocess
import json

class FeaturesOptimizer:
    """Windows özellikleri optimizasyonu"""
    
    # Kapatılacak özellikler
    FEATURES_TO_DISABLE = [
        "MicrosoftWindowsPowerShellV2Root",  # PowerShell 2.0 (eski)
        "WorkFolders-Client",                # Work Folders Client
        "MediaPlayback",                     # Media Features (isteğe bağlı)
    ]
    
    # Korunacak özellikler (yazılım geliştirme için)
    FEATURES_TO_KEEP = [
        "Microsoft-Windows-Subsystem-Linux",  # WSL2
        "Microsoft-Hyper-V-All",              # Hyper-V (isteğe bağlı)
        "Containers",                         # Containers
        "VirtualMachinePlatform",             # Virtual Machine Platform
    ]
    
    def __init__(self):
        self.changes = []
        self.features_backup = {}
    
    def disable_feature(self, feature_name):
        """Windows özelliğini devre dışı bırak"""
        try:
            cmd = f'Disable-WindowsOptionalFeature -Online -FeatureName "{feature_name}" -NoRestart'
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 or "NoRestart" in result.stdout:
                self.changes.append({
                    "type": "feature_disable",
                    "feature": feature_name
                })
                return True
            return False
        except Exception as e:
            print(f"      ⚠️  {feature_name}: {e}")
            return False
    
    def backup_features(self):
        """Mevcut özellik durumlarını yedekle"""
        try:
            cmd = 'Get-WindowsOptionalFeature -Online | ConvertTo-Json'
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                features = json.loads(result.stdout)
                if isinstance(features, dict):
                    features = [features]
                return {f["FeatureName"]: f["State"] for f in features if isinstance(f, dict)}
        except:
            pass
        return {}
    
    def optimize(self):
        """Windows özelliklerini optimize et"""
        changes = []
        
        print("   📋 Windows özellikleri kontrol ediliyor...")
        
        for feature in self.FEATURES_TO_DISABLE:
            if feature in self.FEATURES_TO_KEEP:
                continue  # Korunacak özellikleri atla
            
            try:
                if self.disable_feature(feature):
                    changes.append(f"Özellik devre dışı: {feature}")
                    print(f"      ✅ {feature} devre dışı bırakıldı")
            except Exception as e:
                print(f"      ⚠️  {feature}: {str(e)}")
        
        return changes

