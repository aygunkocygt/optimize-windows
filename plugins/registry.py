#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin Registry
Manages optimizer plugins and their lifecycle
"""

from typing import Dict, List, Optional, Type
from .base import OptimizerPlugin, OptimizationResult
import threading


class PluginRegistry:
    """
    Plugin registry for managing optimizer plugins
    Thread-safe plugin management
    """
    
    def __init__(self):
        self._plugins: Dict[str, OptimizerPlugin] = {}
        self._lock = threading.RLock()
    
    def register(self, plugin: OptimizerPlugin) -> None:
        """Register a plugin"""
        with self._lock:
            self._plugins[plugin.name] = plugin
    
    def unregister(self, plugin_name: str) -> None:
        """Unregister a plugin"""
        with self._lock:
            if plugin_name in self._plugins:
                del self._plugins[plugin_name]
    
    def get(self, plugin_name: str) -> Optional[OptimizerPlugin]:
        """Get plugin by name"""
        with self._lock:
            return self._plugins.get(plugin_name)
    
    def get_all(self) -> List[OptimizerPlugin]:
        """Get all registered plugins"""
        with self._lock:
            return list(self._plugins.values())
    
    def get_enabled(self) -> List[OptimizerPlugin]:
        """Get all enabled plugins"""
        with self._lock:
            return [p for p in self._plugins.values() if p.enabled]
    
    def get_sorted(self) -> List[OptimizerPlugin]:
        """
        Get plugins sorted by priority and dependencies
        Returns plugins in execution order
        """
        with self._lock:
            plugins = list(self._plugins.values())
            enabled = [p for p in plugins if p.enabled]
            
            # Sort by priority
            enabled.sort(key=lambda p: p.priority)
            
            # Resolve dependencies
            sorted_plugins = []
            processed = set()
            
            def add_plugin(plugin: OptimizerPlugin):
                if plugin.name in processed:
                    return
                
                # Add dependencies first
                for dep_name in plugin.get_dependencies():
                    dep = self._plugins.get(dep_name)
                    if dep and dep.enabled:
                        add_plugin(dep)
                
                sorted_plugins.append(plugin)
                processed.add(plugin.name)
            
            for plugin in enabled:
                add_plugin(plugin)
            
            return sorted_plugins
    
    def exists(self, plugin_name: str) -> bool:
        """Check if plugin exists"""
        with self._lock:
            return plugin_name in self._plugins
    
    def count(self) -> int:
        """Get total plugin count"""
        with self._lock:
            return len(self._plugins)
    
    def clear(self) -> None:
        """Clear all plugins"""
        with self._lock:
            self._plugins.clear()


# Global registry instance
_registry: Optional[PluginRegistry] = None


def get_registry() -> PluginRegistry:
    """Get singleton plugin registry"""
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
    return _registry

