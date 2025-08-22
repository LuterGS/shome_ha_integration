"""Support for SHome ventilation fan."""
import asyncio
import logging
from typing import Any, Optional
from math import ceil

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.percentage import (
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from ..const import DOMAIN
from ..coordinators.ventilation_coordinator import VentilationCoordinator
from ..shome_client.dto.status import OnOffStatus
from ..shome_client.dto.ventilation import VentilationSpeed

_LOGGER = logging.getLogger(__name__)

# Speed range mapping
SPEED_RANGE = (1, 3)  # 1-3 speed levels


class VentilationFan(CoordinatorEntity, FanEntity):
    """Representation of a SHome ventilation fan."""
    
    _attr_should_poll = False
    _attr_supported_features = FanEntityFeature.SET_SPEED
    _attr_speed_count = 3
    
    def __init__(self, coordinator: VentilationCoordinator, info: dict):
        """Initialize the fan."""
        super().__init__(coordinator)
        self._id = str(info["sub_device_num"])
        self._device_key = info["device_info"]["shome_id"]
        self._attr_unique_id = f"{self._device_key}_{info['sub_device_num']}"
        self._attr_name = info["sub_device_name"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_key)},
            name=info["device_info"]["name"],
            model=info["device_info"]["model"],
            model_id=info["device_info"]["model_id"],
            modified_at=info["device_info"]["created_at"],
            manufacturer="SHome"
        )

    @property
    def _state(self) -> dict:
        """Get current state from coordinator."""
        return self.coordinator.data.get(self._device_key, {}).get(self._id, {})

    @property
    def is_on(self) -> bool:
        """Return true if the fan is on."""
        if self._state.get("status", 0):
            return False
        else:
            return True

    @property
    def percentage(self) -> Optional[int]:
        """Return the current speed percentage."""
        current_speed = self._state.get("status", 0)
        if current_speed == VentilationSpeed.OFF:
            return 0
        real_speed = 4 - current_speed
        return ranged_value_to_percentage(SPEED_RANGE, real_speed)

    async def _delayed_refresh(self):
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, percentage: Optional[int] = None, preset_mode: Optional[str] = None, **kwargs) -> None:
        """Turn on the fan."""
        self.coordinator.toggle_ventilation(self._device_key, self._id, OnOffStatus.ON)

        new_data = self.coordinator.data
        current_device = new_data.get(self._device_key, {})
        if not current_device:
            return
        new_data[self._device_key][self._id]["status"] = VentilationSpeed.SPEED_2
        self.coordinator.async_set_updated_data(new_data)

        asyncio.create_task(self._delayed_refresh())

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        self.coordinator.toggle_ventilation(self._device_key, self._id, OnOffStatus.OFF)

        new_data = self.coordinator.data
        current_device = new_data.get(self._device_key, {})
        if not current_device:
            return
        new_data[self._device_key][self._id]["status"] = VentilationSpeed.OFF
        self.coordinator.async_set_updated_data(new_data)

        asyncio.create_task(self._delayed_refresh())


    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        if percentage == 0:
            await self.async_turn_off()
        else:
            # Convert percentage to speed level (1-3)
            speed_value = ceil(percentage_to_ranged_value(SPEED_RANGE, percentage))
            shome_value = VentilationSpeed(4 - speed_value)
            self.coordinator.set_ventilation_speed(self._device_key, self._id, shome_value)

            new_data = self.coordinator.data
            current_device = new_data.get(self._device_key, {})
            if not current_device:
                return
            new_data[self._device_key][self._id]["status"] = shome_value.value

            asyncio.create_task(self._delayed_refresh())
