#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimization Service
Orchestrates optimization process using event-driven architecture
"""

from typing import List, Optional
from datetime import datetime
import time

from core.events import EventBus, Event, EventType, get_event_bus
from core.config import Config
from core.logger import Logger, get_logger
from plugins.base import OptimizerPlugin, OptimizationResult, OptimizationStatus
from plugins.registry import PluginRegistry, get_registry


class OptimizationService:
    """
    Optimization service
    Coordinates optimization process with event-driven architecture
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
        self.results: List[OptimizationResult] = []
    
    def optimize(self, config: Config) -> List[OptimizationResult]:
        """
        Execute optimization process
        
        Args:
            config: Configuration object
            
        Returns:
            List of optimization results
        """
        start_time = time.time()
        self.results.clear()
        
        # Publish optimization started event
        self.event_bus.publish(Event(
            event_type=EventType.OPTIMIZATION_STARTED,
            timestamp=datetime.now(),
            source="OptimizationService",
            data={"config": config.to_dict()}
        ))
        
        self.logger.info("Optimization started", mode=config.mode.value)
        
        # Get sorted plugins
        plugins = self.plugin_registry.get_sorted()
        
        if not plugins:
            self.logger.warning("No plugins available for optimization")
            return self.results
        
        self.logger.info(f"Found {len(plugins)} plugins to execute")
        
        # Execute each plugin
        for idx, plugin in enumerate(plugins, 1):
            if not plugin.can_optimize(config):
                self.logger.info(f"Skipping plugin {plugin.name} (cannot optimize)")
                continue
            
            # Validate plugin
            validation_errors = plugin.validate(config)
            if validation_errors:
                self.logger.error(
                    f"Plugin {plugin.name} validation failed",
                    errors=validation_errors
                )
                result = OptimizationResult(
                    plugin_name=plugin.name,
                    status=OptimizationStatus.FAILED,
                    errors=validation_errors
                )
                self.results.append(result)
                continue
            
            # Publish optimizer started event
            self.event_bus.publish(Event(
                event_type=EventType.OPTIMIZER_STARTED,
                timestamp=datetime.now(),
                source="OptimizationService",
                data={
                    "plugin_name": plugin.name,
                    "index": idx,
                    "total": len(plugins)
                }
            ))
            
            # Execute optimization
            plugin_start_time = time.time()
            try:
                result = plugin.optimize(config)
                result.duration_ms = (time.time() - plugin_start_time) * 1000
                
                if result.status == OptimizationStatus.SUCCESS:
                    self.logger.info(
                        f"Plugin {plugin.name} completed successfully",
                        changes=result.changes_count,
                        duration_ms=result.duration_ms
                    )
                elif result.status == OptimizationStatus.PARTIAL:
                    self.logger.warning(
                        f"Plugin {plugin.name} completed with warnings",
                        changes=result.changes_count,
                        errors=len(result.errors)
                    )
                else:
                    self.logger.error(
                        f"Plugin {plugin.name} failed",
                        errors=result.errors
                    )
                
            except Exception as e:
                self.logger.exception(f"Error executing plugin {plugin.name}", exc_info=e)
                result = OptimizationResult(
                    plugin_name=plugin.name,
                    status=OptimizationStatus.FAILED,
                    errors=[str(e)],
                    duration_ms=(time.time() - plugin_start_time) * 1000
                )
            
            self.results.append(result)
            
            # Publish optimizer completed event
            self.event_bus.publish(Event(
                event_type=EventType.OPTIMIZER_COMPLETED,
                timestamp=datetime.now(),
                source="OptimizationService",
                data={
                    "plugin_name": plugin.name,
                    "status": result.status.value,
                    "changes_count": result.changes_count,
                    "errors_count": len(result.errors)
                }
            ))
        
        # Calculate totals
        total_duration = (time.time() - start_time) * 1000
        total_changes = sum(r.changes_count for r in self.results)
        successful = sum(1 for r in self.results if r.is_success())
        failed = sum(1 for r in self.results if r.status == OptimizationStatus.FAILED)
        
        # Publish optimization completed event
        self.event_bus.publish(Event(
            event_type=EventType.OPTIMIZATION_COMPLETED,
            timestamp=datetime.now(),
            source="OptimizationService",
            data={
                "total_plugins": len(plugins),
                "successful": successful,
                "failed": failed,
                "total_changes": total_changes,
                "duration_ms": total_duration
            }
        ))
        
        self.logger.info(
            "Optimization completed",
            total_plugins=len(plugins),
            successful=successful,
            failed=failed,
            total_changes=total_changes,
            duration_ms=total_duration
        )
        
        return self.results
    
    def get_results(self) -> List[OptimizationResult]:
        """Get optimization results"""
        return self.results
    
    def get_summary(self) -> dict:
        """Get optimization summary"""
        if not self.results:
            return {
                "total_plugins": 0,
                "successful": 0,
                "failed": 0,
                "total_changes": 0
            }
        
        return {
            "total_plugins": len(self.results),
            "successful": sum(1 for r in self.results if r.is_success()),
            "failed": sum(1 for r in self.results if r.status == OptimizationStatus.FAILED),
            "total_changes": sum(r.changes_count for r in self.results),
            "total_errors": sum(len(r.errors) for r in self.results),
            "total_warnings": sum(len(r.warnings) for r in self.results)
        }

