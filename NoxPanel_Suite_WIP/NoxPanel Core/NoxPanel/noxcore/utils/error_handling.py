"""
Unified Error Handling Utilities for NoxPanel
Provides standardized error handling, logging, and exception management
"""

import json
import logging
import sys
import traceback
from datetime import datetime, timezone
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union


class ErrorSeverity(Enum):
    """
    REASONING CHAIN:
    1. Problem: System component ErrorSeverity needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for ErrorSeverity functionality
    3. Solution: Implement ErrorSeverity with SOLID principles and enterprise patterns
    4. Validation: Test ErrorSeverity with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Error severity levels for consistent classification."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ErrorCategory(Enum):
    """
    REASONING CHAIN:
    1. Problem: System component ErrorCategory needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for ErrorCategory functionality
    3. Solution: Implement ErrorCategory with SOLID principles and enterprise patterns
    4. Validation: Test ErrorCategory with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Error categories for better organization."""
    SYSTEM = "system"
    DATABASE = "database"
    NETWORK = "network"
    AUTH = "authentication"
    VALIDATION = "validation"
    PLUGIN = "plugin"
    CONFIG = "configuration"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USER = "user"


class NoxPanelError(Exception):
    """
    REASONING CHAIN:
    1. Problem: System component NoxPanelError needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for NoxPanelError functionality
    3. Solution: Implement NoxPanelError with SOLID principles and enterprise patterns
    4. Validation: Test NoxPanelError with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Base exception class for NoxPanel with enhanced metadata."""
    
    def __init__(
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize NoxPanel error with comprehensive metadata.
        
        Args:
            message: Error message
            category: Error category
            severity: Error severity level
            details: Additional error details
            context: Context information when error occurred
            original_exception: Original exception if this is a wrapper
        """
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.context = context or {}
        self.original_exception = original_exception
        self.timestamp = datetime.now(timezone.utc)
        self.error_id = self._generate_error_id()
    
    def _generate_error_id(self) -> str:
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _generate_error_id with enterprise-grade patterns and error handling
    4. Validation: Test _generate_error_id with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Generate unique error ID for tracking."""
        import uuid
        return f"NOX-{self.category.value.upper()}-{str(uuid.uuid4())[:8]}"
    
    def to_dict(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function to_dict needs clear operational definition
    2. Analysis: Implementation requires specific logic for to_dict operation
    3. Solution: Implement to_dict with enterprise-grade patterns and error handling
    4. Validation: Test to_dict with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Convert error to dictionary for serialization."""
        return {
            'error_id': self.error_id,
            'message': self.message,
            'category': self.category.value,
            'severity': self.severity.value,
            'details': self.details,
            'context': self.context,
            'timestamp': self.timestamp.isoformat(),
            'original_exception': str(self.original_exception) if self.original_exception else None,
            'traceback': traceback.format_exc() if self.original_exception else None
        }
    
    def __str__(self) -> str:
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __str__ with enterprise-grade patterns and error handling
    4. Validation: Test __str__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """String representation of error."""
        return f"[{self.error_id}] {self.category.value.upper()}: {self.message}"


class DatabaseError(NoxPanelError):
    """
    REASONING CHAIN:
    1. Problem: System component DatabaseError needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for DatabaseError functionality
    3. Solution: Implement DatabaseError with SOLID principles and enterprise patterns
    4. Validation: Test DatabaseError with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Database-specific error."""
    
    def __init__(self, message: str, **kwargs):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        kwargs.setdefault('category', ErrorCategory.DATABASE)
        kwargs.setdefault('severity', ErrorSeverity.HIGH)
        super().__init__(message, **kwargs)


class NetworkError(NoxPanelError):
    """
    REASONING CHAIN:
    1. Problem: System component NetworkError needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for NetworkError functionality
    3. Solution: Implement NetworkError with SOLID principles and enterprise patterns
    4. Validation: Test NetworkError with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Network-specific error."""
    
    def __init__(self, message: str, **kwargs):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        kwargs.setdefault('category', ErrorCategory.NETWORK)
        kwargs.setdefault('severity', ErrorSeverity.MEDIUM)
        super().__init__(message, **kwargs)


class AuthenticationError(NoxPanelError):
    """
    REASONING CHAIN:
    1. Problem: System component AuthenticationError needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for AuthenticationError functionality
    3. Solution: Implement AuthenticationError with SOLID principles and enterprise patterns
    4. Validation: Test AuthenticationError with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Authentication-specific error."""
    
    def __init__(self, message: str, **kwargs):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        kwargs.setdefault('category', ErrorCategory.AUTH)
        kwargs.setdefault('severity', ErrorSeverity.HIGH)
        super().__init__(message, **kwargs)


