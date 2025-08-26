from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True) 
class SHomeSensorInfo:
    sub_device_num: int
    sub_device_name: str
    temperature: Optional[float]
    humidity: Optional[float]
    co2: Optional[int]
    pm10: Optional[float]
    
    @staticmethod
    def from_dict(data: dict) -> list['SHomeSensorInfo']:
        devices = data.get("deviceInfoList", [])
        result = []
        for device in devices:
            if device.get("temperature") is not None:
                device["temperature"] = float(device["temperature"])
            if device.get("humidity") is not None:
                device["humidity"] = int(device["humidity"])
            if device.get("co2") is not None:
                device["co2"] = int(device["co2"])
            if device.get("fineDust") is not None:
                device["fineDust"] = int(device["fineDust"])

            result.append(SHomeSensorInfo(
                sub_device_num=device.get("deviceId"),
                sub_device_name=device.get("nickname", ""),
                temperature=device.get("temperature"),
                humidity=device.get("humidity"),
                co2=device.get("co2"),
                pm10=device.get("fineDust")
            ))
        return result
