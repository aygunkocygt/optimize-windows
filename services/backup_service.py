#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backup Service
Manages backup operations with event-driven architecture
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from core.events import EventBus, Event, EventType, get_event_bus
from core.config import Config, BackupConfig
from core.logger import Logger, get_logger
from plugins.registry import PluginRegistry, get_registry


class BackupService:
    """
    Backup service for managing system state backups
    """
    
    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
        plugin_registry: Optional[PluginRegistry] = None,
        logger: Optional[Logger] = None
    ):
        self.event_bus = event_bus or get_event_bus()
        self.plugin_registry = plugin_registry or get_registry()
        self.logger = logger or get_logger()
        self.backup_dir: Optional[Path] = None
    
    def initialize(self, config: BackupConfig) -> None:
        """Initialize backup service with configuration"""
        self.backup_dir = Path(config.directory)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, config: Config) -> Path:
        """
        Create backup of current system state
        
        Args:
            config: Configuration object
            
        Returns:
            Path to backup file
        """
        if self.backup_dir is None:
            raise RuntimeError("BackupService not initialized")
        
        # Publish backup started event
        self.event_bus.publish(Event(
            event_type=EventType.BACKUP_STARTED,
            timestamp=datetime.now(),
            source="BackupService",
            data={}
        ))
        
        self.logger.info("Creating backup")
        
        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"backup_{timestamp}.json"
        
        # Collect backup data from plugins
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "config": config.to_dict(),
            "plugins": {}
        }
        
        # Backup each plugin
        plugins = self.plugin_registry.get_all()
        for plugin in plugins:
            try:
                plugin_backup = plugin.backup()
                if plugin_backup:
                    backup_data["plugins"][plugin.name] = plugin_backup
            except Exception as e:
                self.logger.warning(f"Failed to backup plugin {plugin.name}: {e}")
        
        # Save backup file
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Backup created: {backup_file.name}")
            
            # Publish backup completed event
            self.event_bus.publish(Event(
                event_type=EventType.BACKUP_COMPLETED,
                timestamp=datetime.now(),
                source="BackupService",
                data={
                    "backup_file": str(backup_file),
                    "plugins_backed_up": len(backup_data["plugins"])
                }
            ))
            
            return backup_file
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            raise
    
    def get_latest_backup(self) -> Optional[Path]:
        """Get latest backup file"""
        if self.backup_dir is None or not self.backup_dir.exists():
            return None
        
        backup_files = list(self.backup_dir.glob("backup_*.json"))
        if not backup_files:
            return None
        
        return max(backup_files, key=lambda p: p.stat().st_mtime)
    
    def list_backups(self, limit: int = 10) -> list[Path]:
        """List backup files"""
        if self.backup_dir is None or not self.backup_dir.exists():
            return []
        
        backup_files = sorted(
            self.backup_dir.glob("backup_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        return backup_files[:limit]
    
    def cleanup_old_backups(self, max_backups: int) -> int:
        """Clean up old backups, keeping only the most recent ones"""
        if self.backup_dir is None or not self.backup_dir.exists():
            return 0
        
        backups = self.list_backups(limit=max_backups * 2)
        
        if len(backups) <= max_backups:
            return 0
        
        # Delete old backups
        deleted = 0
        for backup in backups[max_backups:]:
            try:
                backup.unlink()
                deleted += 1
            except Exception as e:
                self.logger.warning(f"Failed to delete backup {backup.name}: {e}")
        
        if deleted > 0:
            self.logger.info(f"Cleaned up {deleted} old backup(s)")
        
        return deleted

