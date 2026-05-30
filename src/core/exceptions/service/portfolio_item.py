from .base import NotFoundError


class PortfolioItemNotFoundError(NotFoundError):
    message = "Portfolio item not found"
