import time
import ntplib
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class TimeSync:
    def __init__(self):
        self.ntp_client = ntplib.NTPClient()
        self.ntp_servers = [
            'pool.ntp.org',
            'time.google.com',
            'time.windows.com'
        ]

    def get_ntp_time(self) -> Optional[int]:
        """Get current time from NTP server"""
        for server in self.ntp_servers:
            try:
                response = self.ntp_client.request(server, timeout=5)
                return int(response.tx_time * 1000)  # Convert to milliseconds
            except Exception as e:
                logger.warning(f"Failed to get time from {server}: {e}")
                continue
        return None

    def get_local_time(self) -> int:
        """Get current local time in milliseconds"""
        return int(time.time() * 1000)

    def sync_time(self) -> Tuple[bool, str]:
        """Synchronize time and return status"""
        ntp_time = self.get_ntp_time()
        if not ntp_time:
            return False, "Failed to fetch NTP time from all servers"

        local_time = self.get_local_time()
        time_diff = abs(ntp_time - local_time)

        if time_diff > 1000:  # More than 1 second difference
            logger.warning(f"Time difference detected: {time_diff}ms")
            return False, f"System clock is off by {time_diff}ms"

        return True, "Time is synchronized"