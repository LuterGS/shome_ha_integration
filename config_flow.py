import hashlib
import logging
import secrets
from typing import Optional

from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import DOMAIN
from .utils import get_or_create_client

_LOGGER = logging.getLogger(__name__)

ACCOUNT_SCHEMA = vol.Schema({
    vol.Required("username"): str,
    vol.Required("password"): str,
    vol.Required("device_id", default=lambda: secrets.token_hex(8)): str,
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
        self._credential: dict = {}
        self._client = None
        self._devices = []

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            hashed_user_id = hashlib.sha512(user_input["password"].encode("utf-8")).hexdigest()
            self._credential = {
                "username": user_input["username"],
                "password": hashed_user_id,
                "device_id": user_input["device_id"]
            }
            _LOGGER.info("User attempting login with credential: %s", self._credential)

            try:
                # Import here to avoid circular import
                
                _LOGGER.debug("Attempting to authenticate user")
                client = await get_or_create_client(self.hass, self._credential)
                _LOGGER.info("Login successful")
                
                self._client = client   # Store for later use
            except Exception as e:
                _LOGGER.error("Login failed - %s", str(e))
                errors["base"] = "auth"
                return self.async_show_form(step_id="user", data_schema=ACCOUNT_SCHEMA, errors=errors)

            await self.async_set_unique_id(self._credential['username'])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"{self._credential['username']} - {self._credential['device_id']}",
                data={
                    "credential": self._credential
                },
            )

        return self.async_show_form(step_id="user", data_schema=ACCOUNT_SCHEMA, errors=errors)
