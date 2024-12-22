"""
EASY_SECURE™ Backup Manager
Version: 1.0
"""

import os
import schedule
import time
import logging
from datetime import datetime
from typing import List, Dict
from .backup_config import BackupConfig

class BackupManager:
    def __init__(self):
        self.clients: Dict[str, BackupConfig] = {}
        self.logger = logging.getLogger('EASY_SECURE.manager')

    def add_client(self, client_name: str) -> bool:
        """Add a new client to the backup system."""
        try:
            if client_name not in self.clients:
                self.clients[client_name] = BackupConfig(client_name)
                self.logger.info(f"Added new client: {client_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to add client {client_name}: {str(e)}")
            return False

    def remove_client(self, client_name: str) -> bool:
        """Remove a client from the backup system."""
        try:
            if client_name in self.clients:
                del self.clients[client_name]
                self.logger.info(f"Removed client: {client_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to remove client {client_name}: {str(e)}")
            return False

    def schedule_backup(self, client_name: str, source_path: str, 
                       schedule_type: str = "daily") -> bool:
        """Schedule automated backups for a client."""
        try:
            if client_name not in self.clients:
                self.logger.error(f"Client {client_name} not found")
                return False

            def backup_job():
                self.create_backup(client_name, source_path)

            if schedule_type == "daily":
                schedule.every().day.at("02:00").do(backup_job)
            elif schedule_type == "weekly":
                schedule.every().monday.at("02:00").do(backup_job)
            else:
                self.logger.error(f"Invalid schedule type: {schedule_type}")
                return False

            self.logger.info(
                f"Scheduled {schedule_type} backup for {client_name}"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to schedule backup for {client_name}: {str(e)}"
            )
            return False

    def create_backup(self, client_name: str, source_path: str) -> dict:
        """Create a backup for a specific client."""
        try:
            if client_name not in self.clients:
                return {
                    "status": "error",
                    "message": f"Client {client_name} not found"
                }

            result = self.clients[client_name].create_backup(source_path)
            if result["status"] == "success":
                self.logger.info(
                    f"Created backup for {client_name} at {result['timestamp']}"
                )
            return result

        except Exception as e:
            self.logger.error(
                f"Failed to create backup for {client_name}: {str(e)}"
            )
            return {
                "status": "error",
                "message": str(e)
            }

    def verify_backup(self, client_name: str, 
                     backup_timestamp: str = None) -> dict:
        """Verify a backup for a specific client."""
        try:
            if client_name not in self.clients:
                return {
                    "status": "error",
                    "message": f"Client {client_name} not found"
                }

            result = self.clients[client_name].verify_backup(backup_timestamp)
            if result["status"] == "success":
                self.logger.info(
                    f"Verified backup for {client_name} at {result['timestamp']}"
                )
            return result

        except Exception as e:
            self.logger.error(
                f"Failed to verify backup for {client_name}: {str(e)}"
            )
            return {
                "status": "error",
                "message": str(e)
            }

    def get_client_backups(self, client_name: str) -> List[str]:
        """Get a list of all backups for a specific client."""
        try:
            if client_name not in self.clients:
                self.logger.error(f"Client {client_name} not found")
                return []

            return self.clients[client_name].list_backups()

        except Exception as e:
            self.logger.error(
                f"Failed to get backups for {client_name}: {str(e)}"
            )
            return []

    def get_backup_info(self, client_name: str, 
                       backup_timestamp: str = None) -> dict:
        """Get information about a specific backup."""
        try:
            if client_name not in self.clients:
                return {
                    "status": "error",
                    "message": f"Client {client_name} not found"
                }

            return self.clients[client_name].get_backup_info(backup_timestamp)

        except Exception as e:
            self.logger.error(
                f"Failed to get backup info for {client_name}: {str(e)}"
            )
            return {
                "status": "error",
                "message": str(e)
            }

    def run_scheduler(self):
        """Run the backup scheduler."""
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            self.logger.info("Backup scheduler stopped")
        except Exception as e:
            self.logger.error(f"Scheduler error: {str(e)}")

# Example usage:
if __name__ == "__main__":
    # Initialize the backup manager
    manager = BackupManager()

    # Add a test client
    manager.add_client("test_client")

    # Schedule daily backup
    manager.schedule_backup(
        "test_client",
        "/path/to/backup",
        "daily"
    )

    # Run the scheduler
    manager.run_scheduler()
