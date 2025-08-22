from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class SHomeLightGroupInfo:
    group_id: int
    nick_name: str
    devices: list[int]
    is_all_off: bool

    @staticmethod
    def from_dict(data: dict) -> 'SHomeLightGroupInfo':
        group_status = data.get("groupStatus", 0)
        is_all_off = True if group_status == 0 else False
        return SHomeLightGroupInfo(
            group_id=data.get("groupId", 0),
            nick_name=data.get("nickname", ""),
            devices=data.get("deviceList", []),
            is_all_off=is_all_off
        )


@dataclass(frozen=True)
class SHomeLightDevice:
    id: int
    nick_name: str
    on: bool

    @staticmethod
    def from_dict(data: dict) -> 'SHomeLightDevice':
        device_status = data.get("deviceStatus", 0)
        on = True if device_status == 1 else False
        return SHomeLightDevice(
            id=data.get("deviceId", 0),
            nick_name=data.get("nickname", ""),
            on=on
        )


@dataclass(frozen=True)
class SHomeLightInfo:
    groups: list[SHomeLightGroupInfo]
    devices: list[SHomeLightDevice]

    @staticmethod
    def from_dict(data: dict) -> 'SHomeLightInfo':
        groups = [SHomeLightGroupInfo.from_dict(group) for group in data.get("groupInfo", [])]
        devices = [SHomeLightDevice.from_dict(device) for device in data.get("deviceInfoList", [])]
        return SHomeLightInfo(
            groups=groups,
            devices=devices
        )


class OnOffStatus(Enum):
    ON = "ON"
    OFF = "OFF"

