
"""
Brute Force Protection System
Implements rate limiting and account lockout protection
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Set
from collections import defaultdict, deque

class BruteForceProtector:
    def __init__(self):
        # Rate limiting storage (in production, use Redis)
        self.login_attempts = defaultdict(deque)  # IP -> deque of timestamps
        self.failed_logins = defaultdict(int)  # username -> count
        self.locked_accounts = {}  # username -> lock_until_timestamp
        self.blocked_ips = {}  # IP -> block_until_timestamp
        
        # Configuration
        self.max_login_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        self.rate_limit_window = timedelta(minutes=1)
        self.max_requests_per_minute = 10
        self.ip_block_duration = timedelta(hours=1)
        self.max_failed_attempts_per_ip = 20
    
    def check_rate_limit(self, ip_address: str) -> Dict[str, Any]:
        """Check if IP is within rate limits"""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old attempts
        attempts = self.login_attempts[ip_address]
        while attempts and attempts[0] < minute_ago:
            attempts.popleft()
        
        # Check if IP is blocked
        if ip_address in self.blocked_ips:
            if datetime.utcnow() < self.blocked_ips[ip_address]:
                return {
                    "allowed": False,
                    "reason": "IP_BLOCKED",
                    "retry_after": (self.blocked_ips[ip_address] - datetime.utcnow()).total_seconds()
                }
            else:
                # Unblock IP
                del self.blocked_ips[ip_address]
        
        # Check rate limit
        if len(attempts) >= self.max_requests_per_minute:
            return {
                "allowed": False,
                "reason": "RATE_LIMITED",
                "retry_after": 60 - (now - attempts[0])
            }
        
        # Record this attempt
        attempts.append(now)
        
        return {
            "allowed": True,
            "remaining_attempts": self.max_requests_per_minute - len(attempts)
        }
    
    def check_account_lockout(self, username: str) -> Dict[str, Any]:
        """Check if account is locked"""
        if username in self.locked_accounts:
            lock_until = self.locked_accounts[username]
            if datetime.utcnow() < lock_until:
                return {
                    "locked": True,
                    "reason": "ACCOUNT_LOCKED",
                    "unlock_time": lock_until,
                    "retry_after": (lock_until - datetime.utcnow()).total_seconds()
                }
            else:
                # Unlock account
                del self.locked_accounts[username]
                self.failed_logins[username] = 0
        
        return {"locked": False}
    
    def record_failed_login(self, username: str, ip_address: str) -> Dict[str, Any]:
        """Record failed login attempt and check for lockout"""
        self.failed_logins[username] += 1
        failed_count = self.failed_logins[username]
        
        result = {
            "failed_attempts": failed_count,
            "account_locked": False,
            "ip_blocked": False
        }
        
        # Check for account lockout
        if failed_count >= self.max_login_attempts:
            lock_until = datetime.utcnow() + self.lockout_duration
            self.locked_accounts[username] = lock_until
            result["account_locked"] = True
            result["lock_until"] = lock_until
        
        # Check for IP blocking (excessive failed attempts)
        ip_failed_attempts = sum(1 for user, count in self.failed_logins.items() 
                               if self._is_recent_attempt(user, ip_address))
        
        if ip_failed_attempts >= self.max_failed_attempts_per_ip:
            block_until = datetime.utcnow() + self.ip_block_duration
            self.blocked_ips[ip_address] = block_until
            result["ip_blocked"] = True
            result["ip_block_until"] = block_until
        
        return result
    
    def record_successful_login(self, username: str) -> None:
        """Record successful login and reset failed attempts"""
        if username in self.failed_logins:
            del self.failed_logins[username]
        
        if username in self.locked_accounts:
            del self.locked_accounts[username]
    
    def _is_recent_attempt(self, username: str, ip_address: str) -> bool:
        """Check if failed attempt is recent (for IP blocking logic)"""
        # In a real implementation, you'd track IP per failed attempt
        # This is a simplified version
        return True
    
    def get_security_status(self, username: str, ip_address: str) -> Dict[str, Any]:
        """Get comprehensive security status"""
        rate_limit = self.check_rate_limit(ip_address)
        account_status = self.check_account_lockout(username)
        
        return {
            "rate_limit": rate_limit,
            "account_status": account_status,
            "failed_attempts": self.failed_logins.get(username, 0),
            "ip_blocked": ip_address in self.blocked_ips,
            "security_level": self._calculate_security_level(username, ip_address)
        }
    
    def _calculate_security_level(self, username: str, ip_address: str) -> str:
        """Calculate security threat level"""
        failed_attempts = self.failed_logins.get(username, 0)
        
        if ip_address in self.blocked_ips or username in self.locked_accounts:
            return "HIGH_RISK"
        elif failed_attempts >= 3:
            return "MEDIUM_RISK"
        elif failed_attempts >= 1:
            return "LOW_RISK"
        else:
            return "NORMAL"
    
    def cleanup_expired_blocks(self) -> Dict[str, int]:
        """Clean up expired locks and blocks"""
        now = datetime.utcnow()
        cleaned = {"accounts": 0, "ips": 0}
        
        # Clean expired account locks
        expired_accounts = [username for username, lock_time in self.locked_accounts.items() 
                          if now >= lock_time]
        for username in expired_accounts:
            del self.locked_accounts[username]
            self.failed_logins[username] = 0
            cleaned["accounts"] += 1
        
        # Clean expired IP blocks
        expired_ips = [ip for ip, block_time in self.blocked_ips.items() 
                      if now >= block_time]
        for ip in expired_ips:
            del self.blocked_ips[ip]
            cleaned["ips"] += 1
        
        return cleaned
    
    def manually_unlock_account(self, username: str) -> bool:
        """Manually unlock an account (admin function)"""
        if username in self.locked_accounts:
            del self.locked_accounts[username]
            self.failed_logins[username] = 0
            return True
        return False
    
    def manually_unblock_ip(self, ip_address: str) -> bool:
        """Manually unblock an IP (admin function)"""
        if ip_address in self.blocked_ips:
            del self.blocked_ips[ip_address]
            return True
        return False
