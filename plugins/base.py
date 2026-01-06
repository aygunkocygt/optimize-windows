#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Plugin Interface
Strategy pattern for optimizer plugins
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


class OptimizationStatus(Enum):
    """Optimization status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    PARTIAL = "partial"


@dataclass
class OptimizationResult:
    """Optimization result"""
    plugin_name: str
    status: OptimizationStatus
    changes_count: int = 0
    changes: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_change(self, change: Dict[str, Any]) -> None:
        """Add a change to the result"""
        self.changes.append(change)
        self.changes_count = len(self.changes)
    
    def add_error(self, error: str) -> None:
        """Add an error to the result"""
        self.errors.append(error)
        if self.status == OptimizationStatus.SUCCESS:
            self.status = OptimizationStatus.PARTIAL
    
    def add_warning(self, warning: str) -> None:
        """Add a warning to the result"""
        self.warnings.append(warning)
    
    def is_success(self) -> bool:
        """Check if optimization was successful"""
        return self.status == OptimizationStatus.SUCCESS
    
    def has_errors(self) -> bool:
        """Check if optimization has errors"""
        return len(self.errors) > 0


class OptimizerPlugin(ABC):
    """
    Base optimizer plugin interface
    All optimizers must implement this interface
    """
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.enabled = True
        self.priority = 0  # Lower number = higher priority
    
    @abstractmethod
    def optimize(self, config: Any) -> OptimizationResult:
        """
        Execute optimization
        
        Args:
            config: Configuration object
            
        Returns:
            OptimizationResult with details
        """
        pass
    
    @abstractmethod
    def can_optimize(self, config: Any) -> bool:
        """
        Check if optimizer can run with given config
        
        Args:
            config: Configuration object
            
        Returns:
            True if optimizer can run
        """
        pass
    
    def backup(self) -> Dict[str, Any]:
        """
        Backup current state
        
        Returns:
            Backup data dictionary
        """
        return {}
    
    def restore(self, backup_data: Dict[str, Any]) -> bool:
        """
        Restore from backup
        
        Args:
            backup_data: Backup data dictionary
            
        Returns:
            True if restore was successful
        """
        return False
    
    def validate(self, config: Any) -> List[str]:
        """
        Validate configuration
        
        Args:
            config: Configuration object
            
        Returns:
            List of validation errors (empty if valid)
        """
        return []
    
    def get_dependencies(self) -> List[str]:
        """
        Get list of plugin dependencies
        
        Returns:
            List of plugin names that must run before this one
        """
        return []
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "priority": self.priority,
            "dependencies": self.get_dependencies(),
        }

