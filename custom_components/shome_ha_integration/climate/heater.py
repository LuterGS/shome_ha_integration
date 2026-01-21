import asyncio

from homeassistant.components.climate import ClimateEntity, HVACMode, ClimateEntityFeature
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature, PRECISION_WHOLE
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN
from ..coordinators.heater_coordinator import HeaterCoordinator
from ..shome_client.dto.status import OnOffStatus


class Heater(CoordinatorEntity, ClimateEntity):
    _attr_should_poll = False
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_max_temp = 40.0
    _attr_min_temp = 5.0
    _attr_supported_features = ClimateEntityFeature.TURN_ON | ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_precision = PRECISION_WHOLE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: HeaterCoordinator, info: dict):
        super().__init__(coordinator)
        self._id = str(info["sub_device_num"])
        self._device_key = info["device_info"]["shome_id"]
        self._attr_unique_id = f"{self._device_key}_{info['sub_device_num']}"
        self._attr_name = f"{info['sub_device_name']}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_key)},
            name=info["device_info"]["name"],
            model=info["device_info"]["model"],
            model_id=info["device_info"]["model_id"],
            modified_at=info["device_info"]["created_at"],
            manufacturer="SHome"
        )

    @property
    def hvac_mode(self) -> HVACMode:
        is_on = (self.coordinator.data or {}).get(self._device_key, {}).get("sub_devices", {}).get(self._id, {}).get("on", False)
        if is_on:
            return HVACMode.HEAT
        else:
            return HVACMode.OFF

    @property
    def current_temperature(self):
        return (self.coordinator.data or {}).get(self._device_key, {}).get("sub_devices", {}).get(self._id, {}).get("current_temperature")

    @property
    def target_temperature(self):
        return (self.coordinator.data or {}).get(self._device_key, {}).get("sub_devices", {}).get(self._id, {}).get("target_temperature")

    async def _delayed_refresh(self):
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self.async_turn_off()
        elif hvac_mode == HVACMode.HEAT:
            await self.async_turn_on()
        # 다른 모드는 미지원

    async def async_turn_on(self) -> None:
        await self.coordinator.toggle_heater(self._device_key, self._id, OnOffStatus.ON)

        # Optimistic update
        new_data = self.coordinator.data
        current_device = new_data.get(self._device_key, {})
        if not current_device:
            return
        new_data[self._device_key]["sub_devices"][self._id]["on"] = True
        self.coordinator.async_set_updated_data(new_data)

        asyncio.create_task(self._delayed_refresh())

    async def async_turn_off(self) -> None:
        await self.coordinator.toggle_heater(self._device_key, self._id, OnOffStatus.OFF)

        # Optimistic update
        new_data = self.coordinator.data
        current_device = new_data.get(self._device_key, {})
        if not current_device:
            return
        new_data[self._device_key]["sub_devices"][self._id]["on"] = False
        self.coordinator.async_set_updated_data(new_data)

        asyncio.create_task(self._delayed_refresh())

    async def async_set_temperature(self, **kwargs):
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        await self.coordinator.set_heater_temperature(self._device_key, self._id, int(temp))

        # Optimistic update
        new_data = self.coordinator.data
        current_device = new_data.get(self._device_key, {})
        if not current_device:
            return
        new_data[self._device_key]["sub_devices"][self._id]["target_temperature"] = int(temp)
        self.coordinator.async_set_updated_data(new_data)

        asyncio.create_task(self._delayed_refresh())
