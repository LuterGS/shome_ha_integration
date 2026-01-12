import logging

from homeassistant.core import HomeAssistant

from .shome_client.shome_client import SHomeClient

# Store for client instances (singleton pattern)
CLIENT_INSTANCES = "shome_client_instances"

_LOGGER = logging.getLogger(__name__)


async def get_or_create_client(hass: HomeAssistant, credential: dict) -> SHomeClient:
    """Get existing client or create new one (singleton pattern)."""
    if not credential or "username" not in credential:
        raise ValueError("Missing credential or username for SHome client setup")

    # Initialize storage if needed
    if CLIENT_INSTANCES not in hass.data:
        hass.data[CLIENT_INSTANCES] = {}

    # Check if client exists for this username
    existing_client = hass.data[CLIENT_INSTANCES].get(credential["username"])
    if existing_client is not None:
        _LOGGER.info("Returning existing SHomeClient for user: %s", credential["username"])
        return existing_client

    _LOGGER.info("Creating new SHomeClient for user: %s", credential['username'])
    client = SHomeClient(hass)
    client.set_credential(credential)
    await client.login()

    # Store client for reuse
    hass.data[CLIENT_INSTANCES][credential['username']] = client
    return client

async def unload_client(hass: HomeAssistant, credential: dict):
    """Unload SHome client for a specific credential."""
    if CLIENT_INSTANCES not in hass.data:
        return

    if credential["username"] in hass.data[CLIENT_INSTANCES]:
        _LOGGER.info("Unloading SHomeClient for user: %s", credential["username"])
        hass.data[CLIENT_INSTANCES].pop(credential["username"], None)
    else:
        _LOGGER.warning("No SHomeClient found for user: %s", credential['username'])

    return
