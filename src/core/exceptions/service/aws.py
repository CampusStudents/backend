from src.core.exceptions.service.base import (
    BadRequestError,
    InvalidInputError,
    NotFoundError,
)


class UploadFileError(BadRequestError):
    message = "Error uploading file"


class DeleteFileError(BadRequestError):
    message = "Error deleting file"


class InvalidUrlError(InvalidInputError):
    message = "Invalid file URL"


class InvalidFileTypeError(InvalidInputError):
    message = "Image type not supported"


class EmptyFileError(InvalidInputError):
    message = "File is empty"


class FileTooLargeError(InvalidInputError):
    message = "File is too large"


class ImageNotFoundError(NotFoundError):
    message = "Image not found"
