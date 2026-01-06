#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restore Service
Manages restore operations with event-driven architecture
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from core.events import EventBus, Event, EventType, get_event_bus
from core.logger import Logger, get_logger
from plugins.registry import PluginRegistry, get_registry


class RestoreService:
    """
    Restore service for restoring system state from backups
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
    
    def restore_from_backup(self, backup_file: Path) -> Dict[str, Any]:
        """
        Restore system state from backup file
        
        Args:
            backup_file: Path to backup file
            
        Returns:
            Restore result dictionary
        """
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        # Publish restore started event
        self.event_bus.publish(Event(
            event_type=EventType.RESTORE_STARTED,
            timestamp=datetime.now(),
            source="RestoreService",
            data={"backup_file": str(backup_file)}
        ))
        
        self.logger.info(f"Restoring from backup: {backup_file.name}")
        
        # Load backup data
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load backup file: {e}")
            raise
        
        # Restore each plugin
        results = {
            "total_plugins": 0,
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        plugins_data = backup_data.get("plugins", {})
        
        for plugin_name, plugin_backup in plugins_data.items():
            results["total_plugins"] += 1
            
            plugin = self.plugin_registry.get(plugin_name)
            if not plugin:
                self.logger.warning(f"Plugin {plugin_name} not found, skipping restore")
                results["failed"] += 1
                results["errors"].append(f"Plugin {plugin_name} not found")
                continue
            
            try:
                success = plugin.restore(plugin_backup)
                if success:
                    results["successful"] += 1
                    self.logger.info(f"Restored plugin {plugin_name}")
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Plugin {plugin_name} restore returned False")
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Plugin {plugin_name}: {str(e)}")
                self.logger.error(f"Failed to restore plugin {plugin_name}: {e}")
        
        # Publish restore completed event
        self.event_bus.publish(Event(
            event_type=EventType.RESTORE_COMPLETED,
            timestamp=datetime.now(),
            source="RestoreService",
            data=results
        ))
        
        self.logger.info(
            "Restore completed",
            successful=results["successful"],
            failed=results["failed"]
        )
        
        return results

