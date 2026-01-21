from dataclasses import dataclass


@dataclass(frozen=True)
class SHomeHeaterInfo:
    sub_device_num: int
    sub_device_name: str
    on: bool
    current_temp: int       # incorrect value!
    set_temp: int
    support_windspeed: bool
    support_operation: bool

    @staticmethod
    def from_dict(data: dict) -> list['SHomeHeaterInfo']:
        sub_devices = data.get("deviceInfoList", [])
        result = []
        for sub_device in sub_devices:
            result.append(SHomeHeaterInfo(
                sub_device_num=sub_device.get("deviceId", 0),
                sub_device_name=sub_device.get("nickname", ""),
                on=True if sub_device.get("deviceStatus", 0) != 0 else False,
                current_temp=sub_device.get("currentTemp", 0),   # incorrect value!
                set_temp=sub_device.get("setTemp", 0),
                support_windspeed=True if sub_device.get("windSpeedMode", 0) != 0 else False,
                support_operation=True if sub_device.get("operationMode", 0) != 0 else False
            ))
        return result
