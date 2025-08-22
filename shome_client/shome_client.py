import asyncio
import logging
from typing import Optional, Tuple

from aiohttp import ClientResponseError
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .dto.cookie import Cookie
from .dto.device import SHomeDevice
from .dto.home_info import SHomeInfo
from .dto.light import SHomeLightInfo, OnOffStatus
from .dto.login import Login
from .dto.sensor import SHomeSensorInfo
from .dto.pagination import Pagination
from .shome_header_maker import SHomeHeaderMaker
from .shome_param_maker import SHomeParamMaker

_LOGGER = logging.getLogger(__name__)


class SHomeClient:

    def __init__(self, hass: HomeAssistant):
        self._credential: dict = {}
        self._session = async_get_clientsession(hass)
        self._cookie: Optional[Cookie] = None
        self._login: Optional[Login] = None
        self._home_info: Optional[SHomeInfo] = None
        self._header_maker = SHomeHeaderMaker()
        self._param_maker = SHomeParamMaker()


    def set_credential(self, credential: dict):
        """Set the credentials for the client."""
        self._credential = credential
        _LOGGER.debug("Credentials set for user: %s", credential['username'])


    def close(self):
        return None


    def _get_url(self, url_type: str, **kwargs) -> Tuple[str, str]:
        if url_type == "check_app_version":
            return "https://shome-api.samsung-ihp.com/v18/users/checkAppVersion", "GET"
        elif url_type == "login":
            return "https://shome-api.samsung-ihp.com/v18/users/login", "PUT"
        elif url_type == "list_device":
            return f"https://shome-api.samsung-ihp.com/v16/settings/{self._login.wallpad_id}/devices/", "GET"
        elif url_type == "get_light_info":
            device_id = kwargs.get("device_id")
            return f"https://shome-api.samsung-ihp.com/v18/settings/light/{device_id}", "GET"
        elif url_type == "toggle_all_light":
            device_id = kwargs.get("device_id")
            return f"https://shome-api.samsung-ihp.com/v18/settings/light/{device_id}/0/on-off", "PUT"
        elif url_type == "toggle_single_light":
            device_id = kwargs.get("device_id")
            light_id = kwargs.get("light_id")
            return f"https://shome-api.samsung-ihp.com/v18/settings/light/{device_id}/{light_id}/on-off", "PUT"
        elif url_type == "toggle_room_light":
            device_id = kwargs.get("device_id")
            room_id = kwargs.get("room_id")
            return f"https://shome-api.samsung-ihp.com/v18/settings/light/{device_id}/rooms/{room_id}/on-off", "PUT"
        elif url_type == "sensor_info":
            device_id = kwargs.get("device_id")
            return f"https://shome-api.samsung-ihp.com/v18/settings/environment-sensor/{device_id}", "GET"
        else:
            raise ValueError(f"Unknown URL type: {url_type}")


    async def login(self):
        """Perform login to SHome API."""
        _LOGGER.debug("[login] start login for user '%s'", self._credential['username'])
        
        try:
            # Step 1: Check app version and get cookies
            _LOGGER.debug(f"[login] checking app version")
            url, method = self._get_url("check_app_version")

            async with self._session.request(
                method=method, url=url,
                headers=self._header_maker.check_app_version_header(),
                params=self._param_maker.check_app_version_params()
            ) as response:
                response.raise_for_status()
                
                # Debug: Log all headers
                _LOGGER.debug("[login] Response headers: %s", dict(response.headers))
                
                # Extract cookies from response
                jsessionid = None
                wmonid = None
                
                # Parse cookies from response.cookies (SimpleCookie object)
                if response.cookies:
                    for cookie_name, cookie_value in response.cookies.items():
                        _LOGGER.debug("[login] Cookie found: %s = %s", cookie_name, cookie_value.value if hasattr(cookie_value, 'value') else cookie_value)
                        if cookie_name == "JSESSIONID":
                            jsessionid = cookie_value.value if hasattr(cookie_value, 'value') else str(cookie_value)
                        elif cookie_name == "WMONID":
                            wmonid = cookie_value.value if hasattr(cookie_value, 'value') else str(cookie_value)

                if not jsessionid:
                    raise ValueError(f"Failed to get JSESSIONID cookie from response")

                
                self._cookie = Cookie(
                    JSESSIONID=jsessionid,
                    WMONID=wmonid
                )
                _LOGGER.debug("[login] got session cookies - JSESSIONID: %s, WMONID: %s",self._cookie.JSESSIONID, self._cookie.WMONID)

            await asyncio.sleep(0.5)  # Sleep to ensure cookies are set before next request

            # Step 2: Perform actual login
            _LOGGER.debug("[login] Performing login")
            url, method = self._get_url("login")
            async with self._session.request(
                method=method, url=url,
                headers=self._header_maker.login_header(self._cookie),
                params= self._param_maker.login_params(self._credential)
            ) as response:
                response.raise_for_status()
                login_data = await response.json()
                self._login = Login.from_dict(login_data)
                _LOGGER.debug("[login] login response Headers: %s", dict(response.headers))
                _LOGGER.debug("[login] login response status: %s", response.status)
                _LOGGER.debug("[login] login response data: %s", login_data)
                _LOGGER.debug("[login] login result : %s", self._login)
                _LOGGER.info("[login] login successful, wallpad_id: %s", self._login.wallpad_id)
                
        except Exception as e:
            _LOGGER.error("[login] login failed - %s", str(e))
            raise


    async def get_devices(self, retry_on_401=True) -> SHomeInfo:
        """Fetch list of devices from SHome API."""
        _LOGGER.info("[get_devices] fetching device list")
        
        try:
            if self._login is None:
                await self.login()

            url, method = self._get_url("list_device")
            _LOGGER.debug("[get_devices] request URL: %s", url)
            async with self._session.request(
                method=method, url=url,
                headers=self._header_maker.device_header(self._cookie, self._login),
                params=self._param_maker.basic_params(self._login.wallpad_id)
            ) as response:
                response.raise_for_status()
                data = await response.json()
                self._home_info = SHomeInfo(
                    pagination=Pagination.from_dict(data["pagination"]),
                    devices=[SHomeDevice.from_dict(device) for device in data.get("deviceList", [])]
                )
                _LOGGER.info("[get_devices] found %d devices", len(self._home_info.devices))

            return self._home_info
            
        except ClientResponseError as e:
            if e.status == 401 and retry_on_401:
                _LOGGER.warning("[get_devices] request 401 - attempting to re-login")
                await self.login()
                return await self.get_devices(retry_on_401=False)
            else:
                _LOGGER.error("[get_devices] request sent successful, but throw error.\n\tstatus: %s\n\theader: %s\n\tbody: %s", e.status, e.headers, e.message)
                _LOGGER.debug("[get_devices] detailed stack-trace", exc_info=True)
                raise
        except Exception as e:
            _LOGGER.error("[get_devices] failed to get devices - %s", e)
            raise


    async def _device_request(self, url_key: str, headers: dict, params: dict, url_params=None, retry_on_401=True) -> dict:
        """Make a generic request to the SHome API."""
        if url_params is None:
            url_params = {}
        _LOGGER.debug("[%s] request headers: %s, params: %s, url_params: %s", url_key, headers, params, url_params)

        try:
            url, method = self._get_url(url_key, **url_params)
            _LOGGER.debug("[%s] fetched URL: [%s] %s", url_key, method, url)

            async with self._session.request(method=method, url=url, headers=headers, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                _LOGGER.debug("[%s] request success.\n\tstatus: %s\n\theader: %s\n\tbody: %s", url_key, response.status, response.headers, data)
                return data


        except ClientResponseError as e:
            if e.status == 401 and retry_on_401:
                _LOGGER.warning("[%s] request 401 - attempting to re-login", url_key)
                await self.login()
                return await self._device_request(url_key, url_params, headers, params, retry_on_401=False)
            else:
                _LOGGER.error("[%s] request sent successful, but throw error.\n\tstatus: %s\n\theader: %s\n\tbody: %s", url_key, e.status, e.headers, e.message)
                _LOGGER.debug("[%s] detailed stack-trace", url_key, exc_info=True)
                raise

        except Exception as e:
            _LOGGER.error("[%s] failed request - %s", url_key, e)
            raise

    async def get_light_info(self, device_id: str) -> SHomeLightInfo:
        """Fetch light information from SHome API."""
        data = await self._device_request(
            url_key="get_light_info",
            headers=self._header_maker.device_header(self._cookie, self._login),
            params=self._param_maker.basic_params(device_id),
            url_params={"device_id": device_id}
        )
        return SHomeLightInfo.from_dict(data)

    async def toggle_all_light(self, device_id: str, state: OnOffStatus):
        await self._device_request(
            url_key="toggle_all_light",
            headers=self._header_maker.device_header(self._cookie, self._login),
            params=self._param_maker.on_off_params(device_id, "0", state),
            url_params={"device_id": device_id}
        )

    async def toggle_single_light(self, device_id: str, light_id: str, state: OnOffStatus):
        await self._device_request(
            url_key="toggle_single_light",
            headers=self._header_maker.device_header(self._cookie, self._login),
            params=self._param_maker.on_off_params(device_id, light_id, state),
            url_params={"device_id": device_id, "light_id": light_id}
        )

    async def toggle_room_light(self, device_id: str, room_id: str, state: OnOffStatus):
        await self._device_request(
            url_key="toggle_room_light",
            headers=self._header_maker.device_header(self._cookie, self._login),
            params=self._param_maker.on_off_params(device_id, room_id, state),
            url_params={"device_id": device_id, "room_id": room_id}
        )

    async def get_sensor_info(self, device_id: str) -> list[SHomeSensorInfo]:
        data = await self._device_request(
            url_key="sensor_info",
            headers=self._header_maker.device_header(self._cookie, self._login),
            params=self._param_maker.basic_params(device_id),
            url_params={"device_id": device_id}
        )
        return SHomeSensorInfo.from_dict(data)
