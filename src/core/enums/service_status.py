from enum import IntEnum


class ServiceStatus(IntEnum):
    ENABLED = 0  # ON
    DISABLED = 1  # OFF
    DELETED = 2  # DELETED
