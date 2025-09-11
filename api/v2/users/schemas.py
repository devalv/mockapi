from typing import Annotated, Optional

from pydantic import BaseModel, Field

from core.enums import (
    AudioPlaybakModes,
    ConnectionTypes,
    ConnectionTypesMap,
    ImageFormats,
    UserSCPermission,
    VideoCompressionCodecs,
)
from core.schemas import Token


class LoginInputModel(BaseModel):
    username: str
    password: str | None
    ldap: bool
    otp_code: Optional[str] = None


class TokenResponseModel(BaseModel):
    data: Token


# Настройки клиента


class GeneralSettingsModel(BaseModel):
    """Раздел General для клиента (нередактируемые клиентом).

    Настройки хранящиеся на клиенте:
        Архивировать логи
        Масштабирование
        Язык?
        Цветовая схема
    """

    admin_mode_enabled: bool = False
    file_logging_enabled: bool = False
    default_remote_protocol: ConnectionTypesMap = ConnectionTypesMap.GLINTV1
    last_pool_autoconnect_enabled: bool = False
    automatically_install_updates_enabled: bool = True
    documentation_url: str = "https://spacevm.ru/client-docs/latest/"


class WSChanMapping(BaseModel):
    """Сопоставления типа событий и каналов WS."""

    channel: str
    event: str


class NetSettingsModel(BaseModel):
    """Раздел Net для клиента (частично редактируемые клиентом).

    Настройки хранящиеся на клиенте:
        Адрес подключения (Disp || GW)
        Порт подключения (Disp || GW)
        Протокол подключения (http || https)
    """

    network_timeout: Annotated[int, Field(ge=5, le=60)] = 15
    ws_channels: list[WSChanMapping] = [WSChanMapping(channel="api/v2/pools/ws/", event="pool_update")]


class GlintV1HardwareAccelerationOptions(BaseModel):
    """Настройки аппаратного ускорения."""

    hardware_acceleration_enabled: bool = False
    video_compression_codec: VideoCompressionCodecs = VideoCompressionCodecs.AVC420
    h264_bitrate_mbs: Annotated[int, Field(ge=1, le=5)] = 3


class RemoteProtocolBase(BaseModel):
    """Базовый набор настроек для протокола.

    При добавлении нового протокола наследуем его от базового набора.
    """

    id: ConnectionTypesMap
    name: ConnectionTypes
    version: str


class GlintV1SettingsModel(RemoteProtocolBase):
    """Настройки Glint V1.

    Настройки хранящиеся на клиенте:
        Проброс папок (только если есть разрешение из SecuritySettingsModel)
        Проброс буфера обмена (только если есть разрешение из SecuritySettingsModel)
        Мониторы
    """

    id: ConnectionTypesMap = ConnectionTypesMap.GLINTV1
    name: ConnectionTypes = ConnectionTypes.GLINT
    version: str = "1.0.0"
    image_format: ImageFormats = ImageFormats.BGRX32
    fps: Annotated[int, Field(ge=3, le=60)] = 30
    keep_session_enabled: bool = False
    full_screen_enabled: bool = True
    multi_screen_enabled: bool = False
    scale_image_enabled: bool = True
    full_image_redraw_enabled: bool = False
    hardware_acceleration_options: GlintV1HardwareAccelerationOptions = GlintV1HardwareAccelerationOptions()
    audio_playback_mode: AudioPlaybakModes = AudioPlaybakModes.CLIENT


class SecuritySettingsModel(BaseModel):
    """Отображение текущих настроек безопасности клиента (нередактируемые клиентом)."""

    otp_enabled: bool = False
    adfs_enabled: bool = False
    hardware_token_enabled: bool = False
    domain_username_format_enabled: bool = False
    sc_permissions: list[UserSCPermission] = []


class UserClientSettingsDataModel(BaseModel):
    """Набор настроек передаваемых клиенту."""

    general: GeneralSettingsModel
    security: SecuritySettingsModel
    net: NetSettingsModel
    protocols: list[GlintV1SettingsModel | RemoteProtocolBase] = [GlintV1SettingsModel()]


class UserClientSettingsResponseModel(BaseModel):
    data: UserClientSettingsDataModel
