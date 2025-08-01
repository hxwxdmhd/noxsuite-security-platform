
"""
Enhanced Session Security Manager
Implements secure session management with advanced features
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Set
import json

class EnhancedSessionManager:
    def __init__(self):
        self.sessions = {}  # In production, use Redis
        self.session_timeout = timedelta(hours=2)
        self.max_sessions_per_user = 5
        self.secure_cookie_config = {
            "httponly": True,
            "secure": True,
            "samesite": "strict",
            "max_age": 7200  # 2 hours
        }
    
    def create_session(self, user_id: str, user_agent: str, ip_address: str) -> str:
        """Create secure session with tracking"""
        session_id = secrets.token_urlsafe(32)
        
        # Create session fingerprint
        fingerprint = self._create_fingerprint(user_agent, ip_address)
        
        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "fingerprint": fingerprint,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "is_active": True
        }
        
        # Cleanup old sessions for user
        self._cleanup_user_sessions(user_id)
        
        self.sessions[session_id] = session_data
        return session_id
    
    def validate_session(self, session_id: str, user_agent: str, ip_address: str) -> Optional[Dict[str, Any]]:
        """Validate session with security checks"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session is active
        if not session.get("is_active", False):
            return None
        
        # Check session timeout
        if datetime.utcnow() - session["last_activity"] > self.session_timeout:
            self.invalidate_session(session_id)
            return None
        
        # Verify fingerprint
        current_fingerprint = self._create_fingerprint(user_agent, ip_address)
        if current_fingerprint != session["fingerprint"]:
            # Potential session hijacking
            self.invalidate_session(session_id)
            return None
        
        # Update last activity
        session["last_activity"] = datetime.utcnow()
        
        return session
    
    def _create_fingerprint(self, user_agent: str, ip_address: str) -> str:
        """Create session fingerprint for security"""
        data = f"{user_agent}:{ip_address}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a specific session"""
        if session_id in self.sessions:
            self.sessions[session_id]["is_active"] = False
            del self.sessions[session_id]
            return True
        return False
    
    def invalidate_all_user_sessions(self, user_id: str) -> int:
        """Invalidate all sessions for a user"""
        invalidated = 0
        to_remove = []
        
        for session_id, session in self.sessions.items():
            if session["user_id"] == user_id:
                to_remove.append(session_id)
                invalidated += 1
        
        for session_id in to_remove:
            del self.sessions[session_id]
        
        return invalidated
    
    def _cleanup_user_sessions(self, user_id: str) -> None:
        """Cleanup old sessions if user has too many"""
        user_sessions = []
        for session_id, session in self.sessions.items():
            if session["user_id"] == user_id:
                user_sessions.append((session_id, session["created_at"]))
        
        # Sort by creation time, newest first
        user_sessions.sort(key=lambda x: x[1], reverse=True)
        
        # Remove oldest sessions if exceeding limit
        if len(user_sessions) >= self.max_sessions_per_user:
            sessions_to_remove = user_sessions[self.max_sessions_per_user-1:]
            for session_id, _ in sessions_to_remove:
                del self.sessions[session_id]
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        now = datetime.utcnow()
        expired = []
        
        for session_id, session in self.sessions.items():
            if now - session["last_activity"] > self.session_timeout:
                expired.append(session_id)
        
        for session_id in expired:
            del self.sessions[session_id]
        
        return len(expired)
    
    def get_active_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active sessions for a user"""
        active_sessions = []
        
        for session_id, session in self.sessions.items():
            if session["user_id"] == user_id and session.get("is_active", False):
                active_sessions.append({
                    "session_id": session_id,
                    "created_at": session["created_at"],
                    "last_activity": session["last_activity"],
                    "ip_address": session["ip_address"],
                    "user_agent": session["user_agent"]
                })
        
        return active_sessions
