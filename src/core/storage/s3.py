import logging
from contextlib import asynccontextmanager

from aiobotocore.session import get_session
from botocore.config import Config
from botocore.exceptions import ClientError

from src.core.config import settings
from src.core.exceptions.service.aws import (
    DeleteFileError,
    InvalidUrlError,
    UploadFileError,
)

logger = logging.getLogger(__name__)


class S3Client:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        endpoint_url: str,
        region_name: str,
        bucket_name: str,
        domain: str,
        folder: str | None = None,
        use_path_style: bool = True,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
            "region_name": region_name,
        }
        if use_path_style:
            self.config["config"] = Config(s3={"addressing_style": "path"})
        self.bucket_name = bucket_name
        self.session = get_session()
        self.folder = folder.strip("/") if folder else None
        self.domain = domain.rstrip("/")

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    def _build_file_path(self, filename: str) -> str:
        clean_filename = filename.lstrip("/")
        if not self.folder:
            return clean_filename
        if clean_filename == self.folder or clean_filename.startswith(
            f"{self.folder}/"
        ):
            return clean_filename
        return f"{self.folder}/{clean_filename}"

    def _ensure_configured(self) -> None:
        if not self.bucket_name or not self.domain:
            raise InvalidUrlError()
        required_config = (
            self.config.get("aws_access_key_id"),
            self.config.get("aws_secret_access_key"),
            self.config.get("endpoint_url"),
        )
        if not all(required_config):
            raise InvalidUrlError()

    async def upload_file(
        self,
        data: bytes,
        filename: str,
        content_type: str | None = None,
    ) -> str:
        self._ensure_configured()
        file_path = self._build_file_path(filename)
        put_object_kwargs = {
            "Bucket": self.bucket_name,
            "Key": file_path,
            "Body": data,
        }
        if content_type:
            put_object_kwargs["ContentType"] = content_type
        try:
            async with self.get_client() as client:
                await client.put_object(**put_object_kwargs)
                return f"{self.domain}/{file_path}"
        except ClientError as e:
            raise UploadFileError from e

    async def delete_file(self, filename: str) -> None:
        self._ensure_configured()
        file_path = self._build_file_path(filename)
        try:
            async with self.get_client() as client:
                await client.delete_object(Bucket=self.bucket_name, Key=file_path)
        except ClientError as e:
            logger.exception("Error deleting file %s", file_path)
            raise DeleteFileError from e


s3 = S3Client(
    access_key=settings.aws.access_key,
    secret_key=settings.aws.secret_key,
    endpoint_url=settings.aws.endpoint_url,
    region_name=settings.aws.region_name,
    bucket_name=settings.aws.bucket_name,
    domain=settings.aws.domain,
    folder=settings.aws.folder,
    use_path_style=settings.aws.use_path_style,
)
