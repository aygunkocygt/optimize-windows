# Architecture Documentation

## System Architecture Overview

This project follows **Senior-Level Event-Driven Architecture** with modern design patterns and best practices.

## Architecture Principles

### 1. Event-Driven Architecture (EDA)
- **EventBus**: Central event dispatcher using Observer pattern
- **Loose Coupling**: Components communicate through events
- **Asynchronous Processing**: Events can be processed asynchronously
- **Extensibility**: Easy to add new event handlers

### 2. Dependency Injection (DI)
- **Container**: IoC container for managing dependencies
- **Service Lifetime**: Singleton, Transient, Scoped
- **Testability**: Easy to mock dependencies

### 3. Plugin Architecture
- **Strategy Pattern**: Optimizers as plugins
- **Dynamic Loading**: Plugins loaded at runtime
- **Dependency Resolution**: Automatic dependency ordering
- **Extensibility**: Easy to add new optimizers

### 4. Separation of Concerns
- **Core**: Infrastructure (events, config, logging, DI)
- **Plugins**: Business logic (optimizers)
- **Services**: Application services (orchestration)
- **UI**: Presentation layer

## Directory Structure

```
optimize-windows/
├── core/                    # Core infrastructure
│   ├── events.py           # EventBus, Event, EventHandler
│   ├── config.py           # Configuration management
│   ├── logger.py           # Structured logging
│   └── di.py               # Dependency injection
│
├── plugins/                 # Plugin system
│   ├── base.py             # OptimizerPlugin interface
│   ├── registry.py         # Plugin registry
│   └── loader.py           # Plugin loader
│
├── optimizers/              # Optimizer plugins
│   ├── services_optimizer.py
│   ├── registry_optimizer.py
│   └── ...
│
├── services/                # Application services
│   ├── optimization_service.py
│   ├── backup_service.py
│   └── restore_service.py
│
├── modules/                  # Legacy modules (UI, etc.)
│   └── ui.py
│
└── application.py           # Main application class
```

## Core Components

### EventBus (`core/events.py`)

Central event dispatcher implementing Observer pattern.

**Features:**
- Thread-safe event publishing
- Multiple subscribers per event type
- Event history tracking
- Callback and handler support

**Usage:**
```python
from core.events import EventBus, Event, EventType

event_bus = get_event_bus()

# Subscribe
event_bus.subscribe_callback(EventType.OPTIMIZATION_STARTED, my_handler)

# Publish
event_bus.publish(Event(
    event_type=EventType.OPTIMIZATION_STARTED,
    timestamp=datetime.now(),
    source="MyService",
    data={"key": "value"}
))
```

### Configuration (`core/config.py`)

Centralized configuration management with validation.

**Features:**
- Type-safe configuration classes
- File persistence (JSON)
- Hot-reload support
- Mode-based configurations

**Usage:**
```python
from core.config import ConfigManager, OptimizationMode

config_manager = ConfigManager("config.json")
config = config_manager.load()

# Access config
if config.services.disable_telemetry:
    # ...
```

### Logger (`core/logger.py`)

Structured logging with file rotation.

**Features:**
- Multiple log levels
- File rotation
- Console and file output
- Structured logging with context

**Usage:**
```python
from core.logger import get_logger, LogLevel

logger = get_logger(level=LogLevel.INFO)
logger.info("Message", key="value")
```

### Dependency Injection (`core/di.py`)

IoC container for dependency management.

**Features:**
- Service registration
- Lifetime management
- Factory support
- Singleton pattern

**Usage:**
```python
from core.di import Container

# Register
Container.register(IService, ServiceImpl, ServiceLifetime.SINGLETON)

# Resolve
service = Container.resolve(IService)
```

## Plugin System

### OptimizerPlugin Interface

All optimizers implement `OptimizerPlugin` interface.

**Required Methods:**
- `optimize(config) -> OptimizationResult`
- `can_optimize(config) -> bool`

**Optional Methods:**
- `backup() -> Dict`
- `restore(backup_data) -> bool`
- `validate(config) -> List[str]`
- `get_dependencies() -> List[str]`

