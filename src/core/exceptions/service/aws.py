from src.core.exceptions.service.base import (
    AppError,
    InvalidInputError,
    NotFoundError,
)


class AwsError(AppError):
    message = "AWS error"


class UploadFileError(AwsError):
    message = "Error uploading file"


class DeleteFileError(AwsError):
    message = "Error deleting file"


class InvalidUrlError(InvalidInputError):
    message = "Invalid file URL"


class InvalidFileTypeError(InvalidInputError):
    message = "Image type not supported"


class ImageNotFoundError(NotFoundError):
    message = "Image not found"