class ValidationError(NoxPanelError):
    """
    REASONING CHAIN:
    1. Problem: System component ValidationError needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for ValidationError functionality
    3. Solution: Implement ValidationError with SOLID principles and enterprise patterns
    4. Validation: Test ValidationError with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Validation-specific error."""
    
    def __init__(self, message: str, **kwargs):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        kwargs.setdefault('category', ErrorCategory.VALIDATION)
        kwargs.setdefault('severity', ErrorSeverity.MEDIUM)
        super().__init__(message, **kwargs)


class PluginError(NoxPanelError):
    """
    REASONING CHAIN:
    1. Problem: System component PluginError needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for PluginError functionality
    3. Solution: Implement PluginError with SOLID principles and enterprise patterns
    4. Validation: Test PluginError with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Plugin-specific error."""
    
    def __init__(self, message: str, **kwargs):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        kwargs.setdefault('category', ErrorCategory.PLUGIN)
        kwargs.setdefault('severity', ErrorSeverity.MEDIUM)
        super().__init__(message, **kwargs)


class ConfigurationError(NoxPanelError):
    """
    REASONING CHAIN:
    1. Problem: System component ConfigurationError needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for ConfigurationError functionality
    3. Solution: Implement ConfigurationError with SOLID principles and enterprise patterns
    4. Validation: Test ConfigurationError with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Configuration-specific error."""
    
    def __init__(self, message: str, **kwargs):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        kwargs.setdefault('category', ErrorCategory.CONFIG)
        kwargs.setdefault('severity', ErrorSeverity.HIGH)
        super().__init__(message, **kwargs)


class ErrorHandler:
    """
    REASONING CHAIN:
    1. Problem: Event or request processing needs dedicated handling logic
    2. Analysis: Handler class requires specialized processing patterns and error recovery
    3. Solution: Implement ErrorHandler with SOLID principles and enterprise patterns
    4. Validation: Test ErrorHandler with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Centralized error handling with logging and reporting capabilities."""
    
    def __init__(self, logger_name: str = __name__):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Initialize error handler.
        
        Args:
            logger_name: Name for the logger
        """
        self.logger = logging.getLogger(logger_name)
        self.error_count = 0
        self.recent_errors: List[Dict[str, Any]] = []
        self.max_recent_errors = 100
    
    def handle_error(
    """
    REASONING CHAIN:
    1. Problem: Function handle_error needs clear operational definition
    2. Analysis: Implementation requires specific logic for handle_error operation
    3. Solution: Implement handle_error with enterprise-grade patterns and error handling
    4. Validation: Test handle_error with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self,
        error: Union[Exception, NoxPanelError],
        context: Optional[Dict[str, Any]] = None,
        log_level: int = logging.ERROR
    ) -> str:
        """Handle error with logging and tracking.
        
        Args:
            error: Exception or NoxPanelError to handle
            context: Additional context information
            log_level: Logging level for the error
            
        Returns:
            Error ID for tracking
        """
        self.error_count += 1
        
        # Convert to NoxPanelError if needed
        if not isinstance(error, NoxPanelError):
            nox_error = NoxPanelError(
                message=str(error),
                context=context,
                original_exception=error
            )
        else:
            nox_error = error
            if context:
                nox_error.context.update(context)
        
        # Log the error
        error_dict = nox_error.to_dict()
        
        if nox_error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"CRITICAL ERROR: {nox_error}")
        elif nox_error.severity == ErrorSeverity.HIGH:
            self.logger.error(f"HIGH SEVERITY: {nox_error}")
        elif nox_error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"MEDIUM SEVERITY: {nox_error}")
        else:
            self.logger.info(f"LOW SEVERITY: {nox_error}")
        
        # Add to recent errors
        self.recent_errors.append(error_dict)
        if len(self.recent_errors) > self.max_recent_errors:
            self.recent_errors = self.recent_errors[-self.max_recent_errors:]
        
        return nox_error.error_id
    
    def get_error_summary(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_error_summary with enterprise-grade patterns and error handling
    4. Validation: Test get_error_summary with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get summary of recent errors.
        
        Returns:
            Dictionary containing error statistics
        """
        categories = {}
        severities = {}
        
        for error in self.recent_errors:
            category = error['category']
            severity = error['severity']
            
            categories[category] = categories.get(category, 0) + 1
            severities[severity] = severities.get(severity, 0) + 1
        
        return {
            'total_errors': self.error_count,
            'recent_errors': len(self.recent_errors),
            'categories': categories,
            'severities': severities,
            'last_error': self.recent_errors[-1] if self.recent_errors else None
        }
    
    def clear_recent_errors(self):
    """
    REASONING CHAIN:
    1. Problem: Function clear_recent_errors needs clear operational definition
    2. Analysis: Implementation requires specific logic for clear_recent_errors operation
    3. Solution: Implement clear_recent_errors with enterprise-grade patterns and error handling
    4. Validation: Test clear_recent_errors with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Clear recent errors list."""
        self.recent_errors.clear()
        self.logger.info("Recent errors cleared")


def error_handler(
    """
    REASONING CHAIN:
    1. Problem: Function error_handler needs clear operational definition
    2. Analysis: Implementation requires specific logic for error_handler operation
    3. Solution: Implement error_handler with enterprise-grade patterns and error handling
    4. Validation: Test error_handler with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    category: ErrorCategory = ErrorCategory.SYSTEM,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    reraise: bool = True,
    log_level: int = logging.ERROR
):
    """Decorator for automatic error handling.
    
    Args:
        category: Error category
        severity: Error severity
        reraise: Whether to reraise the exception
        log_level: Logging level
    """
    def decorator(func: Callable) -> Callable:
    """
    Enhanced decorator with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Function decorator needs clear operational definition
    2. Analysis: Implementation requires specific logic for decorator operation
    3. Solution: Implement decorator with enterprise-grade patterns and error handling
    4. Validation: Test decorator with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        @wraps(func)
        def wrapper(*args, **kwargs):
    """
    Enhanced wrapper with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Function wrapper needs clear operational definition
    2. Analysis: Implementation requires specific logic for wrapper operation
    3. Solution: Implement wrapper with enterprise-grade patterns and error handling
    4. Validation: Test wrapper with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = ErrorHandler(func.__module__)
                context = {
                    'function': func.__name__,
                    'args': str(args)[:200],  # Limit to avoid huge logs
                    'kwargs': str(kwargs)[:200]
                }
                
                if isinstance(e, NoxPanelError):
                    error_id = handler.handle_error(e, context, log_level)
                else:
                    nox_error = NoxPanelError(
                        message=str(e),
                        category=category,
                        severity=severity,
                        context=context,
                        original_exception=e
                    )
                    error_id = handler.handle_error(nox_error, context, log_level)
                
                if reraise:
                    raise
                
                return None
        return wrapper
    return decorator


def safe_execute(
    """
    REASONING CHAIN:
    1. Problem: Function safe_execute needs clear operational definition
    2. Analysis: Implementation requires specific logic for safe_execute operation
    3. Solution: Implement safe_execute with enterprise-grade patterns and error handling
    4. Validation: Test safe_execute with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    func: Callable,
    *args,
    default_return: Any = None,
    context: Optional[Dict[str, Any]] = None,
    log_errors: bool = True,
    **kwargs
) -> Any:
    """Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Function arguments
        default_return: Default return value on error
        context: Additional context for error logging
        log_errors: Whether to log errors
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or default_return on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            handler = ErrorHandler()
            error_context = {
                'function': func.__name__ if hasattr(func, '__name__') else str(func),
                'args': str(args)[:200],
                'kwargs': str(kwargs)[:200]
            }
            if context:
                error_context.update(context)
            
            handler.handle_error(e, error_context)
        
        return default_return


def validate_input(
    """
    REASONING CHAIN:
    1. Problem: Input validation needs comprehensive checking logic
    2. Analysis: Validation function requires thorough input analysis
    3. Solution: Implement validate_input with enterprise-grade patterns and error handling
    4. Validation: Test validate_input with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    value: Any,
    validators: List[Callable[[Any], bool]],
    error_message: str = "Validation failed",
    context: Optional[Dict[str, Any]] = None
) -> Any:
    """Validate input with custom validators.
    
    Args:
        value: Value to validate
        validators: List of validation functions
        error_message: Error message on validation failure
        context: Additional context
        
    Returns:
        Validated value
        
    Raises:
        ValidationError: If validation fails
    """
    for validator in validators:
        try:
            if not validator(value):
                raise ValidationError(
                    error_message,
                    details={'value': str(value)[:100], 'validator': validator.__name__},
                    context=context
                )
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(
                f"Validation error: {str(e)}",
                details={'value': str(value)[:100], 'validator': validator.__name__},
                context=context,
                original_exception=e
            )
    
    return value


# Global error handler instance
global_error_handler = ErrorHandler(__name__)


# Convenience functions
def handle_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
    """
    REASONING CHAIN:
    1. Problem: Function handle_error needs clear operational definition
    2. Analysis: Implementation requires specific logic for handle_error operation
    3. Solution: Implement handle_error with enterprise-grade patterns and error handling
    4. Validation: Test handle_error with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Handle error using global handler."""
    return global_error_handler.handle_error(error, context)


def get_error_summary() -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_error_summary with enterprise-grade patterns and error handling
    4. Validation: Test get_error_summary with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Get error summary from global handler."""
    return global_error_handler.get_error_summary()


# Export main utilities
__all__ = [
    'ErrorSeverity',
    'ErrorCategory', 
    'NoxPanelError',
    'DatabaseError',
    'NetworkError',
    'AuthenticationError',
    'ValidationError',
    'PluginError',
    'ConfigurationError',
    'ErrorHandler',
    'error_handler',
    'safe_execute',
    'validate_input',
    'handle_error',
    'get_error_summary'
]
