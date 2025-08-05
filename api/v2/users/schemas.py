from typing import Annotated

from pydantic import BaseModel, Field

from core.enums import (
    AudioPlaybakModes,
    ConnectionTypes,
    ImageFormats,
    UserSCPermission,
    VideoCompressionCodecs,
)
from core.schemas import Token


class LoginInputModel(BaseModel):
    username: str
    password: str
    ldap: bool


class TokenResponseModel(BaseModel):
    data: Token


# TODO: перепроверить названия полей


class ServiceSettingsModel(BaseModel):
    """
    Настройки хранящиеся на клиенте:
        Архивировать логи?
        Масштабирование?
        Язык?
        Цветовая схема?
    """

    automatically_install_updates: bool = False
    root_mode_enabled: bool = False
    file_logging_enabled: bool = False
    network_timeout: Annotated[int, Field(ge=5, le=60)] = 15
    debug_mode_enabled: bool = False
    windows_update_url: str | None = None


class SecuritySettingsModel(BaseModel):
    otp_enabled: bool = False
    adfs_enabled: bool = False
    hardware_token_enabled: bool = False
    store_password_enabled: bool = False
    domain_username_format_enabled: bool = False
    sc_permissions: list[UserSCPermission] = []


class WSChanMapping(BaseModel):
    channel: str
    event: str


class MainSettingsModel(BaseModel):
    """
    Настройки хранящиеся на клиенте:
        Адрес подключения (Disp || GW)
        Порт подключения (Disp || GW)
        Протокол подключения (http || https)
    """

    default_remote_protocol: ConnectionTypes = ConnectionTypes.GLINT
    last_pool_autoconnect_ebabled: bool = False
    ws_channels: list[WSChanMapping] = [WSChanMapping(channel="api/v2/pools/ws", event="pool_update")]


class GlintV1HardwareAccelerationOptions(BaseModel):
    """
    Настройки аппаратного ускорения.
    """

    hardware_acceleration_enabled: bool = False
    video_compression_codec: VideoCompressionCodecs = VideoCompressionCodecs.AVC420
    h264_bitreight_mbs: Annotated[int, Field(ge=1, le=5)] = 3


class GlintV1SettingsModel(BaseModel):
    """
    Настройки хранящиеся на клиенте:
        Проброс папок (только если есть разрешение из SecuritySettingsModel)
        Проброс буфера обмена (только если есть разрешение из SecuritySettingsModel)
        Мониторы
    """

    image_format: ImageFormats = ImageFormats.BGRX32
    fps: Annotated[int, Field(ge=3, le=60)] = 30
    keep_session_enabled: bool = False
    full_screen_enabled: bool = True
    multi_screen_enabled: bool = False
    scale_image_enabled: bool = True
    full_image_redraw_enabled: bool = False
    hardware_acceleration_options: GlintV1HardwareAccelerationOptions = GlintV1HardwareAccelerationOptions()
    audio_playback_mode: AudioPlaybakModes = AudioPlaybakModes.CLIENT


class UserClientSettingsDataModel(BaseModel):
    service: ServiceSettingsModel
    security: SecuritySettingsModel
    main: MainSettingsModel
    glint_v1: GlintV1SettingsModel


class UserClientSettingsModel(BaseModel):
    data: UserClientSettingsDataModel
