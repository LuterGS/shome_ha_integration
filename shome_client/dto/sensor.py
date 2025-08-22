from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True) 
class SHomeSensorInfo:
    sub_device_num: int
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
            if device.get("pm10") is not None:
                device["pm10"] = int(device["pm10"])

            result.append(SHomeSensorInfo(
                sub_device_num=device.get("deviceId"),
                temperature=device.get("temperature"),
                humidity=device.get("humidity"),
                co2=device.get("co2"),
                pm10=device.get("pm10")
            ))
        return result
