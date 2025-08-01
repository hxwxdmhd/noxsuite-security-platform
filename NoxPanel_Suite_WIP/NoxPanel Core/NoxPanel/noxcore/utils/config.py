import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)


class NoxConfig:
    """
    REASONING CHAIN:
    1. Problem: System component NoxConfig needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for NoxConfig functionality
    3. Solution: Implement NoxConfig with SOLID principles and enterprise patterns
    4. Validation: Test NoxConfig with comprehensive unit and integration tests

    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Configuration management for NoxPanel with robust error handling and validation."""

    def __init__(self, config_dir: str = "config") -> None:
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements

    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
      """Initialize configuration manager.

        Args:
            config_dir: Directory path for configuration files
        """
       self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "noxpanel.json"
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
    """
    REASONING CHAIN:
    1. Problem: Function load_config needs clear operational definition
    2. Analysis: Implementation requires specific logic for load_config operation
    3. Solution: Implement load_config with enterprise-grade patterns and error handling
    4. Validation: Test load_config with edge cases and performance requirements

    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
      """Load configuration from file with error handling."""
       try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                self.config = self.get_default_config()
                self.save_config()
                logger.info("Default configuration created")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config = self.get_default_config()

    def save_config(self) -> None:
    """
    REASONING CHAIN:
    1. Problem: Function save_config needs clear operational definition
    2. Analysis: Implementation requires specific logic for save_config operation
    3. Solution: Implement save_config with enterprise-grade patterns and error handling
    4. Validation: Test save_config with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
      """Save configuration to file with error handling."""
       try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.debug(f"Configuration saved to {self.config_file}")
        except (IOError, OSError) as e:
            logger.error(f"Failed to save configuration: {e}")
            raise

    def get_default_config(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_default_config with enterprise-grade patterns and error handling
    4. Validation: Test get_default_config with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
      """Get default configuration with comprehensive settings.

        Returns:
            Default configuration dictionary
        """
       return {
            "app": {
                "name": "NoxPanel",
                "version": "1.0.0",
                "debug": False,
                "host": "0.0.0.0",
                "port": 5000
            },
            "security": {
                "max_script_runtime": 300,
                "allowed_script_extensions": [".py", ".sh"],
                "require_auth": True,
                "session_timeout": 3600,
                "max_login_attempts": 5
            },
            "logging": {
                "level": "INFO",
                "max_log_size": "10MB",
                "backup_count": 5,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "database": {
                "type": "sqlite",
                "path": "data/db/noxpanel.db",
                "pool_size": 10,
                "timeout": 30.0
            },
            "theme": {
                "default": "dark",
                "custom_css": "",
                "available_themes": ["dark", "light", "auto"]
            },
            "plugins": {
                "enabled": True,
                "auto_load": True,
                "paths": ["plugins", "external_plugins"]
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
    """
    REASONING CHAIN:
    1. Problem: Function get needs clear operational definition
    2. Analysis: Implementation requires specific logic for get operation
    3. Solution: Implement get with enterprise-grade patterns and error handling
    4. Validation: Test get with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
      """Get configuration value using dot notation.

        Args:
            key: Configuration key using dot notation (e.g., 'app.debug')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
       try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        except (AttributeError, KeyError, TypeError):
            logger.warning(
                f"Configuration key '{key}' not found, using default")
            return default

    def set(self, key: str, value: Any) -> None:
    """
    REASONING CHAIN:
    1. Problem: Function set needs clear operational definition
    2. Analysis: Implementation requires specific logic for set operation
    3. Solution: Implement set with enterprise-grade patterns and error handling
    4. Validation: Test set with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
      """Set configuration value using dot notation.

        Args:
            key: Configuration key using dot notation (e.g., 'app.debug')
            value: Value to set
        """
       try:
            keys = key.split('.')
            config = self.config
            for k in keys[:-1]:
                config = config.setdefault(k, {})
            config[keys[-1]] = value
            self.save_config()
            logger.debug(f"Configuration key '{key}' set to '{value}'")
        except (AttributeError, KeyError, TypeError) as e:
            logger.error(f"Failed to set configuration key '{key}': {e}")
            raise

    def update(self, new_config: Dict[str, Any]) -> None:
    """
    REASONING CHAIN:
    1. Problem: Function update needs clear operational definition
    2. Analysis: Implementation requires specific logic for update operation
    3. Solution: Implement update with enterprise-grade patterns and error handling
    4. Validation: Test update with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
      """Update configuration with new values.

        Args:
            new_config: Dictionary with new configuration values
        """
       try:
            self._deep_update(self.config, new_config)
            self.save_config()
            logger.info("Configuration updated successfully")
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            raise

    def _deep_update(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _deep_update with enterprise-grade patterns and error handling
    4. Validation: Test _deep_update with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
      """Recursively update nested dictionaries.

        Args:
            base_dict: Base dictionary to update
            update_dict: Dictionary with updates
        """
       for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def validate_config(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Input validation needs comprehensive checking logic
    2. Analysis: Validation function requires thorough input analysis
    3. Solution: Implement validate_config with enterprise-grade patterns and error handling
    4. Validation: Test validate_config with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
      """Validate configuration integrity.

        Returns:
            True if configuration is valid, False otherwise
        """
       required_sections = ['app', 'security', 'logging']

        for section in required_sections:
            if section not in self.config:
                logger.error(
                    f"Missing required configuration section: {section}")
                return False

        # Validate specific settings
        if not isinstance(self.get('app.port'), int) or not (1 <= self.get('app.port') <= 65535):
            logger.error("Invalid port configuration")
            return False

        if not isinstance(self.get('security.max_script_runtime'), int) or self.get('security.max_script_runtime') <= 0:
            logger.error("Invalid script runtime configuration")
            return False

        logger.debug("Configuration validation passed")
        return True

    def reset_to_defaults(self) -> None:
    """
    REASONING CHAIN:
    1. Problem: Function reset_to_defaults needs clear operational definition
    2. Analysis: Implementation requires specific logic for reset_to_defaults operation
    3. Solution: Implement reset_to_defaults with enterprise-grade patterns and error handling
    4. Validation: Test reset_to_defaults with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
      """Reset configuration to default values."""
       self.config = self.get_default_config()
        self.save_config()
        logger.info("Configuration reset to defaults")
