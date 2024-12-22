"""
iHelper Tech R2 Resource Manager
Cost-effective solution for R2 bucket management and monitoring
"""
import os
import json
import boto3
import logging
from datetime import datetime
from botocore.config import Config
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('r2_manager.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('R2Manager')

class R2ResourceManager:
    def __init__(self):
        self.bucket_name = 'ihelper-tech-bucket'
        self.s3_client = self._initialize_client()
        self.metrics_file = 'metrics/r2_usage.json'

    def _initialize_client(self) -> boto3.client:
        """Initialize R2 client with proper configuration."""
        try:
            return boto3.client(
                's3',
                endpoint_url=f'https://{os.getenv("R2_ACCOUNT_ID")}.r2.cloudflarestorage.com',
                aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('R2_ACCESS_KEY_SECRET'),
                region_name='auto',
                config=Config(
                    retries={'max_attempts': 3},
                    connect_timeout=5,
                    read_timeout=5
                )
            )
        except Exception as e:
            logger.error(f"Failed to initialize R2 client: {str(e)}")
            raise

    def upload_resource(self, local_path: str, r2_key: str, metadata: Dict = None) -> bool:
        """Upload a resource to R2 with metadata."""
        try:
            with open(local_path, 'rb') as file:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=r2_key,
                    Body=file,
                    Metadata=metadata or {}
                )
            logger.info(f"Successfully uploaded {local_path} to {r2_key}")
            self._update_metrics('upload', r2_key)
            return True
        except Exception as e:
            logger.error(f"Failed to upload {local_path}: {str(e)}")
            return False

    def download_resource(self, r2_key: str, local_path: str) -> bool:
        """Download a resource from R2."""
        try:
            self.s3_client.download_file(
                self.bucket_name,
                r2_key,
                local_path
            )
            logger.info(f"Successfully downloaded {r2_key} to {local_path}")
            self._update_metrics('download', r2_key)
            return True
        except Exception as e:
            logger.error(f"Failed to download {r2_key}: {str(e)}")
            return False

    def list_resources(self, prefix: str = '') -> List[Dict]:
        """List resources in the bucket with optional prefix."""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            resources = []
            for obj in response.get('Contents', []):
                metadata = self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=obj['Key']
                )
                resources.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'metadata': metadata.get('Metadata', {})
                })
            return resources
        except Exception as e:
            logger.error(f"Failed to list resources: {str(e)}")
            return []

    def _update_metrics(self, operation: str, resource_key: str):
        """Update usage metrics."""
        try:
            metrics = self._load_metrics()
            timestamp = datetime.now().isoformat()
            
            if 'operations' not in metrics:
                metrics['operations'] = []
            
            metrics['operations'].append({
                'timestamp': timestamp,
                'operation': operation,
                'resource': resource_key
            })
            
            # Keep only last 1000 operations to manage storage
            metrics['operations'] = metrics['operations'][-1000:]
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=self.metrics_file,
                Body=json.dumps(metrics, indent=2).encode()
            )
        except Exception as e:
            logger.error(f"Failed to update metrics: {str(e)}")

    def _load_metrics(self) -> Dict:
        """Load existing metrics or create new."""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=self.metrics_file
            )
            return json.loads(response['Body'].read().decode())
        except:
            return {'operations': []}

    def get_resource_info(self, r2_key: str) -> Optional[Dict]:
        """Get detailed information about a specific resource."""
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=r2_key
            )
            return {
                'key': r2_key,
                'size': response['ContentLength'],
                'last_modified': response['LastModified'].isoformat(),
                'metadata': response.get('Metadata', {}),
                'content_type': response.get('ContentType', 'application/octet-stream')
            }
        except Exception as e:
            logger.error(f"Failed to get info for {r2_key}: {str(e)}")
            return None

    def delete_resource(self, r2_key: str) -> bool:
        """Delete a resource from R2."""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=r2_key
            )
            logger.info(f"Successfully deleted {r2_key}")
            self._update_metrics('delete', r2_key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete {r2_key}: {str(e)}")
            return False

# Example usage
if __name__ == '__main__':
    manager = R2ResourceManager()
    
    # List all resources
    resources = manager.list_resources()
    print(json.dumps(resources, indent=2))
