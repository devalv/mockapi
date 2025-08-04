from typing import Annotated

from pydantic import BaseModel, Field

from core.enums import (
    AudioPlaybakModes,
    ConnectionTypes,
    GlintV1SecurityProtocols,
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


class MainSettingsModel(BaseModel):
    """
    Настройки хранящиеся на клиенте:
        Адрес подключения (Disp || GW)
        Порт подключения (Disp || GW)
        Протокол подключения (http || https)
    """

    reset_settings: bool = False  # если придет клиенту - сбросить клиентские настройки на стандартные  TODO: а как это будет работать? флаг ведь должен быть 1-разовым
    default_remote_protocol: ConnectionTypes = ConnectionTypes.GLINT
    last_pool_autoconnect_ebabled: bool = False
    # TODO: каналы подписок на события wss - не смог с ходу придумать зачем?


class GlintV1SettingsModel(BaseModel):
    """
    Настройки хранящиеся на клиенте:
        Проброс папок (только если есть разрешение из SecuritySettingsModel)
        Проброс буфера обмена (только если есть разрешение из SecuritySettingsModel)
    """

    image_format: ImageFormats = ImageFormats.BGRX32
    fps: Annotated[int, Field(ge=3, le=60)] = 30
    keep_session_enabled: bool = False
    full_screen_enabled: bool = True
    multi_screen_enabled: bool = False
    scale_image_enabled: bool = True
    full_image_redraw_enabled: bool = False
    hardware_acceleration_enabled: bool = False
    security_protocol: GlintV1SecurityProtocols = GlintV1SecurityProtocols.RDP
    video_compression_codec: VideoCompressionCodecs = VideoCompressionCodecs.AVC420
    h264_bitreight_mbs: Annotated[int, Field(ge=1, le=5)] = 3  # TODO: выше кодек AVC420, тут настройки h264 - непонятно
    audio_playback_mode: AudioPlaybakModes = AudioPlaybakModes.CLIENT
    selected_display_settings: str | None = None
    # TODO: SCImageResolution?


class UserClientSettingsDataModel(BaseModel):
    service: ServiceSettingsModel
    security: SecuritySettingsModel
    main: MainSettingsModel
    glint_v1: GlintV1SettingsModel


class UserClientSettingsModel(BaseModel):
    data: UserClientSettingsDataModel
