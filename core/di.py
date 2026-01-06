#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dependency Injection Container
IoC container for managing dependencies and service lifecycle
"""

from typing import Dict, Type, TypeVar, Callable, Any, Optional, Union
from abc import ABC, abstractmethod
from enum import Enum


T = TypeVar('T')


class ServiceLifetime(Enum):
    """Service lifetime types"""
    TRANSIENT = "transient"  # New instance every time
    SINGLETON = "singleton"  # Single instance
    SCOPED = "scoped"        # Instance per scope


class ServiceProvider:
    """
    Service provider for dependency injection
    Manages service registration and resolution
    """
    
    def __init__(self):
        self._services: Dict[Type, Dict[str, Any]] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register(
        self,
        service_type: Type[T],
        implementation: Optional[Union[Type[T], Callable[[], T]]] = None,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
        factory: Optional[Callable[[], T]] = None
    ) -> None:
        """
        Register a service
        
        Args:
            service_type: Interface or abstract class
            implementation: Concrete implementation class
            lifetime: Service lifetime
            factory: Factory function for creating instances
        """
        if implementation is None and factory is None:
            implementation = service_type
        
        self._services[service_type] = {
            "implementation": implementation,
            "lifetime": lifetime,
            "factory": factory
        }
    
    def register_singleton(
        self,
        service_type: Type[T],
        instance: Optional[T] = None,
        implementation: Optional[Type[T]] = None
    ) -> None:
        """Register singleton instance"""
        if instance is not None:
            self._singletons[service_type] = instance
            self._services[service_type] = {
                "implementation": None,
                "lifetime": ServiceLifetime.SINGLETON,
                "factory": None,
                "instance": instance
            }
        else:
            self.register(service_type, implementation, ServiceLifetime.SINGLETON)
    
    def register_factory(
        self,
        service_type: Type[T],
        factory: Callable[[], T],
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    ) -> None:
        """Register factory function"""
        self.register(service_type, None, lifetime, factory)
    
    def resolve(self, service_type: Type[T]) -> T:
        """
        Resolve service instance
        
        Args:
            service_type: Service type to resolve
            
        Returns:
            Service instance
            
        Raises:
            ValueError: If service is not registered
        """
        # Check if singleton exists
        if service_type in self._singletons:
            return self._singletons[service_type]
        
        # Check if service is registered
        if service_type not in self._services:
            raise ValueError(f"Service {service_type.__name__} is not registered")
        
        service_info = self._services[service_type]
        lifetime = service_info["lifetime"]
        implementation = service_info["implementation"]
        factory = service_info["factory"]
        
        # Create instance
        if factory:
            instance = factory()
        elif implementation:
            if isinstance(implementation, type):
                instance = implementation()
            else:
                instance = implementation
        else:
            instance = service_type()
        
        # Handle lifetime
        if lifetime == ServiceLifetime.SINGLETON:
            self._singletons[service_type] = instance
        
        return instance
    
    def get(self, service_type: Type[T]) -> Optional[T]:
        """Get service instance (returns None if not found)"""
        try:
            return self.resolve(service_type)
        except ValueError:
            return None
    
    def is_registered(self, service_type: Type) -> bool:
        """Check if service is registered"""
        return service_type in self._services
    
    def clear(self) -> None:
        """Clear all registrations"""
        self._services.clear()
        self._singletons.clear()


class Container:
    """
    Dependency Injection Container
    Singleton container for global service access
    """
    
    _instance: Optional['Container'] = None
    _provider: Optional[ServiceProvider] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._provider = ServiceProvider()
        return cls._instance
    
    @classmethod
    def get_provider(cls) -> ServiceProvider:
        """Get service provider instance"""
        if cls._provider is None:
            cls()
        return cls._provider
    
    @classmethod
    def register(cls, *args, **kwargs) -> None:
        """Register service"""
        cls.get_provider().register(*args, **kwargs)
    
    @classmethod
    def register_singleton(cls, *args, **kwargs) -> None:
        """Register singleton"""
        cls.get_provider().register_singleton(*args, **kwargs)
    
    @classmethod
    def resolve(cls, service_type: Type[T]) -> T:
        """Resolve service"""
        return cls.get_provider().resolve(service_type)
    
    @classmethod
    def get(cls, service_type: Type[T]) -> Optional[T]:
        """Get service"""
        return cls.get_provider().get(service_type)
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registrations"""
        cls.get_provider().clear()

