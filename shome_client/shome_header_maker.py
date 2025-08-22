import logging

from .const import VERSION_HEADER, OS_TYPE
from .dto.login import Login
from .dto.cookie import Cookie

_LOGGER = logging.getLogger(__name__)

class SHomeHeaderMaker:

    # X headers
    APP_VERSION = VERSION_HEADER
    DEVICE_MODEL = "sm990n"
    OS_TYPE = OS_TYPE
    OS_VERSION = "11"

    # Other headers
    CONNECTION = "Keep-Alive"
    USER_AGENT = "okhttp/3.12.0"
    ACCEPT_LANGUAGE = "en"
    ACCEPT_ENCODING = "gzip"

    # Host headers
    HOST = "shome-api.samsung-ihp.com"

    def _build_default_headers(self):
        return {
            "User-Agent": self.USER_AGENT,
            "X-APP-VERSION": self.APP_VERSION,
            "X-DEVICE-MODEL": self.DEVICE_MODEL,
            "X-OS-TYPE": self.OS_TYPE,
            "X-OS-VERSION": self.OS_VERSION,
            "Connection": self.CONNECTION,
            "Host": self.HOST,
            "Accept-Encoding": self.ACCEPT_ENCODING,
            "Accept-Language": self.ACCEPT_LANGUAGE,
        }

    def check_app_version_header(self):
        default_headers = self._build_default_headers()
        default_headers["Authorization"] = "Bearer"
        return default_headers

    def login_header(self, cookie: Cookie):
        default_headers = self._build_default_headers()
        default_headers["Content-Length"] = "0"
        default_headers["Cookie"] = cookie.to_header_value()
        return default_headers

    def device_header(self, cookie: Cookie, login: Login):
        default_headers = self._build_default_headers()
        default_headers["Authorization"] = f"Bearer {login.access_token}"
        default_headers["Cookie"] = cookie.to_header_value()
        return default_headers

