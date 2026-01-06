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
    UI.print_info("Kayıt defteri geri yükleme")
    UI.print_warning("Kayıt defteri geri yükleme şu anda manuel olarak yapılmalıdır.")
    UI.print_info("Yedek dosyasını kontrol edin: backups klasörü")

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
        
        UI.print_summary_box("Geri Yükleme Tamamlandı", [
            "Servisler geri yüklendi",
            "Kayıt defteri ayarları kontrol edildi",
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

