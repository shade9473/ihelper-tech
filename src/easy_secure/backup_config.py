"""
EASY_SECURE™ Backup Configuration
Version: 1.0
"""

import os
import logging
from datetime import datetime
import shutil
import hashlib
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('EASY_SECURE')

class BackupConfig:
    def __init__(self, client_name: str):
        self.client_name = client_name
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_root = os.path.join("backups", client_name)
        self.verify_path = os.path.join("verification", client_name)
        
        # Ensure directories exist
        os.makedirs(self.backup_root, exist_ok=True)
        os.makedirs(self.verify_path, exist_ok=True)

    def create_backup(self, source_path: str) -> dict:
        """Create a backup of the specified directory."""
        try:
            # Create backup directory with timestamp
            backup_dir = os.path.join(self.backup_root, self.timestamp)
            os.makedirs(backup_dir, exist_ok=True)

            # Copy files
            shutil.copytree(source_path, backup_dir, dirs_exist_ok=True)

            # Generate verification data
            verification = self._generate_verification(backup_dir)

            logger.info(f"Backup completed for {self.client_name}")
            return {
                "status": "success",
                "timestamp": self.timestamp,
                "backup_location": backup_dir,
                "verification": verification
            }

        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    def _generate_verification(self, backup_dir: str) -> dict:
        """Generate verification data for backup integrity."""
        verification_data = {}
        
        for root, _, files in os.walk(backup_dir):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                    verification_data[file_path] = file_hash

        # Save verification data
        verify_file = os.path.join(
            self.verify_path, 
            f"verify_{self.timestamp}.json"
        )
        
        with open(verify_file, 'w') as f:
            json.dump(verification_data, f, indent=4)

        return verification_data

    def verify_backup(self, backup_timestamp: str) -> dict:
        """Verify the integrity of a specific backup."""
        try:
            # Load verification data
            verify_file = os.path.join(
                self.verify_path,
                f"verify_{backup_timestamp}.json"
            )
            
            with open(verify_file, 'r') as f:
                stored_verification = json.load(f)

            # Verify each file
            backup_dir = os.path.join(self.backup_root, backup_timestamp)
            current_verification = {}
            
            for root, _, files in os.walk(backup_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                        current_verification[file_path] = file_hash

            # Compare verifications
            is_valid = stored_verification == current_verification
            
            return {
                "status": "success",
                "is_valid": is_valid,
                "timestamp": backup_timestamp
            }

        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    def list_backups(self) -> list:
        """List all backups for the client."""
        try:
            backups = os.listdir(self.backup_root)
            return sorted(backups, reverse=True)
        except Exception as e:
            logger.error(f"Failed to list backups: {str(e)}")
            return []

    def get_backup_info(self, backup_timestamp: str = None) -> dict:
        """Get information about a specific backup or the latest one."""
        try:
            if not backup_timestamp:
                backups = self.list_backups()
                if not backups:
                    return {"status": "error", "message": "No backups found"}
                backup_timestamp = backups[0]

            backup_dir = os.path.join(self.backup_root, backup_timestamp)
            
            # Calculate size
            total_size = 0
            file_count = 0
            
            for root, _, files in os.walk(backup_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                    file_count += 1

            return {
                "status": "success",
                "timestamp": backup_timestamp,
                "size_bytes": total_size,
                "file_count": file_count,
                "location": backup_dir
            }

        except Exception as e:
            logger.error(f"Failed to get backup info: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
