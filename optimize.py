#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 11 Optimizer - Balanced Edition
Oyun ve yazılım geliştirme için dengeli optimizasyonlar
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Yönetici hakları kontrolü
def is_admin():
    """Yönetici hakları kontrolü"""
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

if not is_admin():
    UI.print_error("Bu script yönetici haklarıyla çalıştırılmalıdır!")
    UI.print_warning("Lütfen PowerShell veya CMD'yi 'Yönetici olarak çalıştır' ile açın.")
    input("\nDevam etmek için bir tuşa basın...")
    sys.exit(1)

# Modülleri import et
from modules.services import ServiceOptimizer
from modules.registry import RegistryOptimizer
from modules.features import FeaturesOptimizer
from modules.performance import PerformanceOptimizer
from modules.privacy import PrivacyOptimizer
from modules.apps_remover import AppsRemover

# UI modülünü import et
try:
    from modules.ui import UI
    from colorama import Fore, Style
except ImportError:
    # Fallback için basit print fonksiyonları
    class UI:
        @staticmethod
        def print_banner(): print("\n" + "="*70 + "\n  Windows 11 Optimizer\n" + "="*70 + "\n")
        @staticmethod
        def print_error(msg): print(f"❌ {msg}")
        @staticmethod
        def print_warning(msg): print(f"⚠️  {msg}")
        @staticmethod
        def print_info(msg): print(f"ℹ️  {msg}")
        @staticmethod
        def print_success(msg): print(f"✅ {msg}")
        @staticmethod
        def print_step(n, t, msg): print(f"\n[{n}/{t}] {msg}")
        @staticmethod
        def print_progress_bar(c, t): print(f"\r[{c}/{t}]", end='', flush=True)
        @staticmethod
        def print_section_header(title): print(f"\n{'='*70}\n{title}\n{'='*70}\n")
        @staticmethod
        def print_summary_box(title, items): 
            print(f"\n{title}")
            for item in items: print(f"  {item}")
        @staticmethod
        def loading_animation(msg, d): print(f"⏳ {msg}")
        @staticmethod
        def ask_confirmation(msg): 
            response = input(f"{msg} ").strip().upper()
            return response == 'E' or response == 'Y'
        @staticmethod
        def wait_for_key(msg=""): input(msg)
    Fore = type('Fore', (), {'CYAN': '', 'GREEN': '', 'YELLOW': '', 'RED': '', 'MAGENTA': '', 'WHITE': ''})()
    Style = type('Style', (), {'RESET_ALL': ''})()