### Plugin Registry

Manages plugin lifecycle and execution order.

**Features:**
- Automatic dependency resolution
- Priority-based ordering
- Enable/disable plugins
- Thread-safe operations

### Plugin Loader

Dynamic plugin discovery and loading.

**Features:**
- Directory scanning
- Module loading
- Hot-reload support

## Services Layer

### OptimizationService

Orchestrates optimization process.

**Responsibilities:**
- Plugin execution
- Result aggregation
- Event publishing
- Error handling

### BackupService

Manages system state backups.

**Features:**
- Automatic backup creation
- Backup cleanup
- Backup listing

### RestoreService

Manages system state restoration.

**Features:**
- Backup loading
- Plugin restoration
- Error recovery

## Event Flow

```
User Action
    ↓
Application.run_optimization()
    ↓
BackupService.create_backup()
    ↓ [BACKUP_STARTED event]
    ↓ [BACKUP_COMPLETED event]
OptimizationService.optimize()
    ↓ [OPTIMIZATION_STARTED event]
    ↓
    For each plugin:
        Plugin.optimize()
        ↓ [OPTIMIZER_STARTED event]
        ↓ [SERVICE_DISABLED / REGISTRY_CHANGED events]
        ↓ [OPTIMIZER_COMPLETED event]
    ↓
    ↓ [OPTIMIZATION_COMPLETED event]
Results Summary
```

## Design Patterns Used

### 1. Observer Pattern
- **EventBus**: Publishers and subscribers
- **Event Handlers**: React to events

### 2. Strategy Pattern
- **OptimizerPlugin**: Different optimization strategies
- **Config Modes**: Different optimization modes

### 3. Factory Pattern
- **PluginLoader**: Creates plugin instances
- **ServiceProvider**: Creates service instances

### 4. Repository Pattern
- **BackupService**: Manages backup storage
- **ConfigManager**: Manages configuration storage

### 5. Singleton Pattern
- **EventBus**: Single instance
- **PluginRegistry**: Single instance
- **Container**: Single instance

### 6. Command Pattern
- **OptimizationResult**: Encapsulates operation results

## Benefits of This Architecture

### 1. **Maintainability**
- Clear separation of concerns
- Easy to locate and fix bugs
- Well-organized code structure

### 2. **Extensibility**
- Easy to add new optimizers (plugins)
- Easy to add new event handlers
- Easy to add new services

### 3. **Testability**
- Dependency injection enables mocking
- Event-driven design enables isolated testing
- Clear interfaces enable unit testing

### 4. **Scalability**
- Plugin system supports horizontal scaling
- Event-driven design supports async processing
- Service layer supports microservices migration

### 5. **Reliability**
- Structured error handling
- Event history for debugging
- Backup/restore capabilities

## Migration Path

### From Old Architecture

1. **Keep UI Module**: `modules/ui.py` remains unchanged
2. **Refactor Optimizers**: Convert to plugins
3. **Update Application**: Use new `Application` class
4. **Gradual Migration**: Can run old and new side-by-side

### Adding New Optimizer

1. Create plugin class inheriting `OptimizerPlugin`
2. Implement required methods
3. Place in `optimizers/` directory
4. PluginLoader will auto-discover

### Adding New Event Handler

1. Create handler class or function
2. Subscribe to EventBus
3. Handle events in `handle()` method

## Performance Considerations

- **Event Bus**: Thread-safe, low overhead
- **Plugin Loading**: Lazy loading supported
- **Logging**: Async logging can be added
- **Backup**: Compressed backups supported

## Security Considerations

- **Admin Check**: Required for all operations
- **Backup Validation**: Validates backup files
- **Error Handling**: Prevents information leakage
- **Logging**: Sensitive data excluded from logs

## Future Enhancements

1. **Async Operations**: Async/await support
2. **Web UI**: REST API and web interface
3. **Plugin Marketplace**: Download plugins
4. **Telemetry**: Optional usage analytics
5. **Multi-language**: i18n support


