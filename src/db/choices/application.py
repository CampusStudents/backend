from enum import StrEnum


class ApplicationStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class NotificationType(StrEnum):
    APPLICATION_DECISION = "application_decision"
