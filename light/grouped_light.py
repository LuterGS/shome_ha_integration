import asyncio

from homeassistant.components.light import LightEntity, ColorMode
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN
from ..shome_client.dto.light import LightStatus


class ApiGroupedLight(CoordinatorEntity, LightEntity):
    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_color_mode = ColorMode.ONOFF
    _attr_should_poll = False

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._id = "0"
        self._attr_unique_id = f"all_light"
        self._attr_name = "전체 조명"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"all_light")},
            model="SHome Grouped Light",
            name="전체 조명",
        )

    # coordinator.data에서 내 데이터만 꺼내서 표시
    @property
    def _state(self):
        data = self.coordinator.data
        result = {"on": False}
        for light_id, light_data in data.items():
            if light_data["on"]:
                result["on"] = True
                break
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
        await self.coordinator.toggle_light(self._id, LightStatus.ON)

        # Optimistic update
        current_data = self.coordinator.data
        new_data = {}
        for light_id, light_data in current_data.items():
            new_data[light_id] = {"on": True}
        self.coordinator.async_set_updated_data(new_data)

        asyncio.create_task(self._delayed_refresh())

    async def async_turn_off(self, **kwargs):
        await self.coordinator.toggle_light(self._id, LightStatus.OFF)

        # Optimistic update
        current_data = self.coordinator.data
        new_data = {}
        for light_id, light_data in current_data.items():
            new_data[light_id] = {"on": False}
        self.coordinator.async_set_updated_data(new_data)

        asyncio.create_task(self._delayed_refresh())
