#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Application Class
Senior-level application architecture with event-driven design
"""

import os
import sys
from pathlib import Path
from typing import Optional

from core.events import EventBus, Event, EventType, get_event_bus
from core.config import Config, ConfigManager, OptimizationMode
from core.logger import Logger, LogLevel, get_logger
from core.di import Container
from plugins.registry import PluginRegistry, get_registry
from plugins.loader import PluginLoader
from services.optimization_service import OptimizationService
from services.backup_service import BackupService
from services.restore_service import RestoreService

# UI import with fallback
try:
    from modules.ui import UI
except ImportError:
    # Fallback UI
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
        def print_summary_box(title, items): 
            print(f"\n{title}")
            for item in items: print(f"  {item}")
        @staticmethod
        def ask_confirmation(msg): 
            response = input(f"{msg} ").strip().upper()
            return response == 'E' or response == 'Y'
        @staticmethod
        def wait_for_key(msg=""): input(msg)


def is_admin() -> bool:
    """Check if running with administrator privileges"""
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


class Application:
    """
    Main application class
    Senior-level architecture with dependency injection and event-driven design
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        # Initialize core components
        self.event_bus = get_event_bus()
        self.config_manager = ConfigManager(config_file)
        self.config = self.config_manager.load()
        
        # Initialize logger
        log_config = self.config.logging
        self.logger = get_logger(
            name="WindowsOptimizer",
            level=LogLevel[log_config.level],
            log_file=Path(log_config.file) if log_config.file else None,
            console=log_config.console
        )
        
        # Initialize plugin system
        self.plugin_registry = get_registry()
        self.plugin_loader = PluginLoader(self.plugin_registry)
        
        # Initialize services
        self.backup_service = BackupService(
            event_bus=self.event_bus,
            plugin_registry=self.plugin_registry,
            logger=self.logger
        )
        self.backup_service.initialize(self.config.backup)
        
        self.optimization_service = OptimizationService(
            event_bus=self.event_bus,
            plugin_registry=self.plugin_registry,
            logger=self.logger
        )
        
        self.restore_service = RestoreService(
            event_bus=self.event_bus,
            plugin_registry=self.plugin_registry,
            logger=self.logger
        )
        
        # Register services in DI container
        Container.register_singleton(OptimizationService, self.optimization_service)
        Container.register_singleton(BackupService, self.backup_service)
        Container.register_singleton(RestoreService, self.restore_service)
        
        # Setup event handlers
        self._setup_event_handlers()
        
        # Load plugins
        self._load_plugins()
    
    def _setup_event_handlers(self):
        """Setup event handlers for UI updates"""
        def on_progress(event: Event):
            if event.event_type == EventType.OPTIMIZER_STARTED:
                data = event.data
                UI.print_info(f"Optimizing: {data.get('plugin_name')} ({data.get('index')}/{data.get('total')})")
        
        def on_error(event: Event):
            if event.event_type == EventType.ERROR_OCCURRED:
                UI.print_error(event.data.get('message', 'Unknown error'))
        
        self.event_bus.subscribe_callback(EventType.OPTIMIZER_STARTED, on_progress)
        self.event_bus.subscribe_callback(EventType.ERROR_OCCURRED, on_error)
    
    def _load_plugins(self):
        """Load optimizer plugins"""
        # Load from optimizers directory
        optimizers_path = Path(__file__).parent / "optimizers"
        plugins = self.plugin_loader.load_from_directory(optimizers_path)
        
        self.logger.info(f"Loaded {len(plugins)} plugins")
    
    def run_optimization(self) -> bool:
        """Run optimization process"""
        try:
            UI.print_banner()
            
            # Check admin rights
            if not is_admin():
                UI.print_error("Bu script yönetici haklarıyla çalıştırılmalıdır!")
                UI.print_warning("Lütfen PowerShell veya CMD'yi 'Yönetici olarak çalıştır' ile açın.")
                UI.wait_for_key()
                return False
            
            # Show configuration
            UI.print_info(f"Optimization Mode: {self.config.mode.value}")
            
            # Create backup
            UI.print_step(1, 3, "Creating Backup")
            backup_file = self.backup_service.create_backup(self.config)
            UI.print_success(f"Backup created: {backup_file.name}")
            
            # Run optimization
            UI.print_step(2, 3, "Running Optimizations")
            results = self.optimization_service.optimize(self.config)
            
            # Show summary
            UI.print_step(3, 3, "Optimization Complete")
            summary = self.optimization_service.get_summary()
            
            summary_items = [
                f"Total Plugins: {summary['total_plugins']}",
                f"Successful: {summary['successful']}",
                f"Failed: {summary['failed']}",
                f"Total Changes: {summary['total_changes']}",
                f"Backup File: {backup_file.name}",
            ]
            
            UI.print_summary_box("Optimization Summary", summary_items)
            
            # Cleanup old backups
            if self.config.backup.max_backups > 0:
                self.backup_service.cleanup_old_backups(self.config.backup.max_backups)
            
            return True
            
        except KeyboardInterrupt:
            UI.print_error("\nİşlem kullanıcı tarafından durduruldu!")
            return False
        except Exception as e:
            self.logger.exception("Error during optimization", exc_info=e)
            UI.print_error(f"Hata: {e}")
            return False
    
    def run_restore(self) -> bool:
        """Run restore process"""
        try:
            UI.print_banner()
            
            if not is_admin():
                UI.print_error("Bu script yönetici haklarıyla çalıştırılmalıdır!")
                return False
            
            # Get latest backup
            backup_file = self.backup_service.get_latest_backup()
            if not backup_file:
                UI.print_error("Yedek dosyası bulunamadı!")
                return False
            
            UI.print_info(f"Restoring from: {backup_file.name}")
            
            if not UI.ask_confirmation("Devam etmek istiyor musunuz? (E/H):"):
                return False
            
            # Restore
            results = self.restore_service.restore_from_backup(backup_file)
            
            UI.print_success(f"Restore completed: {results['successful']}/{results['total_plugins']} plugins restored")
            
            if results['failed'] > 0:
                UI.print_warning(f"{results['failed']} plugins failed to restore")
            
            return True
            
        except Exception as e:
            self.logger.exception("Error during restore", exc_info=e)
            UI.print_error(f"Hata: {e}")
            return False


def main():
    """Main entry point"""
    app = Application()
    
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        app.run_restore()
    else:
        app.run_optimization()
    
    UI.wait_for_key("\nİşlem tamamlandı. Çıkmak için bir tuşa basın...")


if __name__ == "__main__":
    main()

