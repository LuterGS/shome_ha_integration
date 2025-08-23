from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import CONCENTRATION_PARTS_PER_MILLION
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN


class CO2Sensor(CoordinatorEntity, SensorEntity):
    _attr_should_poll = False
    _attr_device_class = SensorDeviceClass.CO2
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_MILLION

    def __init__(self, coordinator, info: dict):
        super().__init__(coordinator)
        self._id = str(info["sub_device_num"])
        self._device_key = info["device_info"]["shome_id"]
        self._attr_unique_id = f"{self._device_key}_{self._id}_co2"
        self._attr_name = f"{info['sub_device_name']}_co2"
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
        return self.coordinator.data.get(self._device_key, {}).get("sub_devices", {}).get(self._id, {}).get("co2")