#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telemetry Blocker - Kalıcı Telemetri Engelleme
Windows'un telemetriyi tekrar açmasını engeller
"""

import winreg
import subprocess
import os
from pathlib import Path
from typing import List, Dict


class TelemetryBlocker:
    """
    Telemetry blocker - Windows'un telemetriyi tekrar açmasını engeller
    Birden fazla yöntem kullanarak kalıcı çözüm
    """
    
    # Telemetri kayıt defteri konumları (tüm olası yerler)
    TELEMETRY_REGISTRY_PATHS = [
        # Standart konumlar
        ("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection", "AllowTelemetry"),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry"),
        
        # Ek konumlar
        ("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection", "DoNotShowFeedbackNotifications"),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", "DoNotShowFeedbackNotifications"),
        
        # Windows 11 özel
        ("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection", "MaxTelemetryAllowed"),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", "MaxTelemetryAllowed"),
        
        # User level
        ("HKCU", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Privacy", "TailoredExperiencesWithDiagnosticDataEnabled"),
        ("HKCU", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Privacy", "AllowInputPersonalization"),
    ]
    
    # Telemetri servisleri
    TELEMETRY_SERVICES = [
        "DiagTrack",           # Connected User Experiences and Telemetry
        "dmwappushservice",   # WAP Push Message Routing Service
        "wisvc",              # Windows Insider Service
    ]
    
    def __init__(self):
        self.changes = []
    
    def block_telemetry_registry(self) -> List[str]:
        """Tüm kayıt defteri konumlarında telemetriyi kapat"""
        changes = []
        
        for hkey_name, subkey, value_name in self.TELEMETRY_REGISTRY_PATHS:
            try:
                # HKEY seçimi
                if hkey_name == "HKLM":
                    hkey = winreg.HKEY_LOCAL_MACHINE
                elif hkey_name == "HKCU":
                    hkey = winreg.HKEY_CURRENT_USER
                else:
                    continue
                
                # Anahtarı oluştur veya aç
                try:
                    key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_WRITE)
                except FileNotFoundError:
                    # Anahtar yoksa oluştur
                    key_parts = subkey.split("\\")
                    current_key = hkey
                    for part in key_parts:
                        try:
                            current_key = winreg.OpenKey(current_key, part, 0, winreg.KEY_WRITE)
                        except FileNotFoundError:
                            current_key = winreg.CreateKey(current_key, part)
                    key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_WRITE)
                
                # Değeri ayarla
                if "MaxTelemetryAllowed" in value_name:
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 0)
                elif "Enabled" in value_name or "Allow" in value_name:
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 0)
                else:
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 0)
                
                winreg.CloseKey(key)
                changes.append(f"{hkey_name}\\{subkey}\\{value_name} = 0")
                
            except Exception as e:
                print(f"      ⚠️  {hkey_name}\\{subkey}\\{value_name}: {e}")
        
        return changes
    
    def disable_telemetry_services(self) -> List[str]:
        """Telemetri servislerini kalıcı olarak devre dışı bırak"""
        changes = []
        
        for service in self.TELEMETRY_SERVICES:
            try:
                # Servisi durdur
                subprocess.run(
                    ["sc", "stop", service],
                    capture_output=True,
                    timeout=10,
                    check=False
                )
                
                # Servisi devre dışı bırak
                result = subprocess.run(
                    ["sc", "config", service, "start=", "disabled"],
                    capture_output=True,
                    timeout=10,
                    check=False
                )
                
                if result.returncode == 0:
                    changes.append(f"Servis devre dışı: {service}")
                
            except Exception as e:
                print(f"      ⚠️  {service}: {e}")
        
        return changes
    
    def create_group_policy(self) -> bool:
        """
        Group Policy ile telemetriyi kapat (Pro/Enterprise)
        """
        try:
            # Group Policy kayıt defteri konumu
            gpo_path = r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"
            
            key = winreg.CreateKey(
                winreg.HKEY_LOCAL_MACHINE,
                gpo_path
            )
            
            # Tüm telemetri ayarlarını kapat
            winreg.SetValueEx(key, "AllowTelemetry", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "DoNotShowFeedbackNotifications", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "MaxTelemetryAllowed", 0, winreg.REG_DWORD, 0)
            
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"      ⚠️  Group Policy: {e}")
            return False
    
    def create_scheduled_task(self) -> bool:
        """
        Scheduled Task ile telemetriyi sürekli kontrol et ve kapat
        Windows'un tekrar açmasını engelle
        """
        try:
            script_content = '''@echo off
REM Telemetry Blocker - Sürekli kontrol
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f >nul 2>&1
sc stop DiagTrack >nul 2>&1
sc config DiagTrack start= disabled >nul 2>&1
'''
            
            script_path = Path(os.environ.get('TEMP', 'C:\\Temp')) / 'telemetry_blocker.bat'
            script_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Scheduled task oluştur (her 5 dakikada bir çalışsın)
            task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <TimeTrigger>
      <StartBoundary>2024-01-01T00:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <Repetition>
        <Interval>PT5M</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>"{script_path}"</Command>
    </Exec>
  </Actions>
</Task>'''
            
            xml_path = Path(os.environ.get('TEMP', 'C:\\Temp')) / 'telemetry_blocker_task.xml'
            with open(xml_path, 'w', encoding='utf-16') as f:
                f.write(task_xml)
            
            # Task'ı oluştur
            result = subprocess.run(
                ['schtasks', '/Create', '/TN', 'TelemetryBlocker', '/XML', str(xml_path), '/F'],
                capture_output=True,
                timeout=30,
                check=False
            )
            
            if result.returncode == 0:
                return True
            else:
                # Alternatif: Basit task oluştur
                result = subprocess.run(
                    ['schtasks', '/Create', '/TN', 'TelemetryBlocker', '/TR', f'"{script_path}"', 
                     '/SC', 'MINUTE', '/MO', '5', '/RU', 'SYSTEM', '/F'],
                    capture_output=True,
                    timeout=30,
                    check=False
                )
                return result.returncode == 0
                
        except Exception as e:
            print(f"      ⚠️  Scheduled Task: {e}")
            return False
    
    def block_windows_update_telemetry(self) -> bool:
        """Windows Update'in telemetri ayarlarını değiştirmesini engelle"""
        try:
            # Windows Update telemetri ayarları
            key_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\OSUpgrade",
                r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate",
            ]
            
            for key_path in key_paths:
                try:
                    key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                    winreg.SetValueEx(key, "DisableOSUpgrade", 0, winreg.REG_DWORD, 1)
                    winreg.CloseKey(key)
                except:
                    pass
            
            return True
        except Exception as e:
            print(f"      ⚠️  Windows Update telemetry: {e}")
            return False
    
    def apply_all_blocks(self) -> Dict[str, List[str]]:
        """Tüm telemetri engelleme yöntemlerini uygula"""
        results = {
            "registry": [],
            "services": [],
            "group_policy": False,
            "scheduled_task": False,
            "windows_update": False
        }
        
        # Kayıt defteri
        results["registry"] = self.block_telemetry_registry()
        
        # Servisler
        results["services"] = self.disable_telemetry_services()
        
        # Group Policy
        results["group_policy"] = self.create_group_policy()
        
        # Scheduled Task
        results["scheduled_task"] = self.create_scheduled_task()
        
        # Windows Update
        results["windows_update"] = self.block_windows_update_telemetry()
        
        return results

