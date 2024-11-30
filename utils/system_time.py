import subprocess
import platform
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class SystemTime:
    @staticmethod
    def sync_system_time() -> Tuple[bool, str]:
        """
        Attempt to synchronize system time using platform-specific commands
        Returns: (success: bool, message: str)
        """
        try:
            system = platform.system().lower()

            if system == "windows":
                # Windows time sync command
                cmd = ["w32tm", "/resync"]
                subprocess.run(cmd, check=True, capture_output=True)
                return True, "System time synchronized successfully"

            elif system in ("linux", "darwin"):
                # Linux/MacOS time sync command
                cmd = ["sudo", "ntpdate", "pool.ntp.org"]
                subprocess.run(cmd, check=True, capture_output=True)
                return True, "System time synchronized successfully"

            else:
                return False, f"Unsupported operating system: {system}"

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to sync time: {str(e)}")
            return False, "Failed to sync system time. Please sync manually."
        except Exception as e:
            logger.error(f"Error during time sync: {str(e)}")
            return False, "Unexpected error during time synchronization"