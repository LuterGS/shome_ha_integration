import logging

from homeassistant.core import HomeAssistant

from .shome_client.shome_client import SHomeClient

# Store for client instances (singleton pattern)
CLIENT_INSTANCES = "shome_client_instances"

_LOGGER = logging.getLogger(__name__)

async def get_or_create_client(hass: HomeAssistant, username: str, password: str) -> SHomeClient:
    """Get existing client or create new one (singleton pattern)."""
    # Initialize storage if needed
    if CLIENT_INSTANCES not in hass.data:
        hass.data[CLIENT_INSTANCES] = {}

    # Check if client exists for this username
    if username in hass.data[CLIENT_INSTANCES]:
        _LOGGER.info("Returning existing SHomeClient for user: %s", username)
        return hass.data[CLIENT_INSTANCES][username]

    # Create new client
    _LOGGER.info("Creating new SHomeClient for user: %s", username)
    client = SHomeClient(hass)
    client.set_credential(username, password)
    await client.login()

    # Store client for reuse
    hass.data[CLIENT_INSTANCES][username] = client
    return client