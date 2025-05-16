from enum import IntEnum, StrEnum


class ErrorCodes(IntEnum):
    UNKNOWN = 999


class EnitityStatuses(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class PoolTypes(StrEnum):
    AUTOMATED = "AUTOMATED"
    STATIC = "STATIC"
    GUEST = "GUEST"
    RDS = "RDS"
    APPLICATION = "APPLICATION"
    PHYS = "PHYS"


class OSTypes(StrEnum):
    WINDOWS = "Windows"
    LINUX = "Linux"
    OTHER = "Other"


class ConnectionTypes(StrEnum):
    RDP = "RDP"
    NATIVE_RDP = "NATIVE_RDP"
    GLINT = "GLINT"
