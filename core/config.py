#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Management System
Centralized configuration with validation and hot-reload support
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
from enum import Enum


class OptimizationMode(Enum):
    """Optimization modes"""
    BALANCED = "balanced"  # Oyun + Yazılım geliştirme
    GAMING = "gaming"       # Sadece oyun odaklı
    DEVELOPMENT = "development"  # Sadece yazılım geliştirme
    CUSTOM = "custom"      # Özel ayarlar


@dataclass
class ServiceConfig:
    """Service optimization configuration"""
    disable_telemetry: bool = True
    disable_xbox_services: bool = True
    disable_search: bool = True
    keep_wsl: bool = True
    keep_hyperv: bool = True
    keep_windows_update: bool = True


@dataclass
class RegistryConfig:
    """Registry optimization configuration"""
    enable_game_mode: bool = True
    enable_gpu_scheduling: bool = True
    disable_telemetry: bool = True
    disable_advertising: bool = True
    optimize_prefetch: bool = True
    disable_fast_startup: bool = True


@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    power_plan: str = "high_performance"  # balanced, high_performance
    disable_usb_suspend: bool = True
    disable_pcie_power_management: bool = True
    optimize_visual_effects: bool = True


@dataclass
class PrivacyConfig:
    """Privacy optimization configuration"""
    disable_telemetry: bool = True
    disable_advertising_id: bool = True
    disable_location_services: bool = True
    disable_cortana: bool = True


@dataclass
class BackupConfig:
    """Backup configuration"""
    enabled: bool = True
    directory: str = "backups"
    max_backups: int = 10
    compress: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration"""
    enabled: bool = True
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    file: Optional[str] = "optimizer.log"
    console: bool = True
    max_file_size_mb: int = 10
    backup_count: int = 5


@dataclass
class Config:
    """Main configuration class"""
    mode: OptimizationMode = OptimizationMode.BALANCED
    services: ServiceConfig = field(default_factory=ServiceConfig)
    registry: RegistryConfig = field(default_factory=RegistryConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    privacy: PrivacyConfig = field(default_factory=PrivacyConfig)
    backup: BackupConfig = field(default_factory=BackupConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "mode": self.mode.value,
            "services": asdict(self.services),
            "registry": asdict(self.registry),
            "performance": asdict(self.performance),
            "privacy": asdict(self.privacy),
            "backup": asdict(self.backup),
            "logging": asdict(self.logging),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create config from dictionary"""
        config = cls()
        if "mode" in data:
            config.mode = OptimizationMode(data["mode"])
        if "services" in data:
            config.services = ServiceConfig(**data["services"])
        if "registry" in data:
            config.registry = RegistryConfig(**data["registry"])
        if "performance" in data:
            config.performance = PerformanceConfig(**data["performance"])
        if "privacy" in data:
            config.privacy = PrivacyConfig(**data["privacy"])
        if "backup" in data:
            config.backup = BackupConfig(**data["backup"])
        if "logging" in data:
            config.logging = LoggingConfig(**data["logging"])
        return config


class ConfigManager:
    """Configuration manager with file persistence"""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path("config.json")
        self._config: Optional[Config] = None
        self._default_config = Config()
    
    def load(self) -> Config:
        """Load configuration from file or return default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._config = Config.from_dict(data)
                    return self._config
            except Exception as e:
                print(f"Error loading config: {e}, using defaults")
        
        self._config = self._default_config
        return self._config
    
    def save(self, config: Optional[Config] = None) -> None:
        """Save configuration to file"""
        config_to_save = config or self._config or self._default_config
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self) -> Config:
        """Get current configuration"""
        if self._config is None:
            self.load()
        return self._config or self._default_config
    
    def update(self, **kwargs) -> None:
        """Update configuration values"""
        config = self.get()
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        self.save(config)
    
    def reset(self) -> None:
        """Reset to default configuration"""
        self._config = Config()
        self.save()

