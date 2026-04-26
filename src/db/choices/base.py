from enum import Enum


def enum_values(enum: type[Enum]) -> list[str]:
    return [item.value for item in enum]
