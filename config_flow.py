import logging

from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

ACCOUNT_SCHEMA = vol.Schema({
    vol.Required("username"): str,
    vol.Required("password"): str,
})

def build_device_schema(devices: list[dict]) -> vol.Schema:
    """디바이스 목록을 기반으로 schema 생성 (다중 선택)."""
    options = {d["id"]: d["name"] for d in devices}
    return vol.Schema({
        vol.Required("device_ids"): cv.multi_select(options)
    })


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._username = None
        self._password = None
        self._client = None
        self._devices = []

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            self._username = user_input["username"]
            self._password = user_input["password"]
            
            _LOGGER.info("Config flow: User attempting login with username: %s", self._username)

            try:
                # Import here to avoid circular import
                from . import get_or_create_client
                
                _LOGGER.debug("Config flow: Attempting to authenticate user")
                client = await get_or_create_client(self.hass, self._username, self._password)
                _LOGGER.info("Config flow: Login successful, fetching devices")
                
                self._devices = await client.get_devices()
                _LOGGER.info("Config flow: Found %d devices", len(self._devices))
                _LOGGER.debug("Config flow: Devices: %s", [d.get("name", "Unknown") for d in self._devices])
                
                self._client = client   # Store for later use
            except Exception as e:
                _LOGGER.error("Config flow: Login failed - %s", str(e))
                errors["base"] = "auth"
                return self.async_show_form(step_id="user", data_schema=ACCOUNT_SCHEMA, errors=errors)

            await self.async_set_unique_id(self._username)
            self._abort_if_unique_id_configured()
            return await self.async_step_select_device()

        return self.async_show_form(step_id="user", data_schema=ACCOUNT_SCHEMA, errors=errors)

    async def async_step_select_device(self, user_input=None):
        """Handle device selection step."""
        if user_input is not None:
            selected_ids = user_input["device_ids"]
            _LOGGER.info("Config flow: User selected %d devices", len(selected_ids))
            _LOGGER.debug("Config flow: Selected device IDs: %s", selected_ids)

            data = {
                "username": self._username,
                "password": self._password,
                "device_ids": selected_ids,
            }
            
            _LOGGER.info("Config flow: Creating entry for user %s with %d devices", 
                        self._username, len(selected_ids))
            return self.async_create_entry(
                title=f"{self._username} ({len(selected_ids)} devices)",
                data=data,
            )

        _LOGGER.debug("Config flow: Showing device selection form")
        schema = build_device_schema(self._devices)
        return self.async_show_form(step_id="select_device", data_schema=schema)