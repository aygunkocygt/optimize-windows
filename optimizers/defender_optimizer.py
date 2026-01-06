#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows Defender Optimizer Plugin
İsteğe bağlı: Defender'ı kapatma veya optimize etme
"""

import subprocess
import winreg
from typing import Dict, Any

from plugins.base import OptimizerPlugin, OptimizationResult, OptimizationStatus
from core.config import Config, SecurityConfig
from core.events import EventBus, Event, EventType, get_event_bus
from datetime import datetime


class DefenderOptimizer(OptimizerPlugin):
    """Windows Defender optimization plugin"""
    
    def __init__(self, event_bus: EventBus = None):
        super().__init__(
            name="DefenderOptimizer",
            description="Windows Defender optimizasyonu (isteğe bağlı)"
        )
        self.event_bus = event_bus or get_event_bus()
        self.priority = 10  # Düşük öncelik (son çalışsın)
    
    def optimize(self, config: Config) -> OptimizationResult:
        """Execute Defender optimization"""
        result = OptimizationResult(
            plugin_name=self.name,
            status=OptimizationStatus.RUNNING
        )
        
        security_config = config.security
        
        # Defender kapatma istenmiyorsa atla
        if not security_config.disable_windows_defender and not security_config.disable_defender_realtime:
            result.status = OptimizationStatus.SKIPPED
            result.add_warning("Windows Defender optimizasyonları devre dışı (güvenlik için açık bırakılıyor)")
            return result
        
        try:
            # Real-time protection kapat
            if security_config.disable_defender_realtime:
                self._disable_realtime_protection(result)
            
            # Defender servislerini durdur
            if security_config.disable_windows_defender:
                self._disable_defender_services(result)
            
            # Cloud protection kapat
            if security_config.disable_defender_cloud:
                self._disable_cloud_protection(result)
            
            result.status = OptimizationStatus.SUCCESS if not result.has_errors() else OptimizationStatus.PARTIAL
            
        except Exception as e:
            result.status = OptimizationStatus.FAILED
            result.add_error(str(e))
        
        return result
    
    def can_optimize(self, config: Config) -> bool:
        """Check if can optimize with config"""
        return config.security.disable_windows_defender or config.security.disable_defender_realtime
    
    def backup(self) -> Dict[str, Any]:
        """Backup current Defender settings"""
        backup = {}
        
        # Real-time protection durumu
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                "SOFTWARE\\Policies\\Microsoft\\Windows Defender\\Real-Time Protection",
                0,
                winreg.KEY_READ
            )
            backup["realtime_monitoring"] = winreg.QueryValueEx(key, "DisableRealtimeMonitoring")[0]
            winreg.CloseKey(key)
        except:
            backup["realtime_monitoring"] = None
        
        # Servis durumları
        services = ["WinDefend", "WdNisSvc", "Sense"]
        backup["services"] = {}
        for service in services:
            try:
                result = subprocess.run(
                    ["sc", "query", service],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if "STOPPED" in result.stdout:
                    backup["services"][service] = "STOPPED"
                elif "RUNNING" in result.stdout:
                    backup["services"][service] = "RUNNING"
            except:
                pass
        
        return backup
    
    def restore(self, backup_data: Dict[str, Any]) -> bool:
        """Restore Defender settings"""
        try:
            # Real-time protection geri yükle
            if "realtime_monitoring" in backup_data and backup_data["realtime_monitoring"] is not None:
                key = winreg.CreateKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    "SOFTWARE\\Policies\\Microsoft\\Windows Defender\\Real-Time Protection"
                )
                winreg.SetValueEx(
                    key,
                    "DisableRealtimeMonitoring",
                    0,
                    winreg.REG_DWORD,
                    backup_data["realtime_monitoring"]
                )
                winreg.CloseKey(key)
            
            # Servisleri geri yükle
            if "services" in backup_data:
                for service_name, state in backup_data["services"].items():
                    if state == "RUNNING":
                        subprocess.run(["sc", "start", service_name], check=False)
                    elif state == "STOPPED":
                        subprocess.run(["sc", "stop", service_name], check=False)
            
            return True
        except Exception as e:
            return False
    
    def _disable_realtime_protection(self, result: OptimizationResult) -> None:
        """Disable real-time protection"""
        try:
            key = winreg.CreateKey(
                winreg.HKEY_LOCAL_MACHINE,
                "SOFTWARE\\Policies\\Microsoft\\Windows Defender\\Real-Time Protection"
            )
            winreg.SetValueEx(key, "DisableRealtimeMonitoring", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            
            result.add_change({
                "type": "defender_realtime",
                "action": "disabled"
            })
            
            self.event_bus.publish(Event(
                event_type=EventType.REGISTRY_CHANGED,
                timestamp=datetime.now(),
                source=self.name,
                data={"setting": "Defender Real-Time Protection", "action": "disabled"}
            ))
        except Exception as e:
            result.add_error(f"Real-time protection kapatılamadı: {str(e)}")
    
    def _disable_defender_services(self, result: OptimizationResult) -> None:
        """Disable Defender services"""
        services = ["WinDefend", "WdNisSvc", "Sense"]
        
        for service in services:
            try:
                # Servisi durdur
                subprocess.run(["sc", "stop", service], check=False, timeout=10)
                # Servisi devre dışı bırak
                subprocess.run(["sc", "config", service, "start=", "disabled"], check=False)
                
                result.add_change({
                    "type": "defender_service",
                    "service": service,
                    "action": "disabled"
                })
            except Exception as e:
                result.add_error(f"{service} servisi kapatılamadı: {str(e)}")
    
    def _disable_cloud_protection(self, result: OptimizationResult) -> None:
        """Disable cloud protection"""
        try:
            key = winreg.CreateKey(
                winreg.HKEY_LOCAL_MACHINE,
                "SOFTWARE\\Policies\\Microsoft\\Windows Defender"
            )
            winreg.SetValueEx(key, "DisableRealtimeMonitoring", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "DisableIOAVProtection", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            
            result.add_change({
                "type": "defender_cloud",
                "action": "disabled"
            })
        except Exception as e:
            result.add_error(f"Cloud protection kapatılamadı: {str(e)}")

