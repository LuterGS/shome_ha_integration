from .const import DOMAIN

# async def async_setup_entry(hass, entry, async_add_entities):
#     data = hass.data[DOMAIN][entry.entry_id]
#     client = data["client"]
#     device_ids = data["devices"]
#
#     devices = await client.get_devices()  # 최신 목록 (추후 확장 가능)
#     entities = []
#     for dev in devices:
#         if dev["id"] in device_ids:
#             entities.append(MySensorEntity(client, dev))
#     async_add_entities(entities)