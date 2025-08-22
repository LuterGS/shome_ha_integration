

from homeassistant.const import Platform

from ..dto.device import SHomeDevice

def get_device_type(device: SHomeDevice) -> Platform:
    if device.model_type_id == 'TD00000069':
        return Platform.LIGHT
    return Platform.BUTTON  # Default to BUTTON for other types

