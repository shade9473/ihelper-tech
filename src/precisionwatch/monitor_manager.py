"""
PrecisionWatch™ Monitor Manager
Version: 1.0
"""

import time
import logging
import json
import threading
from datetime import datetime
from typing import Dict, Optional
from .monitor_config import SystemMonitor

class MonitorManager:
    def __init__(self):
        self.monitors: Dict[str, SystemMonitor] = {}
        self.running = False
        self.monitor_thread = None
        self.logger = logging.getLogger('PrecisionWatch.manager')
        self.check_interval = 300  # 5 minutes

    def add_client(self, client_name: str) -> bool:
        """Add a new client to monitoring."""
        try:
            if client_name not in self.monitors:
                self.monitors[client_name] = SystemMonitor(client_name)
                self.logger.info(f"Added new client to monitoring: {client_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to add client {client_name}: {str(e)}")
            return False

    def remove_client(self, client_name: str) -> bool:
        """Remove a client from monitoring."""
        try:
            if client_name in self.monitors:
                del self.monitors[client_name]
                self.logger.info(f"Removed client from monitoring: {client_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to remove client {client_name}: {str(e)}")
            return False

    def start_monitoring(self):
        """Start the monitoring process."""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            self.logger.info("Started monitoring service")

    def stop_monitoring(self):
        """Stop the monitoring process."""
        if self.running:
            self.running = False
            if self.monitor_thread:
                self.monitor_thread.join()
            self.logger.info("Stopped monitoring service")

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                for client_name, monitor in self.monitors.items():
                    health_data = monitor.check_system_health()
                    self._process_health_data(client_name, health_data)
                    
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {str(e)}")
                time.sleep(60)  # Wait before retrying

    def _process_health_data(self, client_name: str, health_data: dict):
        """Process and store health check data."""
        try:
            if health_data['status'] == 'success':
                # Save health data
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"health_{client_name}_{timestamp}.json"
                
                with open(filename, 'w') as f:
                    json.dump(health_data, f, indent=4)
                
                # Process alerts
                if health_data.get('alerts'):
                    self._handle_alerts(client_name, health_data['alerts'])
            else:
                self.logger.error(
                    f"Health check failed for {client_name}: {health_data.get('message')}"
                )
                
        except Exception as e:
            self.logger.error(
                f"Failed to process health data for {client_name}: {str(e)}"
            )

    def _handle_alerts(self, client_name: str, alerts: list):
        """Handle system alerts."""
        for alert in alerts:
            self.logger.warning(
                f"Alert for {client_name}: {alert['category']} - {alert['message']}"
            )
            # TODO: Implement notification system
            # self._send_notification(client_name, alert)

    def get_client_health(self, client_name: str) -> Optional[dict]:
        """Get current health status for a client."""
        try:
            if client_name in self.monitors:
                return self.monitors[client_name].check_system_health()
            return None
        except Exception as e:
            self.logger.error(
                f"Failed to get health for {client_name}: {str(e)}"
            )
            return None

    def set_check_interval(self, seconds: int):
        """Update the monitoring check interval."""
        if seconds >= 60:  # Minimum 1 minute
            self.check_interval = seconds
            self.logger.info(f"Updated check interval to {seconds} seconds")
        else:
            self.logger.warning("Check interval must be at least 60 seconds")

    def get_system_info(self, client_name: str) -> Optional[dict]:
        """Get system information for a client."""
        try:
            if client_name in self.monitors:
                return self.monitors[client_name].get_system_info()
            return None
        except Exception as e:
            self.logger.error(
                f"Failed to get system info for {client_name}: {str(e)}"
            )
            return None

# Example usage:
if __name__ == "__main__":
    # Initialize the monitor manager
    manager = MonitorManager()

    # Add a test client
    manager.add_client("test_client")

    # Start monitoring
    manager.start_monitoring()

    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop monitoring on keyboard interrupt
        manager.stop_monitoring()
