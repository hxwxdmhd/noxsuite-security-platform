
"""
Advanced Password Validation System
Implements comprehensive password security policies
"""

import re
import hashlib
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

class AdvancedPasswordValidator:
    def __init__(self):
        self.min_length = 12
        self.max_length = 128
        self.common_passwords = self._load_common_passwords()
        self.password_history = {}  # In production, use database
    
    def validate_password(self, password: str, username: str = None) -> Tuple[bool, List[str]]:
        """
        Comprehensive password validation
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        # Length validation
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")
        
        if len(password) > self.max_length:
            errors.append(f"Password must not exceed {self.max_length} characters")
        
        # Character requirements
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Username similarity check
        if username and username.lower() in password.lower():
            errors.append("Password must not contain username")
        
        # Common password check
        if password.lower() in self.common_passwords:
            errors.append("Password is too common, please choose a more unique password")
        
        # Sequential characters check
        if self._has_sequential_chars(password):
            errors.append("Password must not contain sequential characters (e.g., 123, abc)")
        
        # Repeated characters check
        if self._has_excessive_repeats(password):
            errors.append("Password must not have excessive repeated characters")
        
        return len(errors) == 0, errors
    
    def _load_common_passwords(self) -> set:
        """Load common passwords list"""
        common = {
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "dragon", "master",
            "password1", "123456789", "12345678", "123123", "1234567890"
        }
        return common
    
    def _has_sequential_chars(self, password: str) -> bool:
        """Check for sequential characters"""
        sequences = ["123", "234", "345", "456", "567", "678", "789",
                    "abc", "bcd", "cde", "def", "efg", "fgh", "ghi",
                    "qwe", "wer", "ert", "rty", "tyu", "yui", "uio"]
        
        password_lower = password.lower()
        return any(seq in password_lower for seq in sequences)
    
    def _has_excessive_repeats(self, password: str) -> bool:
        """Check for excessive repeated characters"""
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                return True
        return False
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a cryptographically secure password"""
        import secrets
        import string
        
        # Character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = "!@#$%^&*(),.?":{}|<>"
        
        # Ensure at least one character from each set
        password = [
            secrets.choice(uppercase),
            secrets.choice(lowercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]
        
        # Fill remaining length
        all_chars = lowercase + uppercase + digits + special
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        import bcrypt
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
