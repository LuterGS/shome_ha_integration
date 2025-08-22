

from homeassistant.const import Platform

from ..dto.device import SHomeDevice

def get_device_type(device: SHomeDevice) -> Platform:
    if device.model_type_id == 'TD00000069':
        return Platform.LIGHT
    elif device.model_type_id == 'TD00000076':
        return Platform.SENSOR
    elif device.model_type_id == 'TD00000073':
        return Platform.FAN
    return Platform.BUTTON  # Default to BUTTON for other types

