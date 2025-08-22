from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity


class TemperatureSensor(CoordinatorEntity, SensorEntity):
    _attr_should_poll = False

    def __init__(self, coordinator, info: dict):
        super().__init__(coordinator)
        self._id = "0"
        self._attr_unique_id = f"{info['device_info']['shome_id']}_temperature_sensor"
        self._attr_name = "온도 센서"
        self._attr_device_info = DeviceInfo(
            identifiers={(info['device_info']['shome_id'], 'temperature_sensor')},
            name=info["device_info"]["name"],
            model=info["device_info"]["model"],
            model_id=info["device_info"]["model_id"],
            modified_at=info["device_info"]["created_at"],
            # Assuming 'created_at' is a timestamp or datetime object
        )
        self._device_key = info["device_info"]["shome_id"]

    @property
    def native_value(self):
        return self.coordinator.data.get(self._device_key, {}).get("temperature", None)
