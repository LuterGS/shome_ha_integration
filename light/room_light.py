

"""Support for SHome lights."""
import asyncio
import logging

from homeassistant.components.light import LightEntity, ColorMode
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..coordinators.light_coordinator import LightToggleType
from ..const import DOMAIN
from ..shome_client.dto.status import OnOffStatus

_LOGGER = logging.getLogger(__name__)


class ApiRoomLight(CoordinatorEntity, LightEntity):
    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_color_mode = ColorMode.ONOFF
    _attr_should_poll = False

    def __init__(self, coordinator, info: dict):
        super().__init__(coordinator)
        self._id = str(info["id"])
        self._device_key = info["device_info"]["shome_id"]
        self._attr_unique_id = f"{self._device_key}_room_{info['id']}"
        self._attr_name = info["name"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_key)},
            name=info["device_info"]["name"],
            model=info["device_info"]["model"],
            model_id=info["device_info"]["model_id"],
            modified_at=info["device_info"]["created_at"],
            manufacturer="SHome"
        )
        self._sub_devices = [str(sub_device_id) for sub_device_id in info.get("devices", [])]

    # coordinator.data에서 내 데이터만 꺼내서 표시
    @property
    def _state(self):
        return self.coordinator.data\
            .get(self._device_key, {})\
            .get("sub_device_info", {})

    @property
    def is_on(self) -> bool | None:
        result = []
        for light_id, light_status in self._state.items():
            if light_id in self._sub_devices:
                result.append(light_status.get("on", False))
        if True in result:
            return True
        if result:
            return False
        return None

    @property
    def brightness(self) -> int | None:
        return None

    async def _delayed_refresh(self):
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs):
        await self.coordinator.toggle_light(self._device_key, LightToggleType.ROOM, self._id, OnOffStatus.ON)

        # Optimistic update
        new_data = self.coordinator.data
        current_device = new_data.get(self._device_key, {})
        if not current_device:
            return
        for light_id in self._sub_devices:
            new_data[self._device_key]["sub_device_info"][str(light_id)]["on"] = True
        self.coordinator.async_set_updated_data(new_data)

        asyncio.create_task(self._delayed_refresh())

    async def async_turn_off(self, **kwargs):
        await self.coordinator.toggle_light(self._device_key, LightToggleType.ROOM, self._id, OnOffStatus.OFF)

        # Optimistic update
        new_data = self.coordinator.data
        current_device = new_data.get(self._device_key, {})
        if not current_device:
            return
        for light_id in self._sub_devices:
            new_data[self._device_key]["sub_device_info"][str(light_id)]["on"] = False
        self.coordinator.async_set_updated_data(new_data)

        asyncio.create_task(self._delayed_refresh())
