"""
Plugin Architecture Module
Optimizers as plugins with strategy pattern
"""

from .base import OptimizerPlugin, OptimizationResult, OptimizationStatus
from .registry import PluginRegistry
from .loader import PluginLoader

__all__ = [
    'OptimizerPlugin',
    'OptimizationResult',
    'OptimizationStatus',
    'PluginRegistry',
    'PluginLoader',
]