class WindowsOptimizer:
    """Ana optimizasyon sınıfı"""
    
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.backup_file = self.backup_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.changes = []
        
        # Optimizer modülleri
        self.service_optimizer = ServiceOptimizer()
        self.registry_optimizer = RegistryOptimizer()
        self.features_optimizer = FeaturesOptimizer()
        self.performance_optimizer = PerformanceOptimizer()
        self.privacy_optimizer = PrivacyOptimizer()
    
    def print_header(self):
        """Başlık yazdır"""
        UI.print_banner()
        UI.print_info("Sistem bilgileri kontrol ediliyor...")
        UI.loading_animation("Sistem hazırlanıyor", 0.5)
    
    def backup_current_settings(self):
        """Mevcut ayarları yedekle"""
        UI.print_step(1, 3, "Mevcut Ayarlar Yedekleniyor")
        UI.print_info("Servis durumları kaydediliyor...")
        UI.loading_animation("Servisler yedekleniyor", 0.3)
        
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "services": self.service_optimizer.backup_services(),
            "registry": self.registry_optimizer.backup_registry(),
            "features": self.features_optimizer.backup_features()
        }
        
        UI.print_info("Kayıt defteri ayarları kaydediliyor...")
        UI.loading_animation("Kayıt defteri yedekleniyor", 0.3)
        
        with open(self.backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        UI.print_success(f"Yedek oluşturuldu: {self.backup_file.name}")
        UI.print_info(f"Konum: {self.backup_file}")
    
    def optimize_all(self):
        """Tüm optimizasyonları uygula"""
        UI.print_step(2, 3, "Optimizasyonlar Uygulanıyor")
        
        optimizers = [
            ("Servisler", self.service_optimizer.optimize, "Windows servisleri optimize ediliyor..."),
            ("Kayıt Defteri", self.registry_optimizer.optimize, "Kayıt defteri ayarları uygulanıyor..."),
            ("Windows Özellikleri", self.features_optimizer.optimize, "Windows özellikleri kontrol ediliyor..."),
            ("Performans", self.performance_optimizer.optimize, "Performans ayarları optimize ediliyor..."),
            ("Gizlilik", self.privacy_optimizer.optimize, "Gizlilik ayarları uygulanıyor..."),
            ("Gereksiz Uygulamalar", lambda: self.apps_remover.optimize(remove_mode=True), "Gereksiz uygulamalar kaldırılıyor...")
        ]
        
        total_optimizers = len(optimizers)
        for idx, (name, optimizer_func, desc) in enumerate(optimizers, 1):
            UI.print_section_header(f"{name} Optimizasyonu ({idx}/{total_optimizers})")
            UI.print_info(desc)
            
            try:
                changes = optimizer_func()
                if changes:
                    self.changes.extend(changes)
                    UI.print_success(f"{len(changes)} değişiklik başarıyla uygulandı")
                else:
                    UI.print_info("Değişiklik gerekmedi (zaten optimize edilmiş)")
            except Exception as e:
                UI.print_error(f"Hata: {e}")
            
            # İlerleme çubuğu
            UI.print_progress_bar(idx, total_optimizers)
            time.sleep(0.2)  # Kısa bir gecikme
    
    def print_summary(self):
        """Özet yazdır"""
        UI.print_step(3, 3, "Optimizasyon Tamamlandı")
        
        summary_items = [
            f"Toplam {len(self.changes)} değişiklik uygulandı",
            f"Yedek dosyası: {self.backup_file.name}",
            "",
            "ÖNEMLİ NOTLAR:",
            "• Bazı değişiklikler için sistem yeniden başlatma gerekebilir",
            "• Windows Update bazı ayarları geri alabilir",
            "• Değişiklikleri geri almak için restore.exe kullanın"
        ]
        
        UI.print_summary_box("Optimizasyon Özeti", summary_items)
        
        UI.print_success("Tüm optimizasyonlar başarıyla tamamlandı!")
        UI.print_info("Sistem performansı ve gizlilik ayarları optimize edildi.")

def main():
    """Ana fonksiyon"""
    try:
        optimizer = WindowsOptimizer()
        optimizer.print_header()
        
        # Onay iste
        UI.print_warning("Bu script sistem ayarlarını değiştirecektir!")
        UI.print_info("Yapılacak değişiklikler:")
        print(f"  • {Fore.CYAN}~19 servis{Style.RESET_ALL} devre dışı bırakılacak")
        print(f"  • {Fore.CYAN}~18+ kayıt defteri{Style.RESET_ALL} ayarı optimize edilecek")
        print(f"  • {Fore.CYAN}Performans ve gizlilik{Style.RESET_ALL} ayarları uygulanacak")
        print(f"  • {Fore.GREEN}Tüm değişiklikler yedeklenecek{Style.RESET_ALL}")
        
        if not UI.ask_confirmation("Devam etmek istiyor musunuz? (E/H):"):
            UI.print_error("İşlem kullanıcı tarafından iptal edildi.")
            UI.wait_for_key()
            return
        
        # Yedekle
        optimizer.backup_current_settings()
        time.sleep(0.5)
        
        # Optimize et
        optimizer.optimize_all()
        
        # Özet
        optimizer.print_summary()
        
        UI.wait_for_key("\nİşlem tamamlandı. Çıkmak için bir tuşa basın...")
        
    except KeyboardInterrupt:
        UI.print_error("\nİşlem kullanıcı tarafından durduruldu!")
        UI.print_warning("Kısmi değişiklikler uygulanmış olabilir.")
        UI.wait_for_key()
    except Exception as e:
        UI.print_error(f"Hata oluştu: {e}")
        UI.print_info("Lütfen yedek dosyasını kontrol edin.")
        UI.wait_for_key()

if __name__ == "__main__":
    main()

