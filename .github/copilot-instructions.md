# GitHub Copilot & Claude Code Instructions

This repository contains the Home Assistant Supervisor, a Python 3 based container
orchestration and management system for Home Assistant.

## Supervisor Capabilities & Features

### Architecture Overview

Home Assistant Supervisor is a Python-based container orchestration system that
communicates with the Docker daemon to manage containerized components. It is tightly
integrated with the underlying Operating System and core Operating System components
through D-Bus.

**Managed Components:**
- **Home Assistant Core**: The main home automation application running in its own
  container (also provides the web interface)
- **Add-ons**: Third-party applications and services (each add-on runs in its own
  container)
- **Plugins**: Built-in system services like DNS, Audio, CLI, Multicast, and Observer
- **Host System Integration**: OS-level operations and hardware access via D-Bus
- **Container Networking**: Internal Docker network management and external
  connectivity
- **Storage & Backup**: Data persistence and backup management across all containers

**Key Dependencies:**
- **Docker Engine**: Required for all container operations
- **D-Bus**: System-level communication with the host OS
- **systemd**: Service management for host system operations
- **NetworkManager**: Network configuration and management

### Add-on System

**Add-on Architecture**: Add-ons are containerized applications available through
add-on stores. Each store contains multiple add-ons, and each add-on includes metadata
that tells Supervisor the version, startup configuration (permissions), and available
user configurable options. Add-on metadata typically references a container image that
Supervisor fetches during installation. If not, the Supervisor builds the container
image from a Dockerfile.

**Built-in Stores**: Supervisor comes with several pre-configured stores:
- **Core Add-ons**: Official add-ons maintained by the Home Assistant team
- **Community Add-ons**: Popular third-party add-ons repository
- **ESPHome**: Add-ons for ESPHome ecosystem integration
- **Music Assistant**: Audio and music-related add-ons
- **Local Development**: Local folder for testing custom add-ons during development

**Store Management**: Stores are Git-based repositories that are periodically updated.
When updates are available, users receive notifications.

**Add-on Lifecycle**:
- **Installation**: Supervisor fetches or builds container images based on add-on
  metadata
- **Configuration**: Schema-validated options with integrated UI management
- **Runtime**: Full container lifecycle management, health monitoring
- **Updates**: Automatic or manual version management

### Update System

**Core Components**: Supervisor, Home Assistant Core, HAOS, and built-in plugins
receive version information from a central JSON file fetched from
`https://version.home-assistant.io/{channel}.json`. The `Updater` class handles
fetching this data, validating signatures, and updating internal version tracking.

**Update Channels**: Three channels (`stable`/`beta`/`dev`) determine which version
JSON file is fetched, allowing users to opt into different release streams.

**Add-on Updates**: Add-on version information comes from store repository updates, not
the central JSON file. When repositories are refreshed via the store system, add-ons
compare their local versions against repository versions to determine update
availability.

### Backup & Recovery System

**Backup Capabilities**:
- **Full Backups**: Complete system state capture including all add-ons,
  configuration, and data
- **Partial Backups**: Selective backup of specific components (Home Assistant,
  add-ons, folders)
- **Encrypted Backups**: Optional backup encryption with user-provided passwords
- **Multiple Storage Locations**: Local storage and remote backup destinations

**Recovery Features**:
- **One-click Restore**: Simple restoration from backup files
- **Selective Restore**: Choose specific components to restore
- **Automatic Recovery**: Self-healing for common system issues

---

## Supervisor Development

### Python Requirements

- **Compatibility**: Python 3.13+
- **Language Features**: Use modern Python features:
  - Type hints with `typing` module
  - f-strings (preferred over `%` or `.format()`)
  - Dataclasses and enum classes
  - Async/await patterns
  - Pattern matching where appropriate

### Code Quality Standards

- **Formatting**: Ruff
- **Linting**: PyLint and Ruff  
- **Type Checking**: MyPy
- **Testing**: pytest with asyncio support
- **Language**: American English for all code, comments, and documentation

### Code Organization

**Core Structure**:
```
supervisor/
├── __init__.py           # Package initialization
├── const.py             # Constants and enums
├── coresys.py           # Core system management
├── bootstrap.py         # System initialization
├── exceptions.py        # Custom exception classes
├── api/                 # REST API endpoints
├── addons/              # Add-on management
├── backups/             # Backup system
├── docker/              # Docker integration
├── host/                # Host system interface
├── homeassistant/       # Home Assistant Core management
├── dbus/                # D-Bus system integration
├── hardware/            # Hardware detection and management
├── plugins/             # Plugin system
├── resolution/          # Issue detection and resolution
├── security/            # Security management
├── services/            # Service discovery and management
├── store/               # Add-on store management
└── utils/               # Utility functions
```

**Shared Constants**: Use constants from `supervisor/const.py` instead of hardcoding
values. Define new constants following existing patterns and group related constants
together.

### Supervisor Architecture Patterns

**CoreSysAttributes Inheritance Pattern**: Nearly all major classes in Supervisor
inherit from `CoreSysAttributes`, providing access to the centralized system state
via `self.coresys` and convenient `sys_*` properties.

