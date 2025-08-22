"""Support for SHome lights."""
import asyncio
import logging

from homeassistant.components.light import LightEntity, ColorMode
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..coordinators.light_coordinator import LightToggleType
from ..const import DOMAIN
from ..shome_client.dto.light import LightStatus

_LOGGER = logging.getLogger(__name__)


class ApiLight(CoordinatorEntity, LightEntity):
    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_color_mode = ColorMode.ONOFF
    _attr_should_poll = False

    def __init__(self, coordinator, info: dict):
        super().__init__(coordinator)
        self._id = str(info["id"])
        self._attr_unique_id = f"{info['device_info']['shome_id']}_{info['id']}"
        self._attr_name = info["name"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, info['device_info']['shome_id'])},
            name=info["device_info"]["name"],
            model=info["device_info"]["model"],
            model_id=info["device_info"]["model_id"],
            modified_at=info["device_info"]["created_at"],
            manufacturer="SHome"
        )
        self._device_key = info["device_info"]["shome_id"]

    # coordinator.data에서 내 데이터만 꺼내서 표시
    @property
    def _state(self):
        result = self.coordinator.data\
            .get(self._device_key, {})\
            .get("sub_device_info", {})\
            .get(self._id, {})
        _LOGGER.debug(f"light state: {result}")
        return result

    @property
    def is_on(self) -> bool | None:
        return self._state.get("on")

    @property
    def brightness(self) -> int | None:
        return None

    async def _delayed_refresh(self):
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs):
        await self.coordinator.toggle_light(self._device_key, LightToggleType.SINGLE, self._id, LightStatus.ON)

        # Optimistic update
        new_data = self.coordinator.data
        current_device = new_data.get(self._device_key, {})
        if not current_device:
            return
        new_data[self._device_key]["sub_device_info"][self._id]["on"] = True
        self.coordinator.async_set_updated_data(new_data)

        asyncio.create_task(self._delayed_refresh())

    async def async_turn_off(self, **kwargs):
        await self.coordinator.toggle_light(self._device_key, LightToggleType.SINGLE, self._id, LightStatus.OFF)

        # Optimistic update
        new_data = self.coordinator.data
        _LOGGER.debug(f"light state: {new_data}")
        current_device = new_data.get(self._device_key, {})
        if not current_device:
            return
        new_data[self._device_key]["sub_device_info"][self._id]["on"] = False
        self.coordinator.async_set_updated_data(new_data)

        asyncio.create_task(self._delayed_refresh())
