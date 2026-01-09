#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows Servis Optimizasyonu
Gereksiz servisleri kapatır, yazılım geliştirme için gerekli olanları korur
"""

import win32serviceutil
import win32service
import win32con
import subprocess

class ServiceOptimizer:
    """Windows servis optimizasyonu"""
    
    # Kapatılacak servisler (telemetri ve gereksiz servisler)
    SERVICES_TO_DISABLE = [
        "DiagTrack",                    # Connected User Experiences and Telemetry
        "dmwappushservice",             # WAP Push Message Routing Service
        "WSearch",                      # Windows Search (isteğe bağlı)
        "XblAuthManager",               # Xbox Live Auth Manager
        "XblGameSave",                  # Xbox Live Game Save
        "XboxGipSvc",                   # Xbox Accessory Management Service
        "XboxNetApiSvc",                # Xbox Live Networking Service
        "RetailDemo",                   # Retail Demo Service
        "RemoteRegistry",               # Remote Registry
        "RemoteAccess",                 # Routing and Remote Access
        "Spooler",                      # Print Spooler (yazıcı kullanmıyorsanız)
        "TabletInputService",           # Touch Keyboard and Handwriting Panel Service
        "WbioSrvc",                     # Windows Biometric Service
        "wisvc",                        # Windows Insider Service
        "WerSvc",                       # Windows Error Reporting Service
        "WMPNetworkSvc",                # Windows Media Player Network Sharing Service
        "WpcMonSvc",                    # Parental Controls
        "WpnService",                   # Windows Push Notifications Service
        "SysMain",                      # SysMain (Superfetch) - SSD için gereksiz
        "WidgetsService",               # Windows 11 Widgets Service
        "OneSyncSvc",                   # OneDrive Sync Service (isteğe bağlı)
        "WaaSMedicSvc",                 # Windows Update Medic Service (güncelleme için gerekli ama veri toplar)
        "PcaSvc",                       # Program Compatibility Assistant Service
        "TrkWks",                       # Distributed Link Tracking Client
        "Browser",                       # Computer Browser (eski ağ özelliği)
    ]

    # "Servis trimming" (daha agresif, opsiyonel) - bazı özellikleri etkileyebilir
    # Bu liste optimize.py tarafında kullanıcı onayıyla devreye alınır.
    TRIM_SERVICES_TO_DISABLE = [
        "Fax",                           # Fax
        "lfsvc",                         # Geolocation Service
        "MapsBroker",                    # Downloaded Maps Manager
        "SharedAccess",                  # Internet Connection Sharing (ICS)
        "diagnosticshub.standardcollector.service",  # Diagnostic Hub Standard Collector
        "Wecsvc",                        # Windows Event Collector (kurumsal/forwarding yoksa)
    ]
    
    # Korunacak servisler (yazılım geliştirme için gerekli)
    SERVICES_TO_KEEP = [
        "BITS",                         # Background Intelligent Transfer Service
        "wuauserv",                     # Windows Update
        "WinRM",                        # Windows Remote Management
        "VSS",                          # Volume Shadow Copy
        "EventLog",                     # Windows Event Log
        "PlugPlay",                     # Plug and Play
        "RpcSs",                        # Remote Procedure Call
        "Dnscache",                     # DNS Client
        "Dhcp",                         # DHCP Client
        "lmhosts",                      # TCP/IP NetBIOS Helper
        "nsi",                          # Network Store Interface Service
        "Winmgmt",                      # Windows Management Instrumentation
        "CryptSvc",                     # Cryptographic Services
        "DcomLaunch",                   # DCOM Server Process Launcher
        "gpsvc",                        # Group Policy Client
        "ProfSvc",                      # User Profile Service
        "SENS",                         # System Event Notification Service
        "Schedule",                     # Task Scheduler
        "Themes",                       # Themes (bazı uygulamalar için gerekli)
    ]
    
    def __init__(self):
        self.changes = []
        self.aggressive_trim = False
    
    def get_service_status(self, service_name):
        """Servis durumunu kontrol et"""
        try:
            status = win32serviceutil.QueryServiceStatus(service_name)[1]
            return status == win32service.SERVICE_RUNNING
        except:
            return None
    
    def disable_service(self, service_name):
        """Servisi devre dışı bırak"""
        try:
            # Servis durumunu kontrol et
            current_status = self.get_service_status(service_name)
            if current_status is None:
                return False
            
            # Servisi durdur
            try:
                win32serviceutil.StopService(service_name)
            except:
                pass  # Zaten durmuş olabilir
            
            # Servisi devre dışı bırak
            win32serviceutil.ChangeServiceConfig(
                service_name,
                startType=win32service.SERVICE_DISABLED
            )
            
            self.changes.append({
                "type": "service_disable",
                "service": service_name,
                "action": "disabled"
            })
            return True
        except Exception as e:
            print(f"      ⚠️  {service_name}: {e}")
            return False
    
    def backup_services(self):
        """Mevcut servis durumlarını yedekle"""
        backup = {}
        for service in self.SERVICES_TO_DISABLE:
            try:
                # QueryServiceStatus() tuple yapısı:
                # (ServiceType, CurrentState, ControlsAccepted, Win32ExitCode, ServiceSpecificExitCode, CheckPoint, WaitHint)
                status = win32serviceutil.QueryServiceStatus(service)

                # StartType için QueryServiceConfig gerekir (QueryServiceStatus içinde yok).
                # win32serviceutil.QueryServiceConfig bazı ortamlarda yok/erişilemez olabiliyor,
                # bu yüzden Win32 Service API ile doğrudan okuyoruz.
                start_type = None
                try:
                    scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_CONNECT)
                    try:
                        svc = win32service.OpenService(scm, service, win32service.SERVICE_QUERY_CONFIG)
                        try:
                            cfg = win32service.QueryServiceConfig(svc)
                            # (ServiceType, StartType, ErrorControl, BinaryPathName, ...)
                            start_type = cfg[1]
                        finally:
                            win32service.CloseServiceHandle(svc)
                    finally:
                        win32service.CloseServiceHandle(scm)
                except Exception:
                    # Fallback: sc qc parse
                    try:
                        result = subprocess.run(["sc", "qc", service], capture_output=True, text=True, timeout=10)
                        out = (result.stdout or "")
                        for line in out.splitlines():
                            if "START_TYPE" in line:
                                # örn: "        START_TYPE         : 2   AUTO_START"
                                parts = line.split(":")
                                if len(parts) >= 2:
                                    right = parts[1].strip()
                                    num = right.split()[0].strip()
                                    if num.isdigit():
                                        start_type = int(num)
                                break
                    except Exception:
                        start_type = None
                backup[service] = {
                    "status": status[1],
                    "start_type": start_type
                }
            except:
                pass
        return backup
    
    def optimize(self):
        """Servis optimizasyonlarını uygula"""
        changes = []
        
        print("   📋 Servisler kontrol ediliyor...")
        
        services = list(self.SERVICES_TO_DISABLE)
        if getattr(self, "aggressive_trim", False):
            services.extend(self.TRIM_SERVICES_TO_DISABLE)

        for service in services:
            if service in self.SERVICES_TO_KEEP:
                continue  # Korunacak servisleri atla
            
            try:
                if self.disable_service(service):
                    changes.append(f"Servis devre dışı: {service}")
                    print(f"      ✅ {service} devre dışı bırakıldı")
            except Exception as e:
                print(f"      ⚠️  {service}: {str(e)}")
        
        return changes

