import os
import logging

import boto3
from botocore.exceptions import ClientError

from app.constants import EnvConfig


logger = logging.getLogger()


class S3Client:
    _instance = None

    def __new__(cls):
        """Returns the singleton instance or creates a new one if not existend"""
        if cls._instance is None:
            cls._instance = super(S3Client, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=os.environ[EnvConfig.S3_ENDPOINT_URL.value],
            aws_access_key_id=os.environ[EnvConfig.S3_ACCESS_KEY_ID.value],
            aws_secret_access_key=os.environ[EnvConfig.S3_SECRET_ACCESS_KEY.value],
        )

    def upload_file(
        self, bucket: str, obj=None, object_name=None, file_name=None, extra_args={}
    ):
        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param obj: Object to upload
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """
        if not object_name and not file_name:
            return False

        # If S3 object was not specified, use file_name
        if not object_name:
            object_name = os.path.basename(file_name)

        # Upload the file
        try:
            _ = (
                self.s3_client.upload_file(
                    file_name, bucket, object_name, ExtraArgs=extra_args
                )
                if not obj
                else self.s3_client.upload_fileobj(
                    obj, bucket, object_name, ExtraArgs=extra_args
                )
            )
        except ClientError as e:
            logger.error(e)
            return False

        return True

    def get_metadata(self, bucket: str, object_name: str):
        return self.s3_client.get_object_attributes(
            Bucket=bucket, Key=object_name, ObjectAttributes=["Metadata"]
        )
