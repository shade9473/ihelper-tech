"""
PrecisionWatch™ Monitoring Configuration
Version: 1.0
"""

import os
import logging
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
import socket
import psutil
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('PrecisionWatch')

class SystemMonitor:
    def __init__(self, client_name: str):
        self.client_name = client_name
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time': 2.0  # seconds
        }
        self.alerts = []
        
    def check_system_health(self) -> dict:
        """Check overall system health."""
        try:
            health_data = {
                'timestamp': datetime.now().isoformat(),
                'cpu': self._check_cpu(),
                'memory': self._check_memory(),
                'disk': self._check_disk(),
                'network': self._check_network(),
                'processes': self._check_processes()
            }
            
            return {
                'status': 'success',
                'data': health_data,
                'alerts': self.alerts
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def _check_cpu(self) -> dict:
        """Monitor CPU usage."""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_info = {
            'usage_percent': cpu_percent,
            'core_count': psutil.cpu_count(),
            'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }
        
        if cpu_percent > self.thresholds['cpu_percent']:
            self._add_alert('CPU', f'High CPU usage: {cpu_percent}%')
            
        return cpu_info

    def _check_memory(self) -> dict:
        """Monitor memory usage."""
        memory = psutil.virtual_memory()
        memory_info = {
            'total': memory.total,
            'available': memory.available,
            'percent': memory.percent,
            'used': memory.used
        }
        
        if memory.percent > self.thresholds['memory_percent']:
            self._add_alert('Memory', f'High memory usage: {memory.percent}%')
            
        return memory_info

    def _check_disk(self) -> dict:
        """Monitor disk usage."""
        disk_info = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info[partition.mountpoint] = {
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                }
                
                if usage.percent > self.thresholds['disk_percent']:
                    self._add_alert('Disk', 
                        f'High disk usage on {partition.mountpoint}: {usage.percent}%'
                    )
            except Exception as e:
                logger.warning(f"Couldn't get disk usage for {partition.mountpoint}: {e}")
                
        return disk_info

    def _check_network(self) -> dict:
        """Monitor network connectivity and performance."""
        network_info = {
            'interfaces': psutil.net_if_addrs(),
            'connections': len(psutil.net_connections()),
            'hostname': socket.gethostname()
        }
        
        # Check internet connectivity
        try:
            response = requests.get('https://8.8.8.8', timeout=5)
            network_info['internet_access'] = True
            network_info['latency'] = response.elapsed.total_seconds()
            
            if response.elapsed.total_seconds() > self.thresholds['response_time']:
                self._add_alert('Network', 
                    f'High network latency: {response.elapsed.total_seconds()}s'
                )
        except requests.RequestException:
            network_info['internet_access'] = False
            self._add_alert('Network', 'Internet connectivity issues detected')
            
        return network_info

    def _check_processes(self) -> dict:
        """Monitor system processes."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                if pinfo['cpu_percent'] > 50 or pinfo['memory_percent'] > 50:
                    processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        return {'high_usage_processes': processes}

    def _add_alert(self, category: str, message: str):
        """Add a new alert."""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'message': message
        }
        self.alerts.append(alert)
        logger.warning(f"Alert: {category} - {message}")

    def get_system_info(self) -> dict:
        """Get basic system information."""
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'hostname': socket.gethostname()
        }

    def set_threshold(self, metric: str, value: float):
        """Update monitoring thresholds."""
        if metric in self.thresholds:
            self.thresholds[metric] = value
            logger.info(f"Updated {metric} threshold to {value}")
        else:
            logger.error(f"Invalid metric: {metric}")

    def clear_alerts(self):
        """Clear all current alerts."""
        self.alerts = []
        logger.info("Cleared all alerts")
