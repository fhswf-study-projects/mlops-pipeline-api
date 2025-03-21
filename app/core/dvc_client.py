import os
import io
import logging
import tempfile
from typing import Any, Union

import boto3
import joblib
from botocore.exceptions import ClientError, NoCredentialsError

from app.constants import EnvConfig


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DVCClient:
    """Handles DVC operations with S3-like remote, using temporary files."""

    _instance = None

    def __new__(cls):
        """Returns the singleton instance or creates a new one if not existend"""
        if cls._instance is None:
            cls._instance = super(DVCClient, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.client = boto3.client(
            "s3",
            aws_access_key_id=os.environ[EnvConfig.S3_ACCESS_KEY_ID.value],
            aws_secret_access_key=os.environ[EnvConfig.S3_SECRET_ACCESS_KEY.value],
            endpoint_url=os.environ[
                EnvConfig.S3_ENDPOINT_URL.value
            ],  # Use None for AWS S3, set URL for MinIO
        )

    def read_data_from(self, source: str, bucket_name=None) -> Union[Any, None]:
        """Reads an object from a S3 bucket

        Args:
            source (str): Path under the object is available.
            bucket_name (str, optional): Bucket name to upload to. Defaults to None.
                If not provided, a default name from the environment space will be used.

        Returns:
            Union[Any, None]: Downloaded (python) object.
        """
        obj = None
        if not bucket_name:
            bucket_name = os.environ[EnvConfig.S3_BUCKET_NAME.value]

        try:
            response = self.client.get_object(Bucket=bucket_name, Key=source)
            buffer = io.BytesIO(response["Body"].read())  # Read data into buffer
            obj = joblib.load(buffer)  # Deserialize object
            logger.info(f"Downloaded {source}")
        except ClientError as e:
            logger.error(f"Error in downloading file: {e}")
        return obj

    def save_data_to(self, obj: Any, destination: str, bucket_name=None) -> bool:
        """Upload an object to a S3 bucket

        Args:
            obj (Any): Object to upload.
            bucket_name (str, optional): Bucket name to upload to. Defaults to None.
                If not provided, a default name from the environment space will be used.
            destination (str): Location under the object should be saved.

        Returns:
           bool: True if file was uploaded, else False.
        """
        if not bucket_name:
            bucket_name = os.environ[EnvConfig.S3_BUCKET_NAME.value]

        try:
            # Check if the bucket exists
            existing_buckets = self.client.list_buckets()
            bucket_names = [
                bucket["Name"] for bucket in existing_buckets.get("Buckets", [])
            ]

            if bucket_name not in bucket_names:
                self.client.create_bucket(Bucket=bucket_name)
                logger.info(f"Created bucket: {bucket_name}")

                # Enable versioning
                self.client.put_bucket_versioning(
                    Bucket=bucket_name, VersioningConfiguration={"Status": "Enabled"}
                )
                logger.info(f"Enabled versioning on {bucket_name}")
            else:
                logger.info(f"Bucket {bucket_name} already exists")

            with tempfile.NamedTemporaryFile(mode="wb+", delete=True) as tmp:
                joblib.dump(obj, tmp.name)
                response = self.client.upload_file(
                    Filename=tmp.name,
                    Bucket=bucket_name,
                    Key=destination,
                )
                logger.warning(f"Response: {response}")
                tmp.close()

            logger.info(f"Uploaded {destination} to {bucket_name}")
        except (NoCredentialsError, ClientError) as e:
            logger.error(f"Error in file upload: {e}")
            return False
        return True
