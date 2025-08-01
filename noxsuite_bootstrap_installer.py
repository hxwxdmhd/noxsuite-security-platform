
        from datetime import datetime
from NoxPanel.noxcore.utils.logging_config import get_logger
from pathlib import Path
import json
import os
import sys
import urllib.request

from typing import Any, Dict, List, Optional
import platform
import shutil
import subprocess
import tarfile
import tempfile
import traceback
import urllib.error
import zipfile

                from install_noxsuite import main as launcher_main
                from noxsuite_smart_installer_complete import (

                    InstallMode,
                    SmartNoxSuiteInstaller,
                )

                # Pass control to the launcher with original arguments
                launcher_main()
                return True

            except Exception as e:
                self.logger.error(f"Failed to launch main installer: {e}")
                self.logger.debug(f"Traceback: {traceback.format_exc()}")
                return False

        except Exception as e:
            self.logger.error(f"Exception during installer launch: {e}")
            return False

    def run(self, args: List[str]) -> bool:
        """Main bootstrap process"""
        try:
            self.show_banner()

            # Skip bootstrap for certain commands
            if args and args[0] in ["--help", "-h", "--version"]:
                return self.launch_main_installer(args)

            # Run system checks
            if not self.run_system_checks():
                self.logger.error("System checks failed. Cannot continue.")
                return False

            # Bootstrap dependencies
            deps_ok = self.bootstrap_dependencies()
            if not deps_ok:
                self.logger.warning("Some dependencies could not be installed")
                self.logger.warning(
                    "Attempting to continue with reduced functionality..."
                )

            # Launch main installer
            return self.launch_main_installer(args)

        except KeyboardInterrupt:
            self.logger.warning("Bootstrap cancelled by user")
            return False
        except Exception as e:
            self.logger.error(f"Bootstrap failed: {e}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return False


def main():
    """Entry point"""
    bootstrap = NoxSuiteBootstrap()
    success = bootstrap.run(sys.argv[1:])
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
