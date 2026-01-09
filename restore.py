#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows Optimizer - Restore Script
Yedeklenen ayarları geri yükler
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Yönetici hakları kontrolü
def is_admin():
    """Yönetici hakları kontrolü"""
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

# UI modülünü import et (yönetici kontrolünden önce)
try:
    from modules.ui import UI
except ImportError:
    # Fallback için basit print fonksiyonları
    class UI:
        @staticmethod
        def print_error(msg): print(f"❌ {msg}")
        @staticmethod
        def print_warning(msg): print(f"⚠️  {msg}")
        @staticmethod
        def print_info(msg): print(f"ℹ️  {msg}")
        @staticmethod
        def print_success(msg): print(f"✅ {msg}")
        @staticmethod
        def wait_for_key(msg=""): input(msg)

if not is_admin():
    UI.print_error("Bu script yönetici haklarıyla çalıştırılmalıdır!")
    UI.print_warning("Lütfen PowerShell veya CMD'yi 'Yönetici olarak çalıştır' ile açın.")
    UI.wait_for_key()
    sys.exit(1)

import win32serviceutil
import win32service
import winreg


def _set_run_value(hive_name: str, path: str, name: str, value: str) -> bool:
    try:
        root = winreg.HKEY_CURRENT_USER if hive_name == "HKCU" else winreg.HKEY_LOCAL_MACHINE
        key = winreg.CreateKey(root, path)
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def restore_startup_tasks(backup_data):
    """Startup girdileri ve scheduled task'ları geri yükle"""
    data = backup_data.get("startup_tasks") if isinstance(backup_data, dict) else None
    if not data:
        UI.print_info("Startup/Task yedeği bulunamadı (atlandı).")
        return

    # Startup entries
    startup_entries = data.get("startup_entries") or []
    if startup_entries:
        UI.print_info("Startup girdileri geri yükleniyor...")
        restored = 0
        for entry in startup_entries:
            hive = entry.get("hive")
            path = entry.get("path")
            name = entry.get("name")
            value = entry.get("value")
            if hive and path and name and isinstance(value, str):
                if _set_run_value(hive, path, name, value):
                    restored += 1
        UI.print_success(f"Startup girdileri geri yüklendi: {restored}/{len(startup_entries)}")

    # Scheduled tasks
    tasks = data.get("scheduled_tasks") or []
    if tasks:
        UI.print_info("Scheduled task'lar geri yükleniyor (enable)...")
        restored = 0
        total = len(tasks)
        for t in tasks:
            task_name = t.get("task_name")
            task_path = t.get("task_path")
            prev_state_val = t.get("state")
            prev_state = (prev_state_val if isinstance(prev_state_val, str) else str(prev_state_val or "")).strip().lower()
            # Daha önce Disabled değilse enable et
            # Not: State enum 1 = Disabled olabilir (bazı sistemler numeric döndürüyor)
            if task_name and task_path and prev_state not in ("disabled", "1"):
                try:
                    cmd = f'Enable-ScheduledTask -TaskName "{task_name}" -TaskPath "{task_path}" | Out-Null'
                    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
                                   capture_output=True, text=True, timeout=30, check=False)
                    restored += 1
                except Exception:
                    pass
        UI.print_success(f"Task geri yüklendi: {restored}/{total}")

def restore_services(backup_data):
    """Servisleri geri yükle"""
    UI.print_info("Servisler geri yükleniyor...")
    
    if "services" not in backup_data:
        UI.print_warning("Yedek dosyasında servis bilgisi bulunamadı.")
        return
    
    services = backup_data["services"]
    total = len(services)
    restored = 0
    
    for idx, (service_name, service_data) in enumerate(services.items(), 1):
        try:
            status = service_data.get("status")
            start_type = service_data.get("start_type")
            
            if start_type is not None:
                win32serviceutil.ChangeServiceConfig(
                    service_name,
                    startType=start_type
                )
                UI.print_success(f"{service_name} geri yüklendi ({idx}/{total})")
                restored += 1
            UI.print_progress_bar(idx, total)
        except Exception as e:
            UI.print_error(f"{service_name}: {e}")
    
    UI.print_success(f"{restored}/{total} servis başarıyla geri yüklendi.")

