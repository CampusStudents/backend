from enum import StrEnum


class ProjectStatus(StrEnum):
    NEW = "NEW"
    SELECTION_COMPLETED = "SELECTION_COMPLETED"
    STARTED = "STARTED"
    ENDED = "ENDED"
    CANCELED = "CANCELED"


class ProjectType(StrEnum):
    HACKATHON = "hackathon"
    STARTUP = "startup"
    STUDY = "study"
    COMMERCIAL = "commercial"


class ProjectFormat(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    HYBRID = "hybrid"
