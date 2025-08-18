from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN

class RefreshButton(CoordinatorEntity, ButtonEntity):
    _attr_name = "Refresh Lights"
    _attr_entity_category = "diagnostic"  # 설정/진단 탭로 분류(선택)

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = "refresh_lights_button"
        self._attr_icon = "mdi:refresh"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "refresh_lights_button")},
            name="조명 상태 새로고침",
        )

    async def async_press(self) -> None:
        await self.coordinator.async_request_refresh()