def restore_registry(backup_data):
    """Kayıt defterini geri yükle"""
    UI.print_info("Kayıt defteri geri yükleniyor...")
    data = backup_data.get("registry") if isinstance(backup_data, dict) else None
    if not data or not isinstance(data, dict) or "items" not in data:
        UI.print_warning("Yedek dosyasında registry bilgisi bulunamadı (atlandı).")
        return

    items = data.get("items") or []
    total = len(items)
    if total == 0:
        UI.print_info("Registry yedeği boş (atlandı).")
        return

    def _parse_hive(key_path: str):
        if key_path.startswith("HKLM\\"):
            return winreg.HKEY_LOCAL_MACHINE, key_path[5:]
        if key_path.startswith("HKCU\\"):
            return winreg.HKEY_CURRENT_USER, key_path[5:]
        return None, None

    restored = 0
    for idx, item in enumerate(items, 1):
        try:
            key_path = item.get("path")
            value_name = item.get("value")
            exists = item.get("exists")
            vtype = item.get("type")
            vdata = item.get("data")
            if not key_path or not value_name:
                continue
            hive, subkey = _parse_hive(key_path)
            if hive is None or subkey is None:
                continue

            if not exists:
                # Eskiden yoktu -> value'yu silmeye çalış
                try:
                    key = winreg.OpenKey(hive, subkey, 0, winreg.KEY_SET_VALUE)
                    winreg.DeleteValue(key, value_name)
                    winreg.CloseKey(key)
                except Exception:
                    pass
            else:
                # Eskiden vardı -> eski değere döndür
                try:
                    key = winreg.CreateKey(hive, subkey)
                    winreg.SetValueEx(key, value_name, 0, int(vtype), vdata)
                    winreg.CloseKey(key)
                except Exception:
                    pass

            restored += 1
            UI.print_progress_bar(idx, total)
        except Exception:
            continue

    UI.print_success(f"Registry geri yüklendi: {restored}/{total}")


def restore_features(backup_data):
    """Windows Optional Feature'ları geri yükle (sadece dokunulanlar)"""
    features = backup_data.get("features") if isinstance(backup_data, dict) else None
    if not features or not isinstance(features, dict):
        UI.print_info("Feature yedeği bulunamadı (atlandı).")
        return

    UI.print_info("Windows özellikleri geri yükleniyor...")
    restored = 0
    total = len(features)
    for name, state in features.items():
        try:
            state_norm = (state or "").strip().lower()
            if not state_norm:
                continue
            if state_norm.startswith("enabled"):
                cmd = f'Enable-WindowsOptionalFeature -Online -FeatureName "{name}" -NoRestart -All -ErrorAction SilentlyContinue | Out-Null'
            else:
                cmd = f'Disable-WindowsOptionalFeature -Online -FeatureName "{name}" -NoRestart -ErrorAction SilentlyContinue | Out-Null'
            subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
                capture_output=True, text=True, timeout=60, check=False
            )
            restored += 1
            UI.print_progress_bar(restored, total)
        except Exception:
            pass
    UI.print_success(f"Windows özellikleri geri yüklendi: {restored}/{total}")


def restore_telemetry_blocker():
    """TelemetryBlocker task'ını kaldır (varsa)"""
    try:
        subprocess.run(["schtasks", "/Delete", "/TN", "TelemetryBlocker", "/F"],
                       capture_output=True, text=True, timeout=20, check=False)
    except Exception:
        pass


