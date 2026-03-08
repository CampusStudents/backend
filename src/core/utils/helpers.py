import time
import uuid

def get_time(seconds_precision: bool = True) -> float:
    """
    Get current time.

    :param seconds_precision: If True, returns time in seconds, otherwise in milliseconds.
    :return: Current time as float.
    """
    current_time = time.time()
    if not seconds_precision:
        return current_time * 1000
    return current_time


def get_uuid() -> str:
    """
    Generate a new UUID4.

    :return: UUID4 as string.
    """
    return str(uuid.uuid4())

