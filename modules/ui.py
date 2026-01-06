#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI Helper Modülü
Renkli çıktılar, ilerleme çubukları ve banner'lar için
"""

import sys
import time
from colorama import init, Fore, Back, Style

# Windows için colorama'yı başlat
init(autoreset=True)

class UI:
    """Kullanıcı arayüzü yardımcı sınıfı"""
    
    @staticmethod
    def print_banner():
        """Ana banner yazdır"""
        banner = f"""
{Fore.CYAN}{'='*70}
{Fore.CYAN}  {Fore.YELLOW}╔═══════════════════════════════════════════════════════════╗
{Fore.CYAN}  {Fore.YELLOW}║{Fore.WHITE}     Windows 11 Optimizer - Balanced Edition          {Fore.YELLOW}║
{Fore.CYAN}  {Fore.YELLOW}║{Fore.WHITE}     Oyun + Yazılım Geliştirme Optimizasyonu          {Fore.YELLOW}║
{Fore.CYAN}  {Fore.YELLOW}╚═══════════════════════════════════════════════════════════╝
{Fore.CYAN}{'='*70}
{Style.RESET_ALL}"""
        print(banner)
    
    @staticmethod
    def print_info(message):
        """Bilgi mesajı yazdır"""
        print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def print_success(message):
        """Başarı mesajı yazdır"""
        print(f"{Fore.GREEN}[✓]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def print_warning(message):
        """Uyarı mesajı yazdır"""
        print(f"{Fore.YELLOW}[!]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def print_error(message):
        """Hata mesajı yazdır"""
        print(f"{Fore.RED}[✗]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def print_step(step_num, total_steps, message):
        """Adım bilgisi yazdır"""
        print(f"\n{Fore.MAGENTA}[{step_num}/{total_steps}]{Style.RESET_ALL} {Fore.CYAN}{message}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'─'*70}{Style.RESET_ALL}")
    
    @staticmethod
    def print_progress_bar(current, total, width=50):
        """İlerleme çubuğu yazdır"""
        percent = current / total
        filled = int(width * percent)
        bar = '█' * filled + '░' * (width - filled)
        print(f"\r{Fore.GREEN}[{bar}]{Style.RESET_ALL} {Fore.CYAN}{percent*100:.1f}%{Style.RESET_ALL}", end='', flush=True)
        if current == total:
            print()  # Yeni satır
    
    @staticmethod
    def print_section_header(title):
        """Bölüm başlığı yazdır"""
        print(f"\n{Fore.YELLOW}{'═'*70}")
        print(f"{Fore.YELLOW}  {title}")
        print(f"{Fore.YELLOW}{'═'*70}{Style.RESET_ALL}\n")
    
    @staticmethod
    def print_summary_box(title, items):
        """Özet kutusu yazdır"""
        print(f"\n{Fore.CYAN}{'╔' + '═'*68 + '╗'}")
        print(f"{Fore.CYAN}║{Fore.YELLOW}  {title:<64}{Fore.CYAN}║")
        print(f"{Fore.CYAN}{'╠' + '═'*68 + '╣'}")
        for item in items:
            print(f"{Fore.CYAN}║{Style.RESET_ALL}  {item:<66}{Fore.CYAN}║")
        print(f"{Fore.CYAN}{'╚' + '═'*68 + '╝'}{Style.RESET_ALL}\n")
    
    @staticmethod
    def loading_animation(message, duration=1.0):
        """Yükleme animasyonu"""
        chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        end_time = time.time() + duration
        i = 0
        while time.time() < end_time:
            print(f"\r{Fore.CYAN}{chars[i % len(chars)]}{Style.RESET_ALL} {message}", end='', flush=True)
            time.sleep(0.1)
            i += 1
        print(f"\r{Fore.GREEN}✓{Style.RESET_ALL} {message}")
    
    @staticmethod
    def ask_confirmation(message):
        """Onay iste"""
        print(f"\n{Fore.YELLOW}[!]{Style.RESET_ALL} {message}")
        response = input(f"{Fore.CYAN}>>> {Style.RESET_ALL}").strip().upper()
        return response == 'E' or response == 'Y' or response == 'YES'
    
    @staticmethod
    def clear_screen():
        """Ekranı temizle"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def wait_for_key(message="Devam etmek için bir tuşa basın..."):
        """Tuşa basılmasını bekle"""
        print(f"\n{Fore.CYAN}{message}{Style.RESET_ALL}")
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.getch()
            else:
                input()
        except:
            input()

# os import'u eksikti, ekleyelim
import os

