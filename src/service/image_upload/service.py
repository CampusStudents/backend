from uuid import uuid4

from src.core.config import settings
from src.core.exceptions.service.aws import InvalidFileTypeError, InvalidUrlError
from src.core.storage.s3 import s3


class ImageUploadService:
    @staticmethod
    async def upload_image(image_data: bytes, file_name: str | None) -> str:
        ext = file_name.rsplit(".", maxsplit=1)[-1].lower() if file_name else ""
        if ext not in settings.aws.image_white_list:
            raise InvalidFileTypeError()
        filename = f"{uuid4()}.{ext}"
        return await s3.upload_file(image_data, filename)

    @staticmethod
    async def delete_image(url: str) -> None:
        if not url:
            raise InvalidUrlError()
        domain = settings.aws.domain.rstrip("/")
        if not url.startswith(f"{domain}/"):
            raise InvalidUrlError()
        filepath = url.removeprefix(f"{domain}/")
        await s3.delete_file(filepath)
