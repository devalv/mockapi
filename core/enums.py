from enum import IntEnum, StrEnum


class IntEnumWithValues(IntEnum):
    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls))


class StrEnumWithValues(StrEnum):
    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls))


class ErrorCodes(IntEnumWithValues):
    UNKNOWN = 999


class EnitityStatuses(StrEnumWithValues):
    CREATING = "CREATING"
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"
    DELETING = "DELETING"
    SERVICE = "SERVICE"
    PARTIAL = "PARTIAL"
    BAD_AUTH = "BAD_AUTH"
    RESERVED = "RESERVED"


class PoolTypes(StrEnumWithValues):
    AUTOMATED = "AUTOMATED"
    STATIC = "STATIC"
    GUEST = "GUEST"
    RDS = "RDS"
    APPLICATION = "APPLICATION"
    PHYS = "PHYS"


class OSTypes(StrEnumWithValues):
    WINDOWS = "Windows"
    LINUX = "Linux"
    OTHER = "Other"


class ConnectionTypes(StrEnumWithValues):
    RDP = "RDP"
    NATIVE_RDP = "NATIVE_RDP"
    GLINT = "GLINT"


class PermissionTypes(StrEnumWithValues):
    USB_REDIR = "USB_REDIR"
    FOLDERS_REDIR = "FOLDERS_REDIR"
    SHARED_CLIPBOARD_CLIENT_TO_GUEST = "SHARED_CLIPBOARD_CLIENT_TO_GUEST"
    SHARED_CLIPBOARD_GUEST_TO_CLIENT = "SHARED_CLIPBOARD_GUEST_TO_CLIENT"
    PRINTERS_REDIR = "PRINTERS_REDIR"
    DRAG_AND_DROP_FILES = "DRAG_AND_DROP_FILES"
    VM_POWER_CONTROL = "VM_POWER_CONTROL"
