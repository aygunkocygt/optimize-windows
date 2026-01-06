#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin Loader
Dynamic plugin loading and discovery
"""

import importlib
import inspect
from pathlib import Path
from typing import List, Type, Optional
from .base import OptimizerPlugin
from .registry import PluginRegistry, get_registry


class PluginLoader:
    """
    Plugin loader for dynamic plugin discovery and loading
    """
    
    def __init__(self, registry: Optional[PluginRegistry] = None):
        self.registry = registry or get_registry()
        self._loaded_modules = set()
    
    def load_from_module(self, module_path: str) -> List[OptimizerPlugin]:
        """
        Load plugins from a module
        
        Args:
            module_path: Module path (e.g., 'plugins.optimizers.services')
            
        Returns:
            List of loaded plugins
        """
        try:
            module = importlib.import_module(module_path)
            plugins = []
            
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, OptimizerPlugin) and 
                    obj != OptimizerPlugin):
                    try:
                        plugin = obj()
                        plugins.append(plugin)
                    except Exception as e:
                        print(f"Error instantiating plugin {name}: {e}")
            
            for plugin in plugins:
                self.registry.register(plugin)
            
            self._loaded_modules.add(module_path)
            return plugins
        except Exception as e:
            print(f"Error loading module {module_path}: {e}")
            return []
    
    def load_from_directory(self, directory: Path) -> List[OptimizerPlugin]:
        """
        Load plugins from a directory
        
        Args:
            directory: Directory path containing plugin modules
            
        Returns:
            List of loaded plugins
        """
        plugins = []
        
        if not directory.exists():
            return plugins
        
        # Find all Python files
        for file_path in directory.glob("*.py"):
            if file_path.name == "__init__.py":
                continue
            
            module_name = f"{directory.name}.{file_path.stem}"
            plugins.extend(self.load_from_module(module_name))
        
        return plugins
    
    def reload(self, module_path: str) -> List[OptimizerPlugin]:
        """Reload a module and its plugins"""
        if module_path in self._loaded_modules:
            importlib.reload(importlib.import_module(module_path))
            self._loaded_modules.remove(module_path)
        
        return self.load_from_module(module_path)
    
    def discover_plugins(self, base_path: Path) -> List[OptimizerPlugin]:
        """
        Discover and load all plugins from base path
        
        Args:
            base_path: Base directory for plugin discovery
            
        Returns:
            List of discovered plugins
        """
        plugins = []
        
        # Look for optimizers directory
        optimizers_path = base_path / "optimizers"
        if optimizers_path.exists():
            plugins.extend(self.load_from_directory(optimizers_path))
        
        return plugins

