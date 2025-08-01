"""
NoxPanel v5.0 - Plugin Sandboxing System  
Secure plugin execution environment with resource limits and permission validation
"""

import importlib
import importlib.util
import json
import logging
import os
import shutil
import sys
import tempfile
import threading
import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import psutil

logger = logging.getLogger(__name__)

@dataclass
class PluginLimits:
    """Resource limits for plugin execution"""
    max_memory_mb: int = 100
    max_cpu_percent: float = 50.0
    max_execution_time_seconds: int = 30
    max_file_operations: int = 100
    max_network_connections: int = 10
    allowed_modules: Set[str] = None
    
    def __post_init__(self):
        if self.allowed_modules is None:
            self.allowed_modules = {
                # Standard library modules that are safe
                'json', 'os', 'sys', 'time', 'datetime', 'math', 'random',
                'collections', 'itertools', 'functools', 'operator',
                'string', 'regex', 're', 'pathlib', 'tempfile',
                # Flask and web-related
                'flask', 'requests', 'urllib',
                # Data processing
                'csv', 'xml', 'base64', 'hashlib', 'hmac',
                # Logging
                'logging'
            }

@dataclass 
class PluginPermissions:
    """Permissions for plugin operations"""
    can_read_files: bool = False
    can_write_files: bool = False
    can_execute_commands: bool = False
    can_access_network: bool = False
    can_access_database: bool = False
    can_modify_system: bool = False
    allowed_directories: List[str] = None
    
    def __post_init__(self):
        if self.allowed_directories is None:
            self.allowed_directories = []

class RestrictedImporter:
    """Custom import hook to restrict module access"""
    
    def __init__(self, allowed_modules: Set[str]):
        self.allowed_modules = allowed_modules
        self.original_import = __builtins__['__import__']
    
    def restricted_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        """Restricted import function"""
        base_module = name.split('.')[0]
        
        if base_module not in self.allowed_modules:
            raise ImportError(f"Module '{name}' is not allowed in plugin sandbox")
        
        return self.original_import(name, globals, locals, fromlist, level)
    
    def __enter__(self):
        __builtins__['__import__'] = self.restricted_import
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        __builtins__['__import__'] = self.original_import

class ResourceMonitor:
    """Monitor resource usage during plugin execution"""
    
    def __init__(self, limits: PluginLimits):
        self.limits = limits
        self.start_time = None
        self.start_memory = None
        self.process = psutil.Process()
        self.file_operations = 0
        self.network_connections = 0
        self.monitoring = False
        
    def start_monitoring(self):
        """Start resource monitoring"""
        self.monitoring = True
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss / (1024 * 1024)  # MB
        
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        
    def check_limits(self):
        """Check if resource limits are exceeded"""
        if not self.monitoring:
            return
            
        # Check execution time
        if time.time() - self.start_time > self.limits.max_execution_time_seconds:
            raise RuntimeError(f"Plugin execution time exceeded {self.limits.max_execution_time_seconds}s")
        
        # Check memory usage
        current_memory = self.process.memory_info().rss / (1024 * 1024)  # MB
        memory_used = current_memory - self.start_memory
        if memory_used > self.limits.max_memory_mb:
            raise RuntimeError(f"Plugin memory usage exceeded {self.limits.max_memory_mb}MB")
        
        # Check CPU usage
        cpu_percent = self.process.cpu_percent()
        if cpu_percent > self.limits.max_cpu_percent:
            logger.warning(f"Plugin CPU usage high: {cpu_percent}%")
        
        # Check file operations
        if self.file_operations > self.limits.max_file_operations:
            raise RuntimeError(f"Plugin file operations exceeded {self.limits.max_file_operations}")
    
    def record_file_operation(self):
        """Record a file operation"""
        self.file_operations += 1
        self.check_limits()
    
    def record_network_connection(self):
        """Record a network connection"""
        self.network_connections += 1
        if self.network_connections > self.limits.max_network_connections:
            raise RuntimeError(f"Plugin network connections exceeded {self.limits.max_network_connections}")

