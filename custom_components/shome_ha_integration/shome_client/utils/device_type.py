from typing import Optional

from homeassistant.const import Platform

from ..dto.device import SHomeDevice


_device_type_map: dict[str, tuple[Platform, str]] = {
    "TD00000069": (Platform.LIGHT, 'light'),
    "TD00000071": (Platform.VALVE, 'wired-gasvalve'),      # GAS valve
    "TD00000072": (Platform.CLIMATE, 'aircon'),    # Air Conditioner
    "TD00000073": (Platform.FAN, 'ventilator'),        # Ventilator
    "TD00000075": (Platform.CLIMATE, 'heater'),    # Heater
    "TD00000076": (Platform.SENSOR, 'environment-sensor'),     # Environment Sensor (Temp, Humidity, CO2, PM10)
    "TD00000077": (Platform.SENSOR, 'TODO: need to identify'),     # Door/Window sensor
    "TD00000078": (Platform.SENSOR, 'TODO: need to identify'),     # Motion sensor
    "TD00000081": (Platform.BUTTON, 'TODO: need to identify'),     # SOS Button
    "TE00000075": (Platform.SWITCH, 'TODO: need to identify'),     # Outlet (Plug) - 대기전력
}


def get_device_type(device: SHomeDevice) -> Optional[tuple[Platform, str]]:
    return _device_type_map.get(device.model_type_id)

# use for build URL
def get_shome_device_type(device: SHomeDevice) -> str:
    platform = _device_type_map.get(device.model_type_id, Platform)
    if not platform:
        raise ValueError(f"Unsupported device type: {device.model_type_id}")
    return platform[1]
