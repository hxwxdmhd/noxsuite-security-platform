from NoxPanel.noxcore.utils.logging_config import get_logger

logger = get_logger(__name__)

"""
Example usage and integration code for NoxGuard Database System
Demonstrates how to integrate the database with existing NoxPanel components
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from NoxPanel.noxcore.database_admin import DatabaseAdmin
from NoxPanel.noxcore.database_service import (
    close_database_service,
    get_database_service,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NoxPanelIntegration:
    """
    REASONING CHAIN:
    1. Problem: System component NoxPanelIntegration needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for NoxPanelIntegration functionality
    3. Solution: Implement NoxPanelIntegration with SOLID principles and enterprise patterns
    4. Validation: Test NoxPanelIntegration with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Integration layer for NoxPanel with enhanced database"""
    
    def __init__(self, db_path: str = None):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Initialize with database service"""
        self.db = get_database_service(db_path)
        self.admin = DatabaseAdmin(db_path)
    
    def setup_system(self):
    """
    REASONING CHAIN:
    1. Problem: Function setup_system needs clear operational definition
    2. Analysis: Implementation requires specific logic for setup_system operation
    3. Solution: Implement setup_system with enterprise-grade patterns and error handling
    4. Validation: Test setup_system with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Setup initial system configuration"""
        logger.info("Setting up NoxPanel system...")
        
        # Check database health
        health = self.admin.health_check()
        if health['health_status'] != 'healthy':
            logger.warning(f"Database health issue: {health}")
            return False
        
        # Ensure required settings exist
        self._setup_default_settings()
        
        # Create sample data if empty
        self._create_sample_data()
        
        logger.info("System setup completed successfully")
        return True
    
    def _setup_default_settings(self):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _setup_default_settings with enterprise-grade patterns and error handling
    4. Validation: Test _setup_default_settings with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Setup default system settings"""
        default_settings = {
            'system_name': 'NoxGuard Panel',
            'version': '1.0.0',
            'theme': 'dark',
            'auto_discovery': 'true',
            'scan_interval': '300',
            'max_devices': '1000',
            'security_level': 'high',
            'backup_enabled': 'true',
            'backup_interval': '24',
            'log_retention_days': '30',
            'knowledge_categories': json.dumps([
                'network', 'security', 'troubleshooting', 'documentation'
            ])
        }
        
        with self.db.db.get_connection() as conn:
            for key, value in default_settings.items():
                conn.execute("""
                    INSERT OR IGNORE INTO settings (key, value, category, description)
                    VALUES (?, ?, 'system', ?)
                """, (key, value, f"Default {key} setting"))
    
    def _create_sample_data(self):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _create_sample_data with enterprise-grade patterns and error handling
    4. Validation: Test _create_sample_data with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Create sample data if database is empty"""
        # Check if we need sample data
        with self.db.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM knowledge_items")
            knowledge_count = cursor.fetchone()[0]
            
            if knowledge_count == 0:
                self._create_sample_knowledge()
            
            cursor.execute("SELECT COUNT(*) FROM tags")
            tag_count = cursor.fetchone()[0]
            
            if tag_count == 0:
                self._create_sample_tags()
    
    def _create_sample_knowledge(self):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _create_sample_knowledge with enterprise-grade patterns and error handling
    4. Validation: Test _create_sample_knowledge with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Create sample knowledge items"""
        admin_user = self.db.users.get_user(username='admin')
        if not admin_user:
            return
        
        sample_knowledge = [
            {
                'title': 'Network Discovery Best Practices',
                'content': '''# Network Discovery Best Practices

## Overview
Network discovery is the process of automatically identifying devices on your network.

## Best Practices
1. Use multiple discovery methods (ping, ARP, SNMP)
2. Schedule regular scans during off-peak hours
3. Maintain an allow/deny list for sensitive devices
4. Document discovered devices properly

## Common Tools
- Nmap for port scanning
- ARP tables for local discovery
- SNMP for managed devices
- Custom scripts for specific protocols
''',
                'category': 'network',
                'content_type': 'markdown',
                'search_keywords': 'network discovery nmap arp snmp scanning'
            },
            {
                'title': 'Security Monitoring Guidelines',
                'content': '''# Security Monitoring Guidelines

## Key Areas to Monitor
- Failed login attempts
- Unusual network traffic patterns
- New device connections
- Port scanning activities
- Privilege escalation attempts

## Response Procedures
1. Document the incident
2. Assess the threat level
3. Contain if necessary
4. Investigate and remediate
5. Update monitoring rules

## Tools Integration
- Log analysis systems
- SIEM solutions
- Network monitoring tools
- Vulnerability scanners
''',
                'category': 'security',
                'content_type': 'markdown',
                'search_keywords': 'security monitoring siem logs alerts'
            },
            {
                'title': 'Troubleshooting Network Connectivity',
                'content': '''# Troubleshooting Network Connectivity

## Step-by-Step Process
1. Check physical connections
2. Verify IP configuration
3. Test local connectivity (ping gateway)
4. Test remote connectivity (ping external)
5. Check DNS resolution
6. Verify routing tables
7. Check firewall rules

## Common Issues
- IP conflicts
- DNS misconfigurations
- Routing problems
- Firewall blocking
- Hardware failures

## Useful Commands
```
ping 8.8.8.8
nslookup domain.com
traceroute destination
netstat -rn
```
''',
                'category': 'troubleshooting',
                'content_type': 'markdown',
                'search_keywords': 'troubleshooting connectivity ping dns routing'
            }
        ]
        
        for item in sample_knowledge:
            knowledge_id = self.db.knowledge.create_knowledge_item(
                title=item['title'],
                content=item['content'],
                category=item['category'],
                author_id=admin_user['id'],
                content_type=item['content_type'],
                search_keywords=item['search_keywords']
            )
            logger.info(f"Created knowledge item: {item['title']} (ID: {knowledge_id})")
    
    def _create_sample_tags(self):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _create_sample_tags with enterprise-grade patterns and error handling
    4. Validation: Test _create_sample_tags with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Create sample tags"""
        admin_user = self.db.users.get_user(username='admin')
        if not admin_user:
            return
        
        sample_tags = [
            {'name': 'network', 'description': 'Network-related content', 'color': '#2196F3'},
            {'name': 'security', 'description': 'Security-related content', 'color': '#F44336'},
            {'name': 'troubleshooting', 'description': 'Troubleshooting guides', 'color': '#FF9800'},
            {'name': 'documentation', 'description': 'General documentation', 'color': '#4CAF50'},
            {'name': 'monitoring', 'description': 'Monitoring and alerting', 'color': '#9C27B0'},
            {'name': 'automation', 'description': 'Automation scripts and tools', 'color': '#00BCD4'},
            {'name': 'urgent', 'description': 'Urgent/critical information', 'color': '#FF5722'},
            {'name': 'tutorial', 'description': 'Step-by-step tutorials', 'color': '#607D8B'}
        ]
        
        for tag in sample_tags:
            tag_id = self.db.tags.create_tag(
                name=tag['name'],
                description=tag['description'],
                color=tag['color'],
                created_by=admin_user['id']
            )
            logger.info(f"Created tag: {tag['name']} (ID: {tag_id})")
    
    def close(self):
    """
    REASONING CHAIN:
    1. Problem: Function close needs clear operational definition
    2. Analysis: Implementation requires specific logic for close operation
    3. Solution: Implement close with enterprise-grade patterns and error handling
    4. Validation: Test close with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Close database connections"""
        close_database_service()