class PluginSandbox:
    """Secure sandbox environment for plugin execution"""
    
    def __init__(self, 
                 limits: PluginLimits = None, 
                 permissions: PluginPermissions = None):
        self.limits = limits or PluginLimits()
        self.permissions = permissions or PluginPermissions()
        self.monitor = ResourceMonitor(self.limits)
        self.temp_dir = None
        self.original_cwd = None
        
    def __enter__(self):
        """Enter sandbox environment"""
        # Create temporary directory for plugin
        self.temp_dir = tempfile.mkdtemp(prefix="noxpanel_plugin_")
        self.original_cwd = os.getcwd()
        
        # Change to temp directory
        os.chdir(self.temp_dir)
        
        # Start resource monitoring
        self.monitor.start_monitoring()
        
        logger.debug(f"🔒 Plugin sandbox activated: {self.temp_dir}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit sandbox environment"""
        # Stop monitoring
        self.monitor.stop_monitoring()
        
        # Restore original directory
        if self.original_cwd:
            os.chdir(self.original_cwd)
        
        # Clean up temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.debug(f"🧹 Plugin sandbox cleaned up: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to clean up plugin sandbox: {e}")
    
    def execute_plugin(self, plugin_path: str, plugin_config: Dict[str, Any] = None) -> Any:
        """Execute plugin in sandboxed environment"""
        if not os.path.exists(plugin_path):
            raise FileNotFoundError(f"Plugin file not found: {plugin_path}")
        
        plugin_config = plugin_config or {}
        
        try:
            # Load plugin module with restricted imports
            with RestrictedImporter(self.limits.allowed_modules):
                spec = importlib.util.spec_from_file_location(
                    "sandboxed_plugin", 
                    plugin_path
                )
                
                if spec is None or spec.loader is None:
                    raise ImportError(f"Could not load plugin from {plugin_path}")
                
                plugin_module = importlib.util.module_from_spec(spec)
                
                # Set up plugin environment
                plugin_module.__sandbox__ = self
                plugin_module.__config__ = plugin_config
                plugin_module.__permissions__ = self.permissions
                
                # Execute plugin
                spec.loader.exec_module(plugin_module)
                
                # Look for main plugin functions
                if hasattr(plugin_module, 'main'):
                    return plugin_module.main(plugin_config)
                elif hasattr(plugin_module, 'run'):
                    return plugin_module.run(plugin_config)
                elif hasattr(plugin_module, 'execute'):
                    return plugin_module.execute(plugin_config)
                else:
                    logger.warning("Plugin has no main/run/execute function")
                    return None
                    
        except Exception as e:
            logger.error(f"Plugin execution failed: {e}")
            logger.debug(f"Plugin traceback: {traceback.format_exc()}")
            raise

class SecurePluginLoader:
    """Secure plugin loader with sandboxing"""
    
    def __init__(self):
        self.loaded_plugins: Dict[str, Any] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        
    def load_plugin_metadata(self, plugin_dir: Path) -> Optional[Dict[str, Any]]:
        """Load and validate plugin metadata"""
        metadata_file = plugin_dir / "plugin.json"
        
        if not metadata_file.exists():
            logger.warning(f"No plugin.json found in {plugin_dir}")
            return None
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Validate required fields
            required_fields = ['name', 'version', 'description']
            for field in required_fields:
                if field not in metadata:
                    raise ValueError(f"Missing required field: {field}")
            
            # Set default security settings
            if 'security' not in metadata:
                metadata['security'] = {
                    'limits': {},
                    'permissions': {}
                }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to load plugin metadata from {plugin_dir}: {e}")
            return None
    
    def create_sandbox_from_metadata(self, metadata: Dict[str, Any]) -> PluginSandbox:
        """Create sandbox based on plugin metadata"""
        security_config = metadata.get('security', {})
        
        # Create limits
        limits_config = security_config.get('limits', {})
        limits = PluginLimits(
            max_memory_mb=limits_config.get('max_memory_mb', 100),
            max_cpu_percent=limits_config.get('max_cpu_percent', 50.0),
            max_execution_time_seconds=limits_config.get('max_execution_time_seconds', 30),
            max_file_operations=limits_config.get('max_file_operations', 100),
            max_network_connections=limits_config.get('max_network_connections', 10)
        )
        
        # Add custom allowed modules
        if 'allowed_modules' in limits_config:
            limits.allowed_modules.update(limits_config['allowed_modules'])
        
        # Create permissions
        perms_config = security_config.get('permissions', {})
        permissions = PluginPermissions(
            can_read_files=perms_config.get('can_read_files', False),
            can_write_files=perms_config.get('can_write_files', False),
            can_execute_commands=perms_config.get('can_execute_commands', False),
            can_access_network=perms_config.get('can_access_network', False),
            can_access_database=perms_config.get('can_access_database', False),
            can_modify_system=perms_config.get('can_modify_system', False),
            allowed_directories=perms_config.get('allowed_directories', [])
        )
        
        return PluginSandbox(limits, permissions)
    
    def load_plugin_secure(self, plugin_name: str, plugin_dir: Path) -> bool:
        """Load plugin with security sandboxing"""
        try:
            # Ensure plugin_dir is a Path object and exists
            if isinstance(plugin_dir, str):
                plugin_dir = Path(plugin_dir)
            
            if not plugin_dir.exists():
                logger.error(f"Plugin directory does not exist: {plugin_dir}")
                return False
            
            # Load metadata
            metadata = self.load_plugin_metadata(plugin_dir)
            if not metadata:
                logger.error(f"Failed to load metadata for plugin {plugin_name}")
                return False
            
            # Find main plugin file
            main_file = plugin_dir / "main.py"
            if not main_file.exists():
                logger.error(f"Plugin file not found: {main_file}")
                return False
            
            # Create sandbox
            sandbox = self.create_sandbox_from_metadata(metadata)
            
            # Execute plugin in sandbox
            with sandbox:
                result = sandbox.execute_plugin(str(main_file), metadata.get('config', {}))
                
                # Store plugin info
                self.loaded_plugins[plugin_name] = {
                    'metadata': metadata,
                    'result': result,
                    'sandbox': sandbox,
                    'loaded_at': time.time()
                }
                
                logger.info(f"✅ Plugin loaded securely: {plugin_name}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to load plugin {plugin_name}: {e}")
            logger.debug(f"Plugin loading error details: {traceback.format_exc()}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload plugin and clean up resources"""
        if plugin_name not in self.loaded_plugins:
            logger.warning(f"Plugin {plugin_name} not loaded")
            return False
        
        try:
            # Clean up plugin resources
            del self.loaded_plugins[plugin_name]
            
            logger.info(f"🧹 Plugin unloaded: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def get_loaded_plugins(self) -> List[str]:
        """Get list of loaded plugin names"""
        return list(self.loaded_plugins.keys())
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a loaded plugin"""
        return self.loaded_plugins.get(plugin_name)

# Global secure plugin loader
secure_plugin_loader = SecurePluginLoader()

def load_plugin_securely(plugin_name: str, plugin_dir: Path) -> bool:
    """Load plugin with security sandboxing"""
    return secure_plugin_loader.load_plugin_secure(plugin_name, plugin_dir)

def get_secure_plugin_loader() -> SecurePluginLoader:
    """Get the global secure plugin loader"""
    return secure_plugin_loader
