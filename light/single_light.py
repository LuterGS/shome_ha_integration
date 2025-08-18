"""Support for SHome lights."""
import logging

from homeassistant.components.light import LightEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN
from ..shome_client.dto.light import LightDevice, LightStatus

_LOGGER = logging.getLogger(__name__)


class ApiLight(CoordinatorEntity, LightEntity):
    _attr_should_poll = False

    def __init__(self, coordinator, light: LightDevice):
        super().__init__(coordinator)
        self._id = str(light.id)
        self._attr_unique_id = f"light_{self._id}"
        self._attr_name = light.nick_name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"light_{self._id}")},
            model="SHome Light",
            name=light.nick_name,
        )

    # coordinator.data에서 내 데이터만 꺼내서 표시
    @property
    def _state(self):
        return self.coordinator.data.get(self._id, {})

    @property
    def is_on(self) -> bool | None:
        return self._state.get("on")

    @property
    def brightness(self) -> int | None:
        return None

    async def async_turn_on(self, **kwargs):
        await self.coordinator.toggle_light(self._id, LightStatus.ON)
        self.coordinator.data[self._id] = {"on": True}
        await self.async_update_ha_state(True)

    async def async_turn_off(self, **kwargs):
        await self.coordinator.toggle_light(self._id, LightStatus.OFF)
        self.coordinator.data[self._id] = {"on": False}
        await self.async_update_ha_state(True)
        # self.async_write_ha_state()
