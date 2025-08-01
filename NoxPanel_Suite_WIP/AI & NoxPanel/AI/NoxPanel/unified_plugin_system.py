from datetime import datetime, timezone

from NoxPanel.noxcore.utils.logging_config import get_logger

logger = get_logger(__name__)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ultimate Suite v11.0 - Unified Plugin System
============================================

This module consolidates all plugin systems from across the project:
- Core plugin management
- AI plugin system
- NoxPanel plugin system
- Legacy plugin systems

Author: Ultimate Suite Development Team
Date: July 18, 2025
Version: 11.0.0
Status: PRODUCTION READY
"""

import gc
import hashlib
import importlib
import importlib.util
import inspect
import json
import logging
import os
import sys
import threading
import time
import traceback
import uuid
import weakref
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union

# Plugin system dependencies
try:
    import jsonschema
    from jsonschema import ValidationError, validate
    from packaging import version
    
except ImportError as e:
    logger.info(f"Plugin system dependency missing: {e}")
    logger.info("Please install required packages:")
    logger.info("pip install packaging jsonschema")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PluginStatus(Enum):
    """
    REASONING CHAIN:
    1. Problem: System component PluginStatus needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for PluginStatus functionality
    3. Solution: Implement PluginStatus with SOLID principles and enterprise patterns
    4. Validation: Test PluginStatus with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Plugin status enumeration"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    DISABLED = "disabled"

class PluginType(Enum):
    """
    REASONING CHAIN:
    1. Problem: System component PluginType needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for PluginType functionality
    3. Solution: Implement PluginType with SOLID principles and enterprise patterns
    4. Validation: Test PluginType with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Plugin type enumeration"""
    CORE = "core"
    EXTENSION = "extension"
    THEME = "theme"
    WIDGET = "widget"
    SERVICE = "service"
    MIDDLEWARE = "middleware"
    AI = "ai"
    CUSTOM = "custom"

