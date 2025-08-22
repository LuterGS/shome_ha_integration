from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN


class TemperatureSensor(CoordinatorEntity, SensorEntity):
    _attr_should_poll = False
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator, info: dict):
        super().__init__(coordinator)
        self._id = str(info["sub_device_num"])
        self._device_key = info["device_info"]["shome_id"]
        self._attr_unique_id = f"{self._device_key}_{self._id}_temperature"
        self._attr_name = f"{info['sub_device_name']}_temperature"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_key)},
            name=info["device_info"]["name"],
            model=info["device_info"]["model"],
            model_id=info["device_info"]["model_id"],
            modified_at=info["device_info"]["created_at"],
            manufacturer="SHome"
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(self._device_key, {}).get(self._id, {}).get("temperature")
