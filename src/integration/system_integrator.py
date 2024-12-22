"""
iHelper Tech System Integrator
Version: 1.0
"""

import logging
from typing import Dict, Optional
import threading
import time
from datetime import datetime
import json

from ..precisionwatch.monitor_manager import MonitorManager
from ..easy_secure.backup_manager import BackupManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('integration.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('SystemIntegrator')

class SystemIntegrator:
    def __init__(self):
        self.monitor_manager = MonitorManager()
        self.backup_manager = BackupManager()
        self.clients = {}
        self.running = False
        self.integration_thread = None
        self.check_interval = 300  # 5 minutes

    def add_client(self, client_name: str, config: dict) -> bool:
        """Add a new client with integrated monitoring and backup."""
        try:
            if client_name not in self.clients:
                # Add to monitoring
                monitor_success = self.monitor_manager.add_client(client_name)
                
                # Add to backup
                backup_success = self.backup_manager.add_client(client_name)
                
                if monitor_success and backup_success:
                    self.clients[client_name] = {
                        'config': config,
                        'status': 'active',
                        'added_date': datetime.now().isoformat()
                    }
                    
                    # Schedule backup if path provided
                    if 'backup_path' in config:
                        self.backup_manager.schedule_backup(
                            client_name,
                            config['backup_path'],
                            config.get('backup_schedule', 'daily')
                        )
                    
                    logger.info(f"Successfully integrated client: {client_name}")
                    return True
                else:
                    logger.error(f"Failed to add client {client_name} to all systems")
                    return False
            return False
            
        except Exception as e:
            logger.error(f"Failed to integrate client {client_name}: {str(e)}")
            return False

    def remove_client(self, client_name: str) -> bool:
        """Remove a client from all systems."""
        try:
            if client_name in self.clients:
                # Remove from monitoring
                monitor_success = self.monitor_manager.remove_client(client_name)
                
                # Remove from backup
                backup_success = self.backup_manager.remove_client(client_name)
                
                if monitor_success and backup_success:
                    del self.clients[client_name]
                    logger.info(f"Successfully removed client: {client_name}")
                    return True
                else:
                    logger.error(f"Failed to remove client {client_name} from all systems")
                    return False
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove client {client_name}: {str(e)}")
            return False

    def start_services(self):
        """Start all integrated services."""
        try:
            # Start monitoring
            self.monitor_manager.start_monitoring()
            
            # Start backup scheduler
            self.backup_manager.run_scheduler()
            
            # Start integration checks
            self.running = True
            self.integration_thread = threading.Thread(target=self._integration_loop)
            self.integration_thread.daemon = True
            self.integration_thread.start()
            
            logger.info("Started all integrated services")
            
        except Exception as e:
            logger.error(f"Failed to start services: {str(e)}")
            raise

    def stop_services(self):
        """Stop all integrated services."""
        try:
            # Stop monitoring
            self.monitor_manager.stop_monitoring()
            
            # Stop integration checks
            self.running = False
            if self.integration_thread:
                self.integration_thread.join()
                
            logger.info("Stopped all integrated services")
            
        except Exception as e:
            logger.error(f"Failed to stop services: {str(e)}")
            raise

    def _integration_loop(self):
        """Main integration check loop."""
        while self.running:
            try:
                for client_name in self.clients:
                    # Get system health
                    health_data = self.monitor_manager.get_client_health(client_name)
                    
                    # Get backup status
                    backup_info = self.backup_manager.get_backup_info(client_name)
                    
                    # Combine and store status
                    status = {
                        'timestamp': datetime.now().isoformat(),
                        'health': health_data,
                        'backup': backup_info
                    }
                    
                    self._store_status(client_name, status)
                    
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Integration loop error: {str(e)}")
                time.sleep(60)  # Wait before retrying

    def _store_status(self, client_name: str, status: dict):
        """Store integrated status data."""
        try:
            # Create status directory if needed
            os.makedirs('status', exist_ok=True)
            
            # Save status file
            filename = f"status/status_{client_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(status, f, indent=4)
                
        except Exception as e:
            logger.error(f"Failed to store status for {client_name}: {str(e)}")

    def get_client_status(self, client_name: str) -> Optional[dict]:
        """Get current integrated status for a client."""
        try:
            if client_name in self.clients:
                health_data = self.monitor_manager.get_client_health(client_name)
                backup_info = self.backup_manager.get_backup_info(client_name)
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'health': health_data,
                    'backup': backup_info,
                    'config': self.clients[client_name]['config']
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get status for {client_name}: {str(e)}")
            return None

    def update_client_config(self, client_name: str, config: dict) -> bool:
        """Update client configuration."""
        try:
            if client_name in self.clients:
                self.clients[client_name]['config'] = config
                
                # Update backup schedule if provided
                if 'backup_path' in config:
                    self.backup_manager.schedule_backup(
                        client_name,
                        config['backup_path'],
                        config.get('backup_schedule', 'daily')
                    )
                
                logger.info(f"Updated configuration for {client_name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to update config for {client_name}: {str(e)}")
            return False

# Example usage:
if __name__ == "__main__":
    # Initialize the system integrator
    integrator = SystemIntegrator()

    # Add a test client
    config = {
        'backup_path': '/path/to/backup',
        'backup_schedule': 'daily'
    }
    
    integrator.add_client("test_client", config)

    # Start all services
    integrator.start_services()

    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop all services on keyboard interrupt
        integrator.stop_services()
