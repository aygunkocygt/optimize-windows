#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Services Optimizer Plugin
Refactored from modules/services.py
"""

import win32serviceutil
import win32service
from typing import Dict, Any, List

from plugins.base import OptimizerPlugin, OptimizationResult, OptimizationStatus
from core.config import Config, ServiceConfig
from core.events import EventBus, Event, EventType, get_event_bus
from datetime import datetime


class ServicesOptimizer(OptimizerPlugin):
    """Windows services optimization plugin"""
    
    SERVICES_TO_DISABLE = [
        "DiagTrack",
        "dmwappushservice",
        "WSearch",
        "XblAuthManager",
        "XblGameSave",
        "XboxGipSvc",
        "XboxNetApiSvc",
        "RetailDemo",
        "RemoteRegistry",
        "RemoteAccess",
        "Spooler",
        "TabletInputService",
        "WbioSrvc",
        "wisvc",
        "WerSvc",
        "WMPNetworkSvc",
        "WpcMonSvc",
        "WpnService",
        "SysMain",
    ]
    
    SERVICES_TO_KEEP = [
        "BITS",
        "wuauserv",
        "WinRM",
        "VSS",
        "EventLog",
        "PlugPlay",
        "RpcSs",
        "Dnscache",
        "Dhcp",
        "lmhosts",
        "nsi",
        "Winmgmt",
        "CryptSvc",
        "DcomLaunch",
        "gpsvc",
        "ProfSvc",
        "SENS",
        "Schedule",
        "Themes",
    ]
    
    def __init__(self, event_bus: EventBus = None):
        super().__init__(
            name="ServicesOptimizer",
            description="Optimizes Windows services by disabling unnecessary ones"
        )
        self.event_bus = event_bus or get_event_bus()
        self.priority = 1  # High priority
        self._backup_data = {}
    
    def optimize(self, config: Config) -> OptimizationResult:
        """Execute services optimization"""
        result = OptimizationResult(
            plugin_name=self.name,
            status=OptimizationStatus.RUNNING
        )
        
        service_config = config.services
        
        if not service_config.disable_telemetry and not service_config.disable_xbox_services:
            result.status = OptimizationStatus.SKIPPED
            result.add_warning("All service optimizations disabled in config")
            return result
        
        try:
            for service in self.SERVICES_TO_DISABLE:
                if service in self.SERVICES_TO_KEEP:
                    continue
                
                # Check if should disable based on config
                if service in ["DiagTrack", "dmwappushservice"] and not service_config.disable_telemetry:
                    continue
                if service.startswith("Xbl") or service.startswith("Xbox") and not service_config.disable_xbox_services:
                    continue
                if service == "WSearch" and not service_config.disable_search:
                    continue
                
                try:
                    if self._disable_service(service):
                        result.add_change({
                            "type": "service_disable",
                            "service": service,
                            "action": "disabled"
                        })
                        
                        # Publish event
                        self.event_bus.publish(Event(
                            event_type=EventType.SERVICE_DISABLED,
                            timestamp=result.timestamp,
                            source=self.name,
                            data={"service": service}
                        ))
                except Exception as e:
                    result.add_error(f"Failed to disable {service}: {str(e)}")
            
            result.status = OptimizationStatus.SUCCESS if not result.has_errors() else OptimizationStatus.PARTIAL
            
        except Exception as e:
            result.status = OptimizationStatus.FAILED
            result.add_error(str(e))
        
        return result
    
    def can_optimize(self, config: Config) -> bool:
        """Check if can optimize with config"""
        return config.services.disable_telemetry or config.services.disable_xbox_services
    
    def backup(self) -> Dict[str, Any]:
        """Backup current service states"""
        backup = {}
        for service in self.SERVICES_TO_DISABLE:
            try:
                status = win32serviceutil.QueryServiceStatus(service)
                backup[service] = {
                    "status": status[1],
                    "start_type": status[4]
                }
            except:
                pass
        self._backup_data = backup
        return backup
    
    def restore(self, backup_data: Dict[str, Any]) -> bool:
        """Restore service states"""
        try:
            for service_name, service_data in backup_data.items():
                start_type = service_data.get("start_type")
                if start_type is not None:
                    win32serviceutil.ChangeServiceConfig(
                        service_name,
                        startType=start_type
                    )
            return True
        except Exception as e:
            return False
    
    def _disable_service(self, service_name: str) -> bool:
        """Disable a service"""
        try:
            # Stop service
            try:
                win32serviceutil.StopService(service_name)
            except:
                pass
            
            # Disable service
            win32serviceutil.ChangeServiceConfig(
                service_name,
                startType=win32service.SERVICE_DISABLED
            )
            return True
        except:
            return False