class PluginPriority(Enum):
    """
    REASONING CHAIN:
    1. Problem: System component PluginPriority needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for PluginPriority functionality
    3. Solution: Implement PluginPriority with SOLID principles and enterprise patterns
    4. Validation: Test PluginPriority with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Plugin priority enumeration"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    OPTIONAL = 4

@dataclass
class PluginMetadata:
    """
    REASONING CHAIN:
    1. Problem: System component PluginMetadata needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for PluginMetadata functionality
    3. Solution: Implement PluginMetadata with SOLID principles and enterprise patterns
    4. Validation: Test PluginMetadata with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Plugin metadata container"""
    name: str
    version: str
    description: str = ""
    author: str = ""
    author_email: str = ""
    homepage: str = ""
    
    # Plugin classification
    plugin_type: PluginType = PluginType.EXTENSION
    priority: PluginPriority = PluginPriority.NORMAL
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    optional_dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    
    # Version constraints
    min_system_version: str = "11.0.0"
    max_system_version: str = ""
    python_version: str = ">=3.8"
    
    # Plugin configuration
    config_schema: Dict[str, Any] = field(default_factory=dict)
    default_config: Dict[str, Any] = field(default_factory=dict)
    
    # Plugin capabilities
    capabilities: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    
    # File information
    file_path: str = ""
    file_hash: str = ""
    file_size: int = 0
    
    # Runtime information
    load_time: float = 0.0
    enabled: bool = True
    auto_enable: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __post_init__ with enterprise-grade patterns and error handling
    4. Validation: Test __post_init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Post-initialization processing"""
        if isinstance(self.plugin_type, str):
            self.plugin_type = PluginType(self.plugin_type)
        if isinstance(self.priority, str):
            self.priority = PluginPriority(self.priority)
    
    def to_dict(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function to_dict needs clear operational definition
    2. Analysis: Implementation requires specific logic for to_dict operation
    3. Solution: Implement to_dict with enterprise-grade patterns and error handling
    4. Validation: Test to_dict with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Convert to dictionary"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'author_email': self.author_email,
            'homepage': self.homepage,
            'plugin_type': self.plugin_type.value,
            'priority': self.priority.value,
            'dependencies': self.dependencies,
            'optional_dependencies': self.optional_dependencies,
            'conflicts': self.conflicts,
            'min_system_version': self.min_system_version,
            'max_system_version': self.max_system_version,
            'python_version': self.python_version,
            'config_schema': self.config_schema,
            'default_config': self.default_config,
            'capabilities': self.capabilities,
            'permissions': self.permissions,
            'file_path': self.file_path,
            'file_hash': self.file_hash,
            'file_size': self.file_size,
            'load_time': self.load_time,
            'enabled': self.enabled,
            'auto_enable': self.auto_enable,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginMetadata':
    """
    REASONING CHAIN:
    1. Problem: Function from_dict needs clear operational definition
    2. Analysis: Implementation requires specific logic for from_dict operation
    3. Solution: Implement from_dict with enterprise-grade patterns and error handling
    4. Validation: Test from_dict with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Create from dictionary"""
        # Handle datetime fields
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # Handle enum fields
        if 'plugin_type' in data and isinstance(data['plugin_type'], str):
            data['plugin_type'] = PluginType(data['plugin_type'])
        if 'priority' in data and isinstance(data['priority'], str):
            data['priority'] = PluginPriority(data['priority'])
        
        return cls(**data)

class PluginInterface(ABC):
    """
    REASONING CHAIN:
    1. Problem: System component PluginInterface needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for PluginInterface functionality
    3. Solution: Implement PluginInterface with SOLID principles and enterprise patterns
    4. Validation: Test PluginInterface with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Base interface for all plugins"""
    
    @abstractmethod
    def initialize(self, context: Dict[str, Any]) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function initialize needs clear operational definition
    2. Analysis: Implementation requires specific logic for initialize operation
    3. Solution: Implement initialize with enterprise-grade patterns and error handling
    4. Validation: Test initialize with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Initialize the plugin"""
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function cleanup needs clear operational definition
    2. Analysis: Implementation requires specific logic for cleanup operation
    3. Solution: Implement cleanup with enterprise-grade patterns and error handling
    4. Validation: Test cleanup with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Clean up plugin resources"""
        pass
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_metadata with enterprise-grade patterns and error handling
    4. Validation: Test get_metadata with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get plugin metadata"""
        pass
    
    def get_config(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_config with enterprise-grade patterns and error handling
    4. Validation: Test get_config with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get plugin configuration"""
        return {}
    
    def set_config(self, config: Dict[str, Any]) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Data modification needs controlled state management
    2. Analysis: Setter method requires validation and state consistency
    3. Solution: Implement set_config with enterprise-grade patterns and error handling
    4. Validation: Test set_config with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Set plugin configuration"""
        return True
    
    def get_status(self) -> PluginStatus:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_status with enterprise-grade patterns and error handling
    4. Validation: Test get_status with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get plugin status"""
        return PluginStatus.ACTIVE
    
    def get_info(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_info with enterprise-grade patterns and error handling
    4. Validation: Test get_info with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get plugin information"""
        return {
            'metadata': self.get_metadata().to_dict(),
            'config': self.get_config(),
            'status': self.get_status().value
        }

class CorePlugin(PluginInterface):
    """
    REASONING CHAIN:
    1. Problem: System component CorePlugin needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for CorePlugin functionality
    3. Solution: Implement CorePlugin with SOLID principles and enterprise patterns
    4. Validation: Test CorePlugin with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Enhanced core plugin base class"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self.name = name
        self.version = version
        self.context = {}
        self.config = {}
        self.status = PluginStatus.UNLOADED
        self.logger = logging.getLogger(f"plugin.{name}")
        self.event_handlers = {}
        self.hooks = {}
        self.initialized = False
        self.cleanup_tasks = []
        
        # Performance tracking
        self.performance_stats = {
            'init_time': 0.0,
            'total_runtime': 0.0,
            'call_count': 0,
            'error_count': 0,
            'last_error': None
        }
        
        # Create metadata
        self.metadata = PluginMetadata(
            name=name,
            version=version,
            description=self.get_description(),
            author=self.get_author(),
            plugin_type=self.get_plugin_type(),
            priority=self.get_priority(),
            dependencies=self.get_dependencies(),
            capabilities=self.get_capabilities(),
            permissions=self.get_permissions()
        )
    
    def get_description(self) -> str:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_description with enterprise-grade patterns and error handling
    4. Validation: Test get_description with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Override to provide plugin description"""
        return ""
    
    def get_author(self) -> str:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_author with enterprise-grade patterns and error handling
    4. Validation: Test get_author with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Override to provide plugin author"""
        return ""
    
    def get_plugin_type(self) -> PluginType:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_plugin_type with enterprise-grade patterns and error handling
    4. Validation: Test get_plugin_type with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Override to provide plugin type"""
        return PluginType.EXTENSION
    
    def get_priority(self) -> PluginPriority:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_priority with enterprise-grade patterns and error handling
    4. Validation: Test get_priority with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Override to provide plugin priority"""
        return PluginPriority.NORMAL
    
    def get_dependencies(self) -> List[str]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_dependencies with enterprise-grade patterns and error handling
    4. Validation: Test get_dependencies with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Override to provide plugin dependencies"""
        return []
    
    def get_capabilities(self) -> List[str]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_capabilities with enterprise-grade patterns and error handling
    4. Validation: Test get_capabilities with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Override to provide plugin capabilities"""
        return []
    
    def get_permissions(self) -> List[str]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_permissions with enterprise-grade patterns and error handling
    4. Validation: Test get_permissions with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Override to provide plugin permissions"""
        return []
    
    def initialize(self, context: Dict[str, Any]) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function initialize needs clear operational definition
    2. Analysis: Implementation requires specific logic for initialize operation
    3. Solution: Implement initialize with enterprise-grade patterns and error handling
    4. Validation: Test initialize with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Initialize the plugin"""
        try:
            start_time = utc_now().timestamp()
            self.status = PluginStatus.LOADING
            
            self.context = context
            self.config = context.get('config', {})
            
            # Validate configuration
            if not self.validate_config():
                self.status = PluginStatus.ERROR
                return False
            
            # Initialize plugin
            if not self.on_initialize():
                self.status = PluginStatus.ERROR
                return False
            
            # Register event handlers
            self.register_event_handlers()
            
            # Register hooks
            self.register_hooks()
            
            self.initialized = True
            self.status = PluginStatus.ACTIVE
            
            # Record performance
            self.performance_stats['init_time'] = utc_now().timestamp() - start_time
            
            self.logger.info(f"Plugin {self.name} initialized successfully")
            return True
            
        except Exception as e:
            self.status = PluginStatus.ERROR
            self.performance_stats['error_count'] += 1
            self.performance_stats['last_error'] = str(e)
            self.logger.error(f"Plugin {self.name} initialization failed: {e}")
            return False
    
    def cleanup(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function cleanup needs clear operational definition
    2. Analysis: Implementation requires specific logic for cleanup operation
    3. Solution: Implement cleanup with enterprise-grade patterns and error handling
    4. Validation: Test cleanup with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Clean up plugin resources"""
        try:
            self.logger.info(f"Cleaning up plugin {self.name}")
            
            # Unregister event handlers
            self.unregister_event_handlers()
            
            # Unregister hooks
            self.unregister_hooks()
            
            # Run cleanup tasks
            for task in self.cleanup_tasks:
                try:
                    task()
                except Exception as e:
                    self.logger.error(f"Cleanup task failed: {e}")
            
            # Plugin-specific cleanup
            self.on_cleanup()
            
            self.status = PluginStatus.UNLOADED
            self.initialized = False
            
            self.logger.info(f"Plugin {self.name} cleaned up successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Plugin {self.name} cleanup failed: {e}")
            return False
    
    def get_metadata(self) -> PluginMetadata:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_metadata with enterprise-grade patterns and error handling
    4. Validation: Test get_metadata with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get plugin metadata"""
        return self.metadata
    
    def get_config(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_config with enterprise-grade patterns and error handling
    4. Validation: Test get_config with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get plugin configuration"""
        return self.config
    
    def set_config(self, config: Dict[str, Any]) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Data modification needs controlled state management
    2. Analysis: Setter method requires validation and state consistency
    3. Solution: Implement set_config with enterprise-grade patterns and error handling
    4. Validation: Test set_config with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Set plugin configuration"""
        try:
            # Validate configuration
            if not self.validate_config(config):
                return False
            
            self.config = config
            self.on_config_changed()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set config: {e}")
            return False
    
    def get_status(self) -> PluginStatus:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_status with enterprise-grade patterns and error handling
    4. Validation: Test get_status with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get plugin status"""
        return self.status
    
    def validate_config(self, config: Dict[str, Any] = None) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Input validation needs comprehensive checking logic
    2. Analysis: Validation function requires thorough input analysis
    3. Solution: Implement validate_config with enterprise-grade patterns and error handling
    4. Validation: Test validate_config with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Validate plugin configuration"""
        if config is None:
            config = self.config
        
        # Check if schema is defined
        if not self.metadata.config_schema:
            return True
        
        try:
            validate(config, self.metadata.config_schema)
            return True
        except ValidationError as e:
            self.logger.error(f"Config validation failed: {e}")
            return False
    
    def register_event_handler(self, event_type: str, handler: Callable):
    """
    REASONING CHAIN:
    1. Problem: Function register_event_handler needs clear operational definition
    2. Analysis: Implementation requires specific logic for register_event_handler operation
    3. Solution: Implement register_event_handler with enterprise-grade patterns and error handling
    4. Validation: Test register_event_handler with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def register_hook(self, hook_name: str, handler: Callable):
    """
    REASONING CHAIN:
    1. Problem: Function register_hook needs clear operational definition
    2. Analysis: Implementation requires specific logic for register_hook operation
    3. Solution: Implement register_hook with enterprise-grade patterns and error handling
    4. Validation: Test register_hook with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Register hook handler"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(handler)
    
    def emit_event(self, event_type: str, data: Dict[str, Any]):
    """
    REASONING CHAIN:
    1. Problem: Function emit_event needs clear operational definition
    2. Analysis: Implementation requires specific logic for emit_event operation
    3. Solution: Implement emit_event with enterprise-grade patterns and error handling
    4. Validation: Test emit_event with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Emit event to registered handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    self.logger.error(f"Event handler failed: {e}")
    
    def call_hook(self, hook_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function call_hook needs clear operational definition
    2. Analysis: Implementation requires specific logic for call_hook operation
    3. Solution: Implement call_hook with enterprise-grade patterns and error handling
    4. Validation: Test call_hook with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Call hook handlers"""
        if hook_name in self.hooks:
            for handler in self.hooks[hook_name]:
                try:
                    data = handler(data) or data
                except Exception as e:
                    self.logger.error(f"Hook handler failed: {e}")
        return data
    
    def add_cleanup_task(self, task: Callable):
    """
    REASONING CHAIN:
    1. Problem: Function add_cleanup_task needs clear operational definition
    2. Analysis: Implementation requires specific logic for add_cleanup_task operation
    3. Solution: Implement add_cleanup_task with enterprise-grade patterns and error handling
    4. Validation: Test add_cleanup_task with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Add cleanup task"""
        self.cleanup_tasks.append(task)
    
    # Override these methods in subclasses
    def on_initialize(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function on_initialize needs clear operational definition
    2. Analysis: Implementation requires specific logic for on_initialize operation
    3. Solution: Implement on_initialize with enterprise-grade patterns and error handling
    4. Validation: Test on_initialize with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Called during initialization"""
        return True
    
    def on_cleanup(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function on_cleanup needs clear operational definition
    2. Analysis: Implementation requires specific logic for on_cleanup operation
    3. Solution: Implement on_cleanup with enterprise-grade patterns and error handling
    4. Validation: Test on_cleanup with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Called during cleanup"""
        return True
    
    def on_config_changed(self):
    """
    REASONING CHAIN:
    1. Problem: Function on_config_changed needs clear operational definition
    2. Analysis: Implementation requires specific logic for on_config_changed operation
    3. Solution: Implement on_config_changed with enterprise-grade patterns and error handling
    4. Validation: Test on_config_changed with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Called when configuration changes"""
        pass
    
    def register_event_handlers(self):
    """
    REASONING CHAIN:
    1. Problem: Function register_event_handlers needs clear operational definition
    2. Analysis: Implementation requires specific logic for register_event_handlers operation
    3. Solution: Implement register_event_handlers with enterprise-grade patterns and error handling
    4. Validation: Test register_event_handlers with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Register plugin event handlers"""
        pass
    
    def register_hooks(self):
    """
    REASONING CHAIN:
    1. Problem: Function register_hooks needs clear operational definition
    2. Analysis: Implementation requires specific logic for register_hooks operation
    3. Solution: Implement register_hooks with enterprise-grade patterns and error handling
    4. Validation: Test register_hooks with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Register plugin hooks"""
        pass
    
    def unregister_event_handlers(self):
    """
    REASONING CHAIN:
    1. Problem: Function unregister_event_handlers needs clear operational definition
    2. Analysis: Implementation requires specific logic for unregister_event_handlers operation
    3. Solution: Implement unregister_event_handlers with enterprise-grade patterns and error handling
    4. Validation: Test unregister_event_handlers with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Unregister plugin event handlers"""
        self.event_handlers.clear()
    
    def unregister_hooks(self):
    """
    REASONING CHAIN:
    1. Problem: Function unregister_hooks needs clear operational definition
    2. Analysis: Implementation requires specific logic for unregister_hooks operation
    3. Solution: Implement unregister_hooks with enterprise-grade patterns and error handling
    4. Validation: Test unregister_hooks with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Unregister plugin hooks"""
        self.hooks.clear()

class PluginContainer:
    """
    REASONING CHAIN:
    1. Problem: System component PluginContainer needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for PluginContainer functionality
    3. Solution: Implement PluginContainer with SOLID principles and enterprise patterns
    4. Validation: Test PluginContainer with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Container for plugin instances"""
    
    def __init__(self, metadata: PluginMetadata, plugin_class: Type[PluginInterface]):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self.metadata = metadata
        self.plugin_class = plugin_class
        self.plugin_instance = None
        self.module = None
        self.status = PluginStatus.UNLOADED
        self.load_time = 0.0
        self.error_messages = []
        self.performance_stats = {
            'load_time': 0.0,
            'init_time': 0.0,
            'total_runtime': 0.0,
            'call_count': 0,
            'error_count': 0
        }
    
    def load(self, context: Dict[str, Any] = None) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function load needs clear operational definition
    2. Analysis: Implementation requires specific logic for load operation
    3. Solution: Implement load with enterprise-grade patterns and error handling
    4. Validation: Test load with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Load and initialize plugin"""
        try:
            start_time = utc_now().timestamp()
            self.status = PluginStatus.LOADING
            
            # Create plugin instance
            self.plugin_instance = self.plugin_class()
            
            # Initialize plugin
            if context and hasattr(self.plugin_instance, 'initialize'):
                if not self.plugin_instance.initialize(context):
                    self.status = PluginStatus.ERROR
                    return False
            
            self.status = PluginStatus.ACTIVE
            self.load_time = utc_now().timestamp() - start_time
            self.performance_stats['load_time'] = self.load_time
            
            return True
            
        except Exception as e:
            self.status = PluginStatus.ERROR
            self.error_messages.append(str(e))
            self.performance_stats['error_count'] += 1
            logger.error(f"Failed to load plugin {self.metadata.name}: {e}")
            return False
    
    def unload(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function unload needs clear operational definition
    2. Analysis: Implementation requires specific logic for unload operation
    3. Solution: Implement unload with enterprise-grade patterns and error handling
    4. Validation: Test unload with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Unload plugin"""
        try:
            if self.plugin_instance and hasattr(self.plugin_instance, 'cleanup'):
                self.plugin_instance.cleanup()
            
            self.plugin_instance = None
            self.status = PluginStatus.UNLOADED
            
            # Force garbage collection
            gc.collect()
            
            return True
            
        except Exception as e:
            self.error_messages.append(str(e))
            logger.error(f"Failed to unload plugin {self.metadata.name}: {e}")
            return False
    
    def is_loaded(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function is_loaded needs clear operational definition
    2. Analysis: Implementation requires specific logic for is_loaded operation
    3. Solution: Implement is_loaded with enterprise-grade patterns and error handling
    4. Validation: Test is_loaded with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Check if plugin is loaded"""
        return self.plugin_instance is not None
    
    def is_active(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function is_active needs clear operational definition
    2. Analysis: Implementation requires specific logic for is_active operation
    3. Solution: Implement is_active with enterprise-grade patterns and error handling
    4. Validation: Test is_active with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Check if plugin is active"""
        return self.status == PluginStatus.ACTIVE
    
    def get_info(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_info with enterprise-grade patterns and error handling
    4. Validation: Test get_info with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get plugin information"""
        info = {
            'metadata': self.metadata.to_dict(),
            'status': self.status.value,
            'loaded': self.is_loaded(),
            'active': self.is_active(),
            'load_time': self.load_time,
            'error_messages': self.error_messages,
            'performance_stats': self.performance_stats
        }
        
        if self.plugin_instance and hasattr(self.plugin_instance, 'get_info'):
            info.update(self.plugin_instance.get_info())
        
        return info

class PluginLoader:
    """
    REASONING CHAIN:
    1. Problem: System component PluginLoader needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for PluginLoader functionality
    3. Solution: Implement PluginLoader with SOLID principles and enterprise patterns
    4. Validation: Test PluginLoader with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Plugin loader for discovering and loading plugins"""
    
    def __init__(self, search_paths: List[str] = None):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self.search_paths = search_paths or []
        self.discovered_plugins = {}
        self.loaded_modules = {}
        self.logger = logging.getLogger("plugin_loader")
    
    def discover_plugins(self) -> Dict[str, PluginMetadata]:
    """
    REASONING CHAIN:
    1. Problem: Function discover_plugins needs clear operational definition
    2. Analysis: Implementation requires specific logic for discover_plugins operation
    3. Solution: Implement discover_plugins with enterprise-grade patterns and error handling
    4. Validation: Test discover_plugins with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Discover plugins in search paths"""
        discovered = {}
        
        for search_path in self.search_paths:
            try:
                path = Path(search_path)
                if not path.exists():
                    continue
                
                # Find Python files
                for py_file in path.rglob("*.py"):
                    if py_file.name.startswith("_"):
                        continue
                    
                    try:
                        metadata = self._extract_metadata(py_file)
                        if metadata:
                            discovered[metadata.name] = metadata
                    except Exception as e:
                        self.logger.warning(f"Failed to extract metadata from {py_file}: {e}")
                
            except Exception as e:
                self.logger.error(f"Error discovering plugins in {search_path}: {e}")
        
        self.discovered_plugins = discovered
        return discovered
    
    def _extract_metadata(self, file_path: Path) -> Optional[PluginMetadata]:
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _extract_metadata with enterprise-grade patterns and error handling
    4. Validation: Test _extract_metadata with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Extract metadata from plugin file"""
        try:
            # Calculate file hash
            with open(file_path, 'rb') as f:
                content = f.read()
                file_hash = hashlib.sha256(content).hexdigest()
            
            # Load module
            spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
            if not spec or not spec.loader:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for plugin metadata
            metadata = None
            
            # Check for PLUGIN_METADATA constant
            if hasattr(module, 'PLUGIN_METADATA'):
                metadata_dict = module.PLUGIN_METADATA
                if isinstance(metadata_dict, dict):
                    metadata = PluginMetadata.from_dict(metadata_dict)
            
            # Check for plugin classes
            elif hasattr(module, 'Plugin'):
                plugin_class = module.Plugin
                if hasattr(plugin_class, 'get_metadata'):
                    try:
                        instance = plugin_class()
                        metadata = instance.get_metadata()
                    except Exception:
                        pass
            
            # Look for any class implementing PluginInterface
            else:
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, PluginInterface) and 
                        obj != PluginInterface and 
                        obj.__module__ == module.__name__):
                        try:
                            instance = obj()
                            metadata = instance.get_metadata()
                            break
                        except Exception:
                            continue
            
            if metadata:
                metadata.file_path = str(file_path)
                metadata.file_hash = file_hash
                metadata.file_size = len(content)
                
                return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to extract metadata from {file_path}: {e}")
        
        return None
    
    def load_plugin(self, plugin_name: str) -> Optional[PluginContainer]:
    """
    REASONING CHAIN:
    1. Problem: Function load_plugin needs clear operational definition
    2. Analysis: Implementation requires specific logic for load_plugin operation
    3. Solution: Implement load_plugin with enterprise-grade patterns and error handling
    4. Validation: Test load_plugin with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Load a specific plugin"""
        if plugin_name not in self.discovered_plugins:
            return None
        
        metadata = self.discovered_plugins[plugin_name]
        
        try:
            # Load module
            spec = importlib.util.spec_from_file_location(
                metadata.name, 
                metadata.file_path
            )
            if not spec or not spec.loader:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin class
            plugin_class = None
            
            if hasattr(module, 'Plugin'):
                plugin_class = module.Plugin
            else:
                # Look for any class implementing PluginInterface
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, PluginInterface) and 
                        obj != PluginInterface and 
                        obj.__module__ == module.__name__):
                        plugin_class = obj
                        break
            
            if not plugin_class:
                return None
            
            # Create plugin container
            container = PluginContainer(metadata, plugin_class)
            container.module = module
            
            return container
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return None
    
    def validate_dependencies(self, plugin_name: str, available_plugins: Set[str]) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Input validation needs comprehensive checking logic
    2. Analysis: Validation function requires thorough input analysis
    3. Solution: Implement validate_dependencies with enterprise-grade patterns and error handling
    4. Validation: Test validate_dependencies with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Validate plugin dependencies"""
        if plugin_name not in self.discovered_plugins:
            return False
        
        metadata = self.discovered_plugins[plugin_name]
        
        # Check required dependencies
        for dep in metadata.dependencies:
            if dep not in available_plugins:
                self.logger.error(f"Plugin {plugin_name} missing required dependency: {dep}")
                return False
        
        # Check conflicts
        for conflict in metadata.conflicts:
            if conflict in available_plugins:
                self.logger.error(f"Plugin {plugin_name} conflicts with: {conflict}")
                return False
        
        return True

class UnifiedPluginManager:
    """
    REASONING CHAIN:
    1. Problem: Complex system needs centralized management interface
    2. Analysis: Manager class requires coordinated resource handling and lifecycle management
    3. Solution: Implement UnifiedPluginManager with SOLID principles and enterprise patterns
    4. Validation: Test UnifiedPluginManager with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """
    Unified plugin manager that consolidates all plugin systems
    """
    
    def __init__(self, plugin_directories: List[str] = None):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self.plugin_directories = plugin_directories or []
        self.loader = PluginLoader(self.plugin_directories)
        self.loaded_plugins = {}
        self.plugin_containers = {}
        self.dependencies_resolved = False
        self.system_context = {}
        self.event_system = PluginEventSystem()
        self.hook_system = PluginHookSystem()
        self.logger = logging.getLogger("unified_plugin_manager")
        
        # Performance tracking
        self.stats = {
            'total_plugins': 0,
            'loaded_plugins': 0,
            'active_plugins': 0,
            'failed_plugins': 0,
            'load_time': 0.0,
            'last_scan': None
        }
        
        # Thread safety
        self.lock = threading.RLock()
    
    def scan_plugins(self) -> Dict[str, PluginMetadata]:
    """
    REASONING CHAIN:
    1. Problem: Function scan_plugins needs clear operational definition
    2. Analysis: Implementation requires specific logic for scan_plugins operation
    3. Solution: Implement scan_plugins with enterprise-grade patterns and error handling
    4. Validation: Test scan_plugins with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Scan for available plugins"""
        with self.lock:
            self.logger.info("Scanning for plugins...")
            start_time = utc_now().timestamp()
            
            discovered = self.loader.discover_plugins()
            
            scan_time = utc_now().timestamp() - start_time
            self.stats['total_plugins'] = len(discovered)
            self.stats['last_scan'] = datetime.now(timezone.utc)
            
            self.logger.info(f"Discovered {len(discovered)} plugins in {scan_time:.2f}s")
            
            return discovered
    
    def resolve_dependencies(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function resolve_dependencies needs clear operational definition
    2. Analysis: Implementation requires specific logic for resolve_dependencies operation
    3. Solution: Implement resolve_dependencies with enterprise-grade patterns and error handling
    4. Validation: Test resolve_dependencies with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Resolve plugin dependencies"""
        with self.lock:
            self.logger.info("Resolving plugin dependencies...")
            
            discovered = self.loader.discovered_plugins
            if not discovered:
                self.scan_plugins()
                discovered = self.loader.discovered_plugins
            
            # Build dependency graph
            dependency_graph = {}
            for name, metadata in discovered.items():
                dependency_graph[name] = metadata.dependencies
            
            # Topological sort
            load_order = self._topological_sort(dependency_graph)
            
            if not load_order:
                self.logger.error("Circular dependency detected in plugins")
                return False
            
            # Update load order in metadata
            for i, plugin_name in enumerate(load_order):
                if plugin_name in discovered:
                    discovered[plugin_name].load_order = i
            
            self.dependencies_resolved = True
            self.logger.info("Plugin dependencies resolved successfully")
            
            return True
    
    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _topological_sort with enterprise-grade patterns and error handling
    4. Validation: Test _topological_sort with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Topological sort for dependency resolution"""
        from collections import defaultdict, deque

        # Build reverse graph
        reverse_graph = defaultdict(list)
        in_degree = defaultdict(int)
        
        for node in graph:
            in_degree[node] = 0
        
        for node, deps in graph.items():
            for dep in deps:
                reverse_graph[dep].append(node)
                in_degree[node] += 1
        
        # Kahn's algorithm
        queue = deque([node for node in graph if in_degree[node] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            for neighbor in reverse_graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for cycles
        if len(result) != len(graph):
            return []
        
        return result
    
    def load_plugin(self, plugin_name: str, context: Dict[str, Any] = None) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function load_plugin needs clear operational definition
    2. Analysis: Implementation requires specific logic for load_plugin operation
    3. Solution: Implement load_plugin with enterprise-grade patterns and error handling
    4. Validation: Test load_plugin with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Load a specific plugin"""
        with self.lock:
            if plugin_name in self.loaded_plugins:
                self.logger.warning(f"Plugin {plugin_name} already loaded")
                return True
            
            # Load plugin container
            container = self.loader.load_plugin(plugin_name)
            if not container:
                self.logger.error(f"Failed to load plugin {plugin_name}")
                self.stats['failed_plugins'] += 1
                return False
            
            # Merge context
            plugin_context = self.system_context.copy()
            if context:
                plugin_context.update(context)
            
            # Load and initialize plugin
            if container.load(plugin_context):
                self.loaded_plugins[plugin_name] = container.plugin_instance
                self.plugin_containers[plugin_name] = container
                self.stats['loaded_plugins'] += 1
                
                if container.is_active():
                    self.stats['active_plugins'] += 1
                
                # Register with event system
                self.event_system.register_plugin(plugin_name, container.plugin_instance)
                
                # Register with hook system
                self.hook_system.register_plugin(plugin_name, container.plugin_instance)
                
                self.logger.info(f"Plugin {plugin_name} loaded successfully")
                return True
            else:
                self.stats['failed_plugins'] += 1
                self.logger.error(f"Failed to initialize plugin {plugin_name}")
                return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function unload_plugin needs clear operational definition
    2. Analysis: Implementation requires specific logic for unload_plugin operation
    3. Solution: Implement unload_plugin with enterprise-grade patterns and error handling
    4. Validation: Test unload_plugin with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Unload a specific plugin"""
        with self.lock:
            if plugin_name not in self.loaded_plugins:
                self.logger.warning(f"Plugin {plugin_name} not loaded")
                return True
            
            container = self.plugin_containers.get(plugin_name)
            if container:
                # Unregister from systems
                self.event_system.unregister_plugin(plugin_name)
                self.hook_system.unregister_plugin(plugin_name)
                
                # Unload plugin
                if container.unload():
                    del self.loaded_plugins[plugin_name]
                    del self.plugin_containers[plugin_name]
                    self.stats['loaded_plugins'] -= 1
                    
                    if container.status == PluginStatus.ACTIVE:
                        self.stats['active_plugins'] -= 1
                    
                    self.logger.info(f"Plugin {plugin_name} unloaded successfully")
                    return True
                else:
                    self.logger.error(f"Failed to unload plugin {plugin_name}")
                    return False
            
            return False
    
    def reload_plugin(self, plugin_name: str) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function reload_plugin needs clear operational definition
    2. Analysis: Implementation requires specific logic for reload_plugin operation
    3. Solution: Implement reload_plugin with enterprise-grade patterns and error handling
    4. Validation: Test reload_plugin with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Reload a specific plugin"""
        with self.lock:
            self.logger.info(f"Reloading plugin {plugin_name}")
            
            # Unload if loaded
            if plugin_name in self.loaded_plugins:
                if not self.unload_plugin(plugin_name):
                    return False
            
            # Rescan for updates
            self.scan_plugins()
            
            # Load plugin
            return self.load_plugin(plugin_name)
    
    def load_all_plugins(self) -> Dict[str, bool]:
    """
    REASONING CHAIN:
    1. Problem: Function load_all_plugins needs clear operational definition
    2. Analysis: Implementation requires specific logic for load_all_plugins operation
    3. Solution: Implement load_all_plugins with enterprise-grade patterns and error handling
    4. Validation: Test load_all_plugins with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Load all discovered plugins"""
        with self.lock:
            self.logger.info("Loading all plugins...")
            start_time = utc_now().timestamp()
            
            # Ensure dependencies are resolved
            if not self.dependencies_resolved:
                if not self.resolve_dependencies():
                    return {}
            
            # Load plugins in dependency order
            results = {}
            discovered = self.loader.discovered_plugins
            
            # Sort by load order
            sorted_plugins = sorted(
                discovered.items(),
                key=lambda x: (x[1].priority.value, x[1].load_order)
            )
            
            for plugin_name, metadata in sorted_plugins:
                if not metadata.enabled:
                    continue
                
                try:
                    # Check dependencies
                    available_plugins = set(self.loaded_plugins.keys())
                    if not self.loader.validate_dependencies(plugin_name, available_plugins):
                        results[plugin_name] = False
                        continue
                    
                    # Load plugin
                    results[plugin_name] = self.load_plugin(plugin_name)
                    
                except Exception as e:
                    self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
                    results[plugin_name] = False
            
            load_time = utc_now().timestamp() - start_time
            self.stats['load_time'] = load_time
            
            loaded_count = sum(1 for success in results.values() if success)
            self.logger.info(f"Loaded {loaded_count}/{len(results)} plugins in {load_time:.2f}s")
            
            return results
    
    def enable_plugin(self, plugin_name: str) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function enable_plugin needs clear operational definition
    2. Analysis: Implementation requires specific logic for enable_plugin operation
    3. Solution: Implement enable_plugin with enterprise-grade patterns and error handling
    4. Validation: Test enable_plugin with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Enable a plugin"""
        with self.lock:
            if plugin_name in self.loader.discovered_plugins:
                self.loader.discovered_plugins[plugin_name].enabled = True
                return self.load_plugin(plugin_name)
            return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function disable_plugin needs clear operational definition
    2. Analysis: Implementation requires specific logic for disable_plugin operation
    3. Solution: Implement disable_plugin with enterprise-grade patterns and error handling
    4. Validation: Test disable_plugin with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Disable a plugin"""
        with self.lock:
            if plugin_name in self.loader.discovered_plugins:
                self.loader.discovered_plugins[plugin_name].enabled = False
                return self.unload_plugin(plugin_name)
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_plugin with enterprise-grade patterns and error handling
    4. Validation: Test get_plugin with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get a loaded plugin instance"""
        return self.loaded_plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, PluginInterface]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_all_plugins with enterprise-grade patterns and error handling
    4. Validation: Test get_all_plugins with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get all loaded plugins"""
        return self.loaded_plugins.copy()
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_plugin_info with enterprise-grade patterns and error handling
    4. Validation: Test get_plugin_info with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get plugin information"""
        container = self.plugin_containers.get(plugin_name)
        if container:
            return container.get_info()
        return None
    
    def get_all_plugin_info(self) -> Dict[str, Dict[str, Any]]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_all_plugin_info with enterprise-grade patterns and error handling
    4. Validation: Test get_all_plugin_info with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get information for all plugins"""
        info = {}
        for name, container in self.plugin_containers.items():
            info[name] = container.get_info()
        return info
    
    def get_stats(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_stats with enterprise-grade patterns and error handling
    4. Validation: Test get_stats with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get plugin manager statistics"""
        return self.stats.copy()
    
    def set_system_context(self, context: Dict[str, Any]):
    """
    REASONING CHAIN:
    1. Problem: Data modification needs controlled state management
    2. Analysis: Setter method requires validation and state consistency
    3. Solution: Implement set_system_context with enterprise-grade patterns and error handling
    4. Validation: Test set_system_context with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Set system context for plugins"""
        self.system_context = context
    
    def cleanup(self):
    """
    REASONING CHAIN:
    1. Problem: Function cleanup needs clear operational definition
    2. Analysis: Implementation requires specific logic for cleanup operation
    3. Solution: Implement cleanup with enterprise-grade patterns and error handling
    4. Validation: Test cleanup with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Clean up plugin manager"""
        with self.lock:
            self.logger.info("Cleaning up plugin manager...")
            
            # Unload all plugins
            for plugin_name in list(self.loaded_plugins.keys()):
                self.unload_plugin(plugin_name)
            
            # Clear caches
            self.loaded_plugins.clear()
            self.plugin_containers.clear()
            self.loader.discovered_plugins.clear()
            
            # Clean up subsystems
            self.event_system.cleanup()
            self.hook_system.cleanup()
            
            self.logger.info("Plugin manager cleanup complete")

class PluginEventSystem:
    """
    REASONING CHAIN:
    1. Problem: System component PluginEventSystem needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for PluginEventSystem functionality
    3. Solution: Implement PluginEventSystem with SOLID principles and enterprise patterns
    4. Validation: Test PluginEventSystem with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Plugin event system for inter-plugin communication"""
    
    def __init__(self):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self.event_handlers = {}
        self.plugins = {}
        self.logger = logging.getLogger("plugin_events")
    
    def register_plugin(self, plugin_name: str, plugin_instance: PluginInterface):
    """
    REASONING CHAIN:
    1. Problem: Function register_plugin needs clear operational definition
    2. Analysis: Implementation requires specific logic for register_plugin operation
    3. Solution: Implement register_plugin with enterprise-grade patterns and error handling
    4. Validation: Test register_plugin with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Register plugin with event system"""
        self.plugins[plugin_name] = plugin_instance
        
        # Register plugin's event handlers
        if hasattr(plugin_instance, 'event_handlers'):
            for event_type, handlers in plugin_instance.event_handlers.items():
                self.register_handler(event_type, handlers, plugin_name)
    
    def unregister_plugin(self, plugin_name: str):
    """
    REASONING CHAIN:
    1. Problem: Function unregister_plugin needs clear operational definition
    2. Analysis: Implementation requires specific logic for unregister_plugin operation
    3. Solution: Implement unregister_plugin with enterprise-grade patterns and error handling
    4. Validation: Test unregister_plugin with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Unregister plugin from event system"""
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
        
        # Remove plugin's event handlers
        for event_type, handlers in self.event_handlers.items():
            self.event_handlers[event_type] = [
                (handler, plugin) for handler, plugin in handlers
                if plugin != plugin_name
            ]
    
    def register_handler(self, event_type: str, handler: Callable, plugin_name: str):
    """
    REASONING CHAIN:
    1. Problem: Function register_handler needs clear operational definition
    2. Analysis: Implementation requires specific logic for register_handler operation
    3. Solution: Implement register_handler with enterprise-grade patterns and error handling
    4. Validation: Test register_handler with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        if isinstance(handler, list):
            for h in handler:
                self.event_handlers[event_type].append((h, plugin_name))
        else:
            self.event_handlers[event_type].append((handler, plugin_name))
    
    def emit(self, event_type: str, data: Dict[str, Any], source_plugin: str = None):
    """
    REASONING CHAIN:
    1. Problem: Function emit needs clear operational definition
    2. Analysis: Implementation requires specific logic for emit operation
    3. Solution: Implement emit with enterprise-grade patterns and error handling
    4. Validation: Test emit with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Emit event to handlers"""
        if event_type not in self.event_handlers:
            return
        
        for handler, plugin_name in self.event_handlers[event_type]:
            if source_plugin and plugin_name == source_plugin:
                continue  # Don't send event back to source
            
            try:
                handler(data)
            except Exception as e:
                self.logger.error(f"Event handler failed in plugin {plugin_name}: {e}")
    
    def cleanup(self):
    """
    REASONING CHAIN:
    1. Problem: Function cleanup needs clear operational definition
    2. Analysis: Implementation requires specific logic for cleanup operation
    3. Solution: Implement cleanup with enterprise-grade patterns and error handling
    4. Validation: Test cleanup with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Clean up event system"""
        self.event_handlers.clear()
        self.plugins.clear()

class PluginHookSystem:
    """
    REASONING CHAIN:
    1. Problem: System component PluginHookSystem needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for PluginHookSystem functionality
    3. Solution: Implement PluginHookSystem with SOLID principles and enterprise patterns
    4. Validation: Test PluginHookSystem with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Plugin hook system for modifying behavior"""
    
    def __init__(self):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self.hooks = {}
        self.plugins = {}
        self.logger = logging.getLogger("plugin_hooks")
    
    def register_plugin(self, plugin_name: str, plugin_instance: PluginInterface):
    """
    REASONING CHAIN:
    1. Problem: Function register_plugin needs clear operational definition
    2. Analysis: Implementation requires specific logic for register_plugin operation
    3. Solution: Implement register_plugin with enterprise-grade patterns and error handling
    4. Validation: Test register_plugin with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Register plugin with hook system"""
        self.plugins[plugin_name] = plugin_instance
        
        # Register plugin's hooks
        if hasattr(plugin_instance, 'hooks'):
            for hook_name, handlers in plugin_instance.hooks.items():
                self.register_hook(hook_name, handlers, plugin_name)
    
    def unregister_plugin(self, plugin_name: str):
    """
    REASONING CHAIN:
    1. Problem: Function unregister_plugin needs clear operational definition
    2. Analysis: Implementation requires specific logic for unregister_plugin operation
    3. Solution: Implement unregister_plugin with enterprise-grade patterns and error handling
    4. Validation: Test unregister_plugin with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Unregister plugin from hook system"""
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
        
        # Remove plugin's hooks
        for hook_name, handlers in self.hooks.items():
            self.hooks[hook_name] = [
                (handler, plugin) for handler, plugin in handlers
                if plugin != plugin_name
            ]
    
    def register_hook(self, hook_name: str, handler: Callable, plugin_name: str):
    """
    REASONING CHAIN:
    1. Problem: Function register_hook needs clear operational definition
    2. Analysis: Implementation requires specific logic for register_hook operation
    3. Solution: Implement register_hook with enterprise-grade patterns and error handling
    4. Validation: Test register_hook with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Register hook handler"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        
        if isinstance(handler, list):
            for h in handler:
                self.hooks[hook_name].append((h, plugin_name))
        else:
            self.hooks[hook_name].append((handler, plugin_name))
    
    def call_hook(self, hook_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function call_hook needs clear operational definition
    2. Analysis: Implementation requires specific logic for call_hook operation
    3. Solution: Implement call_hook with enterprise-grade patterns and error handling
    4. Validation: Test call_hook with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Call hook handlers"""
        if hook_name not in self.hooks:
            return data
        
        result = data
        for handler, plugin_name in self.hooks[hook_name]:
            try:
                result = handler(result) or result
            except Exception as e:
                self.logger.error(f"Hook handler failed in plugin {plugin_name}: {e}")
        
        return result
    
    def cleanup(self):
    """
    REASONING CHAIN:
    1. Problem: Function cleanup needs clear operational definition
    2. Analysis: Implementation requires specific logic for cleanup operation
    3. Solution: Implement cleanup with enterprise-grade patterns and error handling
    4. Validation: Test cleanup with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Clean up hook system"""
        self.hooks.clear()
        self.plugins.clear()

# Global plugin manager instance
plugin_manager = None

def get_plugin_manager(plugin_directories: List[str] = None) -> UnifiedPluginManager:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_plugin_manager with enterprise-grade patterns and error handling
    4. Validation: Test get_plugin_manager with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Get or create global plugin manager"""
    global plugin_manager
    
    if plugin_manager is None:
        plugin_manager = UnifiedPluginManager(plugin_directories)
    
    return plugin_manager

def initialize_plugin_system(plugin_directories: List[str] = None, 
    """
    REASONING CHAIN:
    1. Problem: Function initialize_plugin_system needs clear operational definition
    2. Analysis: Implementation requires specific logic for initialize_plugin_system operation
    3. Solution: Implement initialize_plugin_system with enterprise-grade patterns and error handling
    4. Validation: Test initialize_plugin_system with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
                           system_context: Dict[str, Any] = None) -> UnifiedPluginManager:
    """Initialize the unified plugin system"""
    global plugin_manager
    
    plugin_manager = UnifiedPluginManager(plugin_directories)
    
    if system_context:
        plugin_manager.set_system_context(system_context)
    
    # Scan and load plugins
    plugin_manager.scan_plugins()
    plugin_manager.resolve_dependencies()
    
    return plugin_manager

# Export main components
__all__ = [
    'PluginInterface', 'CorePlugin', 'PluginContainer',
    'PluginMetadata', 'PluginLoader', 'UnifiedPluginManager',
    'PluginEventSystem', 'PluginHookSystem',
    'PluginStatus', 'PluginType', 'PluginPriority',
    'get_plugin_manager', 'initialize_plugin_system'
]

if __name__ == '__main__':
    # Test plugin system
    plugin_dirs = ['plugins', 'AI/plugins', 'NoxPanel/plugins']
    
    try:
        manager = initialize_plugin_system(plugin_dirs)
        results = manager.load_all_plugins()
        
        logger.info(f"Plugin system test completed:")
        logger.info(f"Results: {results}")
        logger.info(f"Stats: {manager.get_stats()}")
        
    except Exception as e:
        logger.info(f"Plugin system test failed: {e}")
        traceback.print_exc()