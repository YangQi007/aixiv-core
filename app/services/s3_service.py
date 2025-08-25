import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import uuid
from app.config import settings
import os

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        self.bucket_name = settings.aws_s3_bucket
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename"""
        return filename.split('.')[-1].lower() if '.' in filename else ''
    
    def _get_content_type(self, file_extension: str) -> str:
        """Get the appropriate content type for the file extension"""
        content_types = {
            'pdf': 'application/pdf',
            'tex': 'application/x-tex',
            'latex': 'application/x-tex',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        return content_types.get(file_extension, 'application/octet-stream')
    
    def generate_upload_url(self, filename: str) -> dict:
        """
        Generate a pre-signed URL for uploading a file to S3
        """
        # Generate unique file key with date-based organization
        file_extension = self._get_file_extension(filename)
        
        # Validate file extension
        if file_extension not in ['pdf', 'tex', 'latex']:
            raise ValueError("Only PDF and LaTeX files (.pdf, .tex, .latex) are supported")
        
        try:
            file_uuid = str(uuid.uuid4())
            # Sanitize the original filename to avoid S3 issues
            safe_filename = os.path.basename(filename).replace(" ", "_")
            file_key = f"{file_uuid}_{safe_filename}"
            
            # Get appropriate content type
            content_type = self._get_content_type(file_extension)
            
            # Generate pre-signed URL for PUT operation
            presigned_url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key,
                    'ContentType': content_type
                },
                ExpiresIn=3600  # URL expires in 1 hour
            )
            
            # Construct the final S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{file_key}"
            
            return {
                "upload_url": presigned_url,
                "file_key": file_key,
                "s3_url": s3_url,
                "content_type": content_type,
                "file_extension": file_extension
            }
            
        except ClientError as e:
            raise Exception(f"S3 error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error generating upload URL: {str(e)}")
    
    def delete_file(self, file_key: str) -> bool:
        """
        Delete a file from S3
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except ClientError as e:
            raise Exception(f"Error deleting file from S3: {str(e)}")
    
    def file_exists(self, file_key: str) -> bool:
        """
        Check if a file exists in S3
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise Exception(f"Error checking file existence: {str(e)}")
    
    def upload_avatar(self, file_content: bytes, filename: str, user_id: str) -> str:
        """
        Upload avatar image directly to S3
        Returns the S3 URL of the uploaded avatar
        """
        file_extension = self._get_file_extension(filename)
        
        # Validate file extension for avatars
        if file_extension not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            raise ValueError("Only image files (jpg, jpeg, png, gif, webp) are supported for avatars")
        
        try:
            # Generate unique file key with user ID prefix for organization
            file_uuid = str(uuid.uuid4())
            file_key = f"avatars/{user_id}/{file_uuid}.{file_extension}"
            
            # Get appropriate content type
            content_type = self._get_content_type(file_extension)
            
            # Upload directly to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
                # Set cache control for avatars
                CacheControl='max-age=31536000'
            )
            
            # Construct the final S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{file_key}"
            
            return s3_url
            
        except ClientError as e:
            raise Exception(f"S3 error uploading avatar: {str(e)}")
        except Exception as e:
            raise Exception(f"Error uploading avatar: {str(e)}")
    
    def delete_avatar(self, avatar_url: str) -> bool:
        """
        Delete an avatar from S3 based on its URL
        """
        try:
            # Extract file key from S3 URL
            if f"{self.bucket_name}.s3" in avatar_url:
                file_key = avatar_url.split(f"{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/")[-1]
                return self.delete_file(file_key)
            return False
        except Exception as e:
            raise Exception(f"Error deleting avatar: {str(e)}")

# Create a singleton instance
s3_service = S3Service() 