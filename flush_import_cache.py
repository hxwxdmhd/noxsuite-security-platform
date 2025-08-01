#!/usr/bin/env python3
"""
Python Import Cache Flusher
==========================
Utility to flush Python's import cache and reload modules.
"""

import sys
import importlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImportCacheFlusher:
    """Flush Python's import cache to ensure modules are reloaded correctly"""
    
    def __init__(self):
        self.modules_flushed = 0
        self.modules_reloaded = 0
        self.errors = []
    
    def flush_module(self, module_name):
        """Flush a specific module from sys.modules"""
        try:
            if module_name in sys.modules:
                del sys.modules[module_name]
                self.modules_flushed += 1
                logger.info(f"✅ Flushed module: {module_name}")
                return True
            else:
                logger.info(f"ℹ️ Module not loaded: {module_name}")
                return False
        except Exception as e:
            error_msg = f"❌ Error flushing {module_name}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def reload_module(self, module_name):
        """Reload a module after flushing it"""
        try:
            if self.flush_module(module_name):
                module = importlib.import_module(module_name)
                importlib.reload(module)
                self.modules_reloaded += 1
                logger.info(f"✅ Reloaded module: {module_name}")
                return module
            return None
        except Exception as e:
            error_msg = f"❌ Error reloading {module_name}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return None
    
    def flush_related_modules(self, base_name):
        """Flush all modules related to a base module name"""
        related_modules = []
        for module_name in list(sys.modules.keys()):
            if module_name == base_name or module_name.startswith(f"{base_name}."):
                related_modules.append(module_name)
        
        # Flush in reverse order to handle dependencies
        for module_name in sorted(related_modules, reverse=True):
            self.flush_module(module_name)
        
        return related_modules

if __name__ == "__main__":
    flusher = ImportCacheFlusher()
    
    # Modules to flush
    modules_to_flush = [
        "mariadb_dev_setup",
        "noxsuite_fastapi_server", 
        "rbac_mfa_extension",
        "backend.models.mariadb_user"
    ]
    
    for module in modules_to_flush:
        flusher.flush_related_modules(module)
    
    print(f"\nSummary: Flushed {flusher.modules_flushed} modules")
    if flusher.errors:
        print(f"Encountered {len(flusher.errors)} errors:")
        for error in flusher.errors:
            print(f"  - {error}")
    else:
        print("All modules flushed successfully!")
    
    print("\nIMPORTANT: Restart your FastAPI server to apply changes.")
