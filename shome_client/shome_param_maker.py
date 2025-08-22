import hashlib
import logging

from datetime import datetime, timezone

from .const import APP_NAME, OS_TYPE, VERSION_PARAM
from .dto.light import OnOffStatus
from .dto.login import Login

_LOGGER = logging.getLogger(__name__)

class SHomeParamMaker:

    APP_NAME = APP_NAME
    OS_TYPE = OS_TYPE
    VERSION = VERSION_PARAM
    LANGUAGE = "ENG"

    def _get_hash(self, data: list[str]) -> str:
        data_str = "".join(data)
        msg = f"IHRESTAPI{data_str}".encode("utf-8")
        return hashlib.sha512(msg).hexdigest()

    def check_app_version_params(self):
        current_date = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
        hash_data = self._get_hash([self.APP_NAME, self.OS_TYPE,  self.VERSION, current_date])
        return {
            "appName": self.APP_NAME,
            "osType": self.OS_TYPE,
            "currentVersion": self.VERSION,
            "createDate": current_date,
            "hashData": hash_data
        }

    def login_params(self, credential: dict):
        current_date = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")

        hash_data = self._get_hash([credential['username'], credential['password'], credential['device_id'], self.LANGUAGE, current_date])
        return {
            "userId": credential['username'],
            "password": credential['password'],
            "mobileDeviceIdno": credential['device_id'],
            "appRegstId": "",
            "language": self.LANGUAGE,
            "createDate": current_date,
            "hashData": hash_data
        }

    def basic_params(self, device_id: str):
        current_date = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
        hash_data = self._get_hash([device_id, current_date])
        return {
            "createDate": current_date,
            "hashData": hash_data
        }

    def on_off_params(self, device_id: str, sub_device_id: str, state: OnOffStatus):
        create_date = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
        hash_data = self._get_hash([device_id, sub_device_id, state.name, create_date])
        return {
            "state": state.name,
            "createDate": create_date,
            "hashData": hash_data
        }