```python
# Standard Supervisor class pattern
class MyManager(CoreSysAttributes):
    """Manage my functionality."""
    
    def __init__(self, coresys: CoreSys):
        """Initialize manager."""
        self.coresys: CoreSys = coresys
        self._component: MyComponent = MyComponent(coresys)
    
    @property
    def component(self) -> MyComponent:
        """Return component handler."""
        return self._component
    
    # Access system components via inherited properties
    async def do_something(self):
        await self.sys_docker.containers.get("my_container")
        self.sys_bus.fire_event(BusEvent.MY_EVENT, {"data": "value"})
```

**Key Inherited Properties from CoreSysAttributes**:
- `self.sys_docker` - Docker API access
- `self.sys_run_in_executor()` - Execute blocking operations
- `self.sys_create_task()` - Create async tasks
- `self.sys_bus` - Event bus for system events
- `self.sys_config` - System configuration
- `self.sys_homeassistant` - Home Assistant Core management
- `self.sys_addons` - Add-on management
- `self.sys_host` - Host system access
- `self.sys_dbus` - D-Bus system interface

**Load Pattern**: Many components implement a `load()` method which effectively
initialize the component from external sources (containers, files, D-Bus services).

### API Development

**REST API Structure**:
- **Base Path**: `/api/` for all endpoints
- **Authentication**: Bearer token authentication
- **Consistent Response Format**: `{"result": "ok", "data": {...}}` or
  `{"result": "error", "message": "..."}`
- **Validation**: Use voluptuous schemas with `api_validate()`

**Use `@api_process` Decorator**: This decorator handles all standard error handling
and response formatting automatically. The decorator catches `APIError`, `HassioError`,
and other exceptions, returning appropriate HTTP responses.

```python
from ..api.utils import api_process, api_validate

@api_process
async def backup_full(self, request: web.Request) -> dict[str, Any]:
    """Create full backup."""
    body = await api_validate(SCHEMA_BACKUP_FULL, request)
    job = await self.sys_backups.do_backup_full(**body)
    return {ATTR_JOB_ID: job.uuid}
```

### Docker Integration

- **Container Management**: Use Supervisor's Docker manager instead of direct
  Docker API
- **Networking**: Supervisor manages internal Docker networks with predefined IP
  ranges
- **Security**: AppArmor profiles, capability restrictions, and user namespace
  isolation
- **Health Checks**: Implement health monitoring for all managed containers

### D-Bus Integration

- **Use dbus-fast**: Async D-Bus library for system integration
- **Service Management**: systemd, NetworkManager, hostname management
- **Error Handling**: Wrap D-Bus exceptions in Supervisor-specific exceptions

### Async Programming

- **All I/O operations must be async**: File operations, network calls, subprocess
  execution
- **Use asyncio patterns**: Prefer `asyncio.gather()` over sequential awaits
- **Executor jobs**: Use `self.sys_run_in_executor()` for blocking operations
- **Two-phase initialization**: `__init__` for sync setup, `post_init()` for async
  initialization

### Testing

- **Location**: `tests/` directory with module mirroring
- **Fixtures**: Extensive use of pytest fixtures for CoreSys setup
- **Mocking**: Mock external dependencies (Docker, D-Bus, network calls)
- **Coverage**: Minimum 90% test coverage, 100% for security-sensitive code

### Error Handling

- **Custom Exceptions**: Defined in `exceptions.py` with clear inheritance hierarchy
- **Error Propagation**: Use `from` clause for exception chaining
- **API Errors**: Use `APIError` with appropriate HTTP status codes

### Security Considerations

- **Container Security**: AppArmor profiles mandatory for add-ons, minimal
  capabilities
- **Authentication**: Token-based API authentication with role-based access
- **Data Protection**: Backup encryption, secure secret management, comprehensive
  input validation

### Development Commands

```bash
# Run tests, adjust paths as necessary
pytest -qsx tests/

# Linting and formatting
ruff check supervisor/
ruff format supervisor/

# Type checking
mypy --ignore-missing-imports supervisor/

# Pre-commit hooks
pre-commit run --all-files
```

Always run the pre-commit hooks at the end of code editing.

### Common Patterns to Follow

**✅ Use These Patterns**:
- Inherit from `CoreSysAttributes` for system access
- Use `@api_process` decorator for API endpoints
- Use `self.sys_run_in_executor()` for blocking operations
- Access Docker via `self.sys_docker` not direct Docker API
- Use constants from `const.py` instead of hardcoding
- Store types in (per-module) `const.py` (e.g. supervisor/store/const.py)

**❌ Avoid These Patterns**:
- Direct Docker API usage - use Supervisor's Docker manager
- Blocking operations in async context (use asyncio alternatives)
- Hardcoded values - use constants from `const.py`
- Manual error handling in API endpoints - let `@api_process` handle it

This guide provides the foundation for contributing to Home Assistant Supervisor.
Follow these patterns and guidelines to ensure code quality, security, and
maintainability.
