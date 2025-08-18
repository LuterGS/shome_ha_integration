from homeassistant.components.light import LightEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN
from ..shome_client.dto.light import LightInfo, LightStatus


class ApiGroupedLight(CoordinatorEntity, LightEntity):
    _attr_should_poll = False

    def __init__(self, coordinator, light: LightInfo):
        super().__init__(coordinator)
        self._id = "0"
        self._attr_unique_id = f"all_light"
        self._attr_name = "전체 조명"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"all_light")},
            model="SHome Grouped Light",
            name="전체 조명",
        )
        self.light_info = light

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

    async def async_turn_on(self, **kwargs):
        await self.coordinator.toggle_light(self._id, LightStatus.ON)
        self.coordinator.data[self._id] = {"on": True}
        await self.async_update_ha_state(True)

    async def async_turn_off(self, **kwargs):
        await self.coordinator.toggle_light(self._id, LightStatus.OFF)
        self.coordinator.data[self._id] = {"on": False}
        await self.async_update_ha_state(True)
        # self.async_write_ha_state()