def example_usage():
    """
    REASONING CHAIN:
    1. Problem: Function example_usage needs clear operational definition
    2. Analysis: Implementation requires specific logic for example_usage operation
    3. Solution: Implement example_usage with enterprise-grade patterns and error handling
    4. Validation: Test example_usage with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Example usage of the integrated database system"""
    import shutil
    import tempfile
    
    temp_dir = tempfile.mkdtemp()
    try:
        db_path = os.path.join(temp_dir, 'noxpanel.db')
        
        # Initialize the integration
        integration = NoxPanelIntegration(db_path)
        
        # Setup the system
        integration.setup_system()
        
        # Get admin user
        admin_user = integration.db.users.get_user(username='admin')
        if admin_user:
            # Search knowledge
            results = integration.db.knowledge.search_knowledge_items('network')
            logger.info(f"Found {len(results)} knowledge items")
            
            # Create conversation
            conv_id = integration.db.conversations.create_conversation(
                user_id=admin_user['id'],
                title="Test Chat"
            )
            logger.info(f"Created conversation: {conv_id}")
            
            # Add messages
            integration.db.conversations.add_message(
                conversation_id=conv_id,
                role='user',
                content='How do I troubleshoot network connectivity?'
            )
            
            integration.db.conversations.add_message(
                conversation_id=conv_id,
                role='assistant', 
                content='Here is a step-by-step approach to troubleshoot network connectivity...'
            )
            
            logger.info("Added messages to conversation")
            
            # Generate report
            status = integration.admin.status()
            logger.info(f"Database has {status['table_counts']['knowledge_items']} knowledge items")
        
        logger.info("Example completed successfully!")
        
        integration.close()
        
    finally:
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    example_usage()