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
        "WindowsMediaPlayer",                # Windows Media Player (isteğe bağlı)
        "Internet-Explorer-Optional-amd64",  # Internet Explorer (kaldırıldı ama bazı sistemlerde kalabilir)
    ]

    # WSL2 kapatma için gerekli opsiyonel özellikler
    WSL_FEATURES = [
        "Microsoft-Windows-Subsystem-Linux",  # WSL
        "VirtualMachinePlatform",             # WSL2 altyapısı
    ]
    
    # Korunacak özellikler (yazılım geliştirme için)
    FEATURES_TO_KEEP = [
        "Microsoft-Hyper-V-All",              # Hyper-V (isteğe bağlı)
        "Containers",                         # Containers
    ]
    
    def __init__(self):
        self.changes = []
        self.features_backup = {}
        # Kullanıcı tercihleri / mod ayarı (optimize.py tarafından set edilebilir)
        self.disable_wsl2: bool = False
    
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
        """Mevcut özellik durumlarını yedekle (sadece dokunabileceğimiz özellikler)"""
        states = {}
        feature_names = sorted(set(self.FEATURES_TO_DISABLE + self.WSL_FEATURES + self.FEATURES_TO_KEEP))
        for feature in feature_names:
            try:
                cmd = f'(Get-WindowsOptionalFeature -Online -FeatureName "{feature}" -ErrorAction SilentlyContinue).State'
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
                    capture_output=True,
                    text=True,
                    timeout=20
                )
                if result.returncode == 0:
                    state = (result.stdout or "").strip()
                    if state:
                        states[feature] = state
            except:
                pass
        return states
    
    def optimize(self):
        """Windows özelliklerini optimize et"""
        changes = []
        
        print("   📋 Windows özellikleri kontrol ediliyor...")

        features = list(self.FEATURES_TO_DISABLE)
        if getattr(self, "disable_wsl2", False):
            features.extend(self.WSL_FEATURES)

        for feature in features:
            if feature in self.FEATURES_TO_KEEP:
                continue  # Korunacak özellikleri atla
            
            try:
                if self.disable_feature(feature):
                    changes.append(f"Özellik devre dışı: {feature}")
                    print(f"      ✅ {feature} devre dışı bırakıldı")
            except Exception as e:
                print(f"      ⚠️  {feature}: {str(e)}")
        
        return changes

