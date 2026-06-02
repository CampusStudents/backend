import mimetypes
from uuid import uuid4

from src.core.config import settings
from src.core.exceptions.service.aws import (
    EmptyFileError,
    FileTooLargeError,
    InvalidFileTypeError,
    InvalidUrlError,
)
from src.core.storage.s3 import s3


class ImageUploadService:
    @staticmethod
    async def upload_image(
        image_data: bytes,
        file_name: str | None,
        content_type: str | None = None,
        folder: str | None = None,
    ) -> str:
        if not image_data:
            raise EmptyFileError()
        if len(image_data) > settings.aws.max_image_size_bytes:
            raise FileTooLargeError()
        ext = file_name.rsplit(".", maxsplit=1)[-1].lower() if file_name else ""
        if ext not in settings.aws.image_white_list:
            raise InvalidFileTypeError()
        expected_content_type = mimetypes.types_map.get(f".{ext}")
        content_type = content_type or expected_content_type
        if not content_type or not content_type.startswith("image/"):
            raise InvalidFileTypeError()
        filename = f"{uuid4()}.{ext}"
        if folder:
            filename = f"{folder.strip('/')}/{filename}"
        return await s3.upload_file(image_data, filename, content_type)

    @staticmethod
    async def delete_image(url: str) -> None:
        if not url:
            raise InvalidUrlError()
        domain = settings.aws.domain.rstrip("/")
        if not url.startswith(f"{domain}/"):
            raise InvalidUrlError()
        filepath = url.removeprefix(f"{domain}/")
        await s3.delete_file(filepath)