def restore_onedrive(backup_data):
    """OneDrive kaldırıldıysa tekrar kurmayı dene (best-effort)"""
    od = backup_data.get("onedrive") if isinstance(backup_data, dict) else None
    if not od or not isinstance(od, dict):
        return
    was_installed = bool(od.get("was_installed"))
    if not was_installed:
        return

    UI.print_info("OneDrive geri yükleme deneniyor (best-effort)...")
    windir = os.environ.get("WINDIR", r"C:\Windows")
    candidates = [
        Path(windir) / "SysWOW64" / "OneDriveSetup.exe",
        Path(windir) / "System32" / "OneDriveSetup.exe",
    ]
    for exe in candidates:
        if not exe.exists():
            continue
        try:
            # OneDriveSetup.exe çoğu sistemde /install destekler
            subprocess.run([str(exe), "/install"], capture_output=True, text=True, timeout=120, check=False)
            UI.print_success("OneDrive kurulum komutu çalıştırıldı.")
            return
        except Exception:
            pass
    UI.print_warning("OneDriveSetup.exe bulunamadı, OneDrive otomatik geri yüklenemedi.")
    try:
        temp_dir = os.environ.get("TEMP") or os.environ.get("TMP") or ""
        if temp_dir:
            bat = Path(temp_dir) / "telemetry_blocker.bat"
            if bat.exists():
                bat.unlink(missing_ok=True)
    except Exception:
        pass

def main():
    """Ana fonksiyon"""
    UI.print_banner()
    UI.print_info("Geri Yükleme Modu")
    
    # Yedek dosyalarını listele
    backup_dir = Path("backups")
    if not backup_dir.exists():
        UI.print_error("Yedek klasörü bulunamadı!")
        UI.print_info("Önce optimize.exe çalıştırılmalıdır.")
        UI.wait_for_key()
        return
    
    backup_files = list(backup_dir.glob("backup_*.json"))
    if not backup_files:
        UI.print_error("Yedek dosyası bulunamadı!")
        UI.print_info("Önce optimize.exe çalıştırılmalıdır.")
        UI.wait_for_key()
        return
    
    # En son yedeği göster
    latest_backup = max(backup_files, key=lambda p: p.stat().st_mtime)
    backup_time = datetime.fromtimestamp(latest_backup.stat().st_mtime)
    
    UI.print_section_header("Yedek Dosyası Bilgileri")
    UI.print_info(f"Dosya: {latest_backup.name}")
    UI.print_info(f"Oluşturulma: {backup_time.strftime('%Y-%m-%d %H:%M:%S')}")
    UI.print_info(f"Boyut: {latest_backup.stat().st_size / 1024:.2f} KB")
    
    UI.print_warning("Bu işlem ayarları geri yükleyecektir!")
    
    if not UI.ask_confirmation("Devam etmek istiyor musunuz? (E/H):"):
        UI.print_error("İşlem kullanıcı tarafından iptal edildi.")
        UI.wait_for_key()
        return
    
    # Yedeği yükle
    try:
        UI.print_info("Yedek dosyası okunuyor...")
        UI.loading_animation("Dosya yükleniyor", 0.5)
        
        with open(latest_backup, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        UI.print_success("Yedek dosyası başarıyla yüklendi.")
    except Exception as e:
        UI.print_error(f"Yedek dosyası okunamadı: {e}")
        UI.wait_for_key()
        return
    
    # Geri yükle
    try:
        UI.print_section_header("Geri Yükleme İşlemi")
        restore_services(backup_data)
        restore_registry(backup_data)
        restore_features(backup_data)
        restore_telemetry_blocker()
        restore_startup_tasks(backup_data)
        restore_onedrive(backup_data)
        
        UI.print_summary_box("Geri Yükleme Tamamlandı", [
            "Servisler geri yüklendi",
            "Kayıt defteri ayarları kontrol edildi",
            "Startup/Task trimming geri yüklendi",
            "",
            "NOT: Bazı değişiklikler için sistem",
            "yeniden başlatma gerekebilir."
        ])
        
        UI.print_success("Geri yükleme başarıyla tamamlandı!")
    except Exception as e:
        UI.print_error(f"Hata oluştu: {e}")
        UI.wait_for_key()
    
    UI.wait_for_key("\nİşlem tamamlandı. Çıkmak için bir tuşa basın...")

if __name__ == "__main__":
    main()

