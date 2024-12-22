"""
CloudFlare R2 Connection Test for iHelper Tech Bucket
"""
import os
import boto3
import logging
from botocore.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('R2Test')

def test_r2_connection():
    """Test CloudFlare R2 connection and operations."""
    try:
        # R2 credentials
        r2_access_key = os.getenv('R2_ACCESS_KEY_ID')
        r2_secret_key = os.getenv('R2_ACCESS_KEY_SECRET')
        account_id = os.getenv('R2_ACCOUNT_ID')

        if not all([r2_access_key, r2_secret_key, account_id]):
            raise ValueError("Missing required R2 credentials")

        # Initialize S3 client for R2
        s3 = boto3.client(
            's3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=r2_access_key,
            aws_secret_access_key=r2_secret_key,
            region_name='auto',  # R2 automatically handles regions
            config=Config(
                retries={'max_attempts': 3},
                connect_timeout=5,
                read_timeout=5
            )
        )

        # Test bucket operations
        test_bucket = 'ihelper-tech-bucket'  # Updated to match your bucket
        test_file = 'test/connection_test.txt'
        test_content = f'R2 Connection Test - {os.getenv("GITHUB_SHA", "local")}'

        # Check bucket exists
        try:
            s3.head_bucket(Bucket=test_bucket)
            logger.info(f"✅ Connected to bucket '{test_bucket}'")
        except Exception as e:
            logger.error(f"❌ Failed to connect to bucket: {str(e)}")
            return False

        # Upload test file
        logger.info("Testing file upload...")
        s3.put_object(
            Bucket=test_bucket,
            Key=test_file,
            Body=test_content.encode(),
            Metadata={
                'purpose': 'connection_test',
                'environment': os.getenv('GITHUB_ENVIRONMENT', 'local'),
                'timestamp': os.getenv('GITHUB_SHA', 'local')
            }
        )

        # Download and verify
        logger.info("Testing file download...")
        response = s3.get_object(
            Bucket=test_bucket,
            Key=test_file
        )
        downloaded_content = response['Body'].read().decode()

        if downloaded_content == test_content:
            logger.info("✅ R2 connection test successful!")
            
            # Cleanup test file
            logger.info("Cleaning up test file...")
            s3.delete_object(
                Bucket=test_bucket,
                Key=test_file
            )
            
            return True
        else:
            logger.error("❌ Content verification failed")
            return False

    except Exception as e:
        logger.error(f"❌ R2 connection test failed: {str(e)}")
        return False

if __name__ == '__main__':
    test_r2_connection()
