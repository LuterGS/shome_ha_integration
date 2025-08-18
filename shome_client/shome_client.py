import asyncio
import logging
from typing import Optional, Tuple

from aiohttp import ClientResponseError
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .dto.cookie import Cookie
from .dto.device import Device
from .dto.device_type import DeviceType
from .dto.home_info import HomeInfo
from .dto.light import LightInfo, LightStatus
from .dto.login import Login
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
        self._home_info: Optional[HomeInfo] = None
        self._header_maker = SHomeHeaderMaker()
        self._param_maker = SHomeParamMaker()


    def set_credential(self, credential: dict):
        """Set the credentials for the client."""
        self._credential = credential
        _LOGGER.debug("SHomeClient: Credentials set for user: %s", credential['username'])


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
            device: Device = kwargs['device']
            return f"https://shome-api.samsung-ihp.com/v18/settings/light/{device.model_name}.{device.unique_num}", "GET"
        elif url_type == "toggle_all_light":
            device: Device = kwargs['device']
            return f"https://shome-api.samsung-ihp.com/v18/settings/light/{device.model_name}.{device.unique_num}/0/on-off", "PUT"
        elif url_type == "toggle_single_light":
            device: Device = kwargs['device']
            light_id = kwargs['light_id']
            return f"https://shome-api.samsung-ihp.com/v18/settings/light/{device.model_name}.{device.unique_num}/{light_id}/on-off", "PUT"
        else:
            raise ValueError(f"Unknown URL type: {url_type}")


    def _determine_device_type(self, device: Device) -> DeviceType:
        if device.model_type_id == 'TD00000069':
            return DeviceType.LIGHT
        return DeviceType.ELSE


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
                _LOGGER.info("[login] got session cookies - JSESSIONID: %s, WMONID: %s",self._cookie.JSESSIONID, self._cookie.WMONID)

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


    async def get_devices(self, retry_on_401=True):
        """Fetch list of devices from SHome API."""
        _LOGGER.info("[get_devices] fetching device list")
        
        try:
            if self._login is None:
                await self.login()

            url, method = self._get_url("list_device")
            _LOGGER.debug("[get_devices] request URL: %s", url)
            async with self._session.request(
                method=method, url=url,
                headers=self._header_maker.list_device_header(self._cookie, self._login),
                params=self._param_maker.list_devices_params(self._login)
            ) as response:
                response.raise_for_status()
                data = await response.json()
                self._home_info = HomeInfo(
                    pagination=Pagination.from_dict(data["pagination"]),
                    devices=[Device.from_dict(device) for device in data.get("deviceList", [])]
                )
                _LOGGER.info("[get_devices] found %d devices", len(self._home_info.devices))
                
            total_result = []
            for device in self._home_info.devices:
                device_info = {
                    "id": device.id,
                    "name": device.nick_name,
                    "model": device.model_id,
                    "type": device.model_type_name,
                    "type_id": device.model_type_id
                }
                total_result.append(device_info)
                _LOGGER.debug("[get_devices] device: %s", device_info)
                
            return total_result
            
        except ClientResponseError as e:
            if e.status == 401 and retry_on_401:
                _LOGGER.warning("[get_devices] request 401 - attempting to re-login")
                await self.login()
                return await self.get_devices(retry_on_401=False)
            else:
                _LOGGER.error("[get_devices] failed to get devices - %s", str(e))
                raise
        except Exception as e:
            _LOGGER.error("[get_devices] failed to get devices - %s", str(e))
            raise


    async def _device_request(self, url_key: str, device: Device, headers: dict, params: dict, url_params=None, retry_on_401=True) -> dict:
        """Make a generic request to the SHome API."""
        if url_params is None:
            url_params = {}
        _LOGGER.debug("[%s] request with device: %s, headers: %s, params: %s", url_key, device, headers, params)

        try:
            url_params['device'] = device
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
                _LOGGER.error("[%s] failed request - %s", url_key, e)
                raise

        except Exception as e:
            _LOGGER.error("[%s] failed request - %s", url_key, e)
            raise

    async def _get_device(self, device_type: DeviceType) -> Optional[Device]:
        """Get the first device of a specific type."""
        if not self._home_info:
            await self.get_devices()

        for device in self._home_info.devices:
            if self._determine_device_type(device) == device_type:
                return device
        return None

    async def get_light_info(self) -> LightInfo:
        """Fetch light information from SHome API."""
        device = await self._get_device(DeviceType.LIGHT)
        if device is None:
            _LOGGER.error("[get_light_info] no light device found")
            raise ValueError("No light device found")

        response = await self._device_request(
            url_key="get_light_info",
            device=device,
            headers=self._header_maker.get_light_info_header(self._cookie, self._login, device),
            params=self._param_maker.get_light_info_params(device)
        )
        return LightInfo.from_dict(response)


    async def toggle_all_light(self, state: LightStatus):
        device = await self._get_device(DeviceType.LIGHT)
        if device is None:
            _LOGGER.error("[toggle_all_light] no light device found")
            raise ValueError("No light device found")

        await self._device_request(
            url_key="toggle_all_light",
            device=device,
            headers=self._header_maker.toggle_light_header(self._cookie, self._login, device),
            params=self._param_maker.toggle_light_params(device, "0", state),
        )


    async def toggle_single_light(self, light_id: str, state: LightStatus):
        device = await self._get_device(DeviceType.LIGHT)
        if device is None:
            _LOGGER.error("[toggle_single_light] no light device found")
            raise ValueError("No light device found")

        await self._device_request(
            url_key="toggle_single_light",
            device=device,
            headers=self._header_maker.toggle_light_header(self._cookie, self._login, device),
            params=self._param_maker.toggle_light_params(device, light_id, state),
            url_params={"light_id": light_id}
        )
