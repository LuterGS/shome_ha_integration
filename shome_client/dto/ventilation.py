from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


class VentilationSpeed(IntEnum):
    OFF = 0
    SPEED_1 = 1     # 3 단
    SPEED_2 = 2     # 2 단
    SPEED_3 = 3     # 1 단


@dataclass(frozen=True)
class SHomeVentilationInfo:
    sub_device_num: int
    sub_device_name: str
    current_speed: VentilationSpeed
    
    @staticmethod
    def from_dict(data: dict) -> list['SHomeVentilationInfo']:
        sub_devices = data.get("deviceInfoList", [])
        result = []
        for sub_device in sub_devices:
            result.append(SHomeVentilationInfo(
                sub_device_num=sub_device.get("deviceId", 0),
                sub_device_name=sub_device.get("nickname", ""),
                current_speed=VentilationSpeed(sub_device.get("windSpeedMode", 0))
            ))
        return result
