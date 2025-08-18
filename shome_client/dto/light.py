from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class LightGroupInfo:
    group_id: int
    nick_name: str
    devices: list[int]
    is_all_off: bool

    @staticmethod
    def from_dict(data: dict) -> 'LightGroupInfo':
        group_status = data.get("groupStatus", 0)
        is_all_off = True if group_status == 0 else False
        return LightGroupInfo(
            group_id=data.get("groupId", 0),
            nick_name=data.get("nickname", ""),
            devices=data.get("deviceList", []),
            is_all_off=is_all_off
        )


@dataclass(frozen=True)
class LightDevice:
    id: int
    nick_name: str
    on: bool

    @staticmethod
    def from_dict(data: dict) -> 'LightDevice':
        device_status = data.get("deviceStatus", 0)
        on = True if device_status == 1 else False
        return LightDevice(
            id=data.get("deviceId", 0),
            nick_name=data.get("nickname", ""),
            on=on
        )


@dataclass(frozen=True)
class LightInfo:
    groups: list[LightGroupInfo]
    devices: list[LightDevice]

    @staticmethod
    def from_dict(data: dict) -> 'LightInfo':
        groups = [LightGroupInfo.from_dict(group) for group in data.get("groupInfo", [])]
        devices = [LightDevice.from_dict(device) for device in data.get("deviceInfoList", [])]
        return LightInfo(
            groups=groups,
            devices=devices
        )


class LightStatus(Enum):
    ON = "ON"
    OFF = "OFF"

