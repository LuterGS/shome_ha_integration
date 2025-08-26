import logging
from dataclasses import dataclass


_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class CheckAppVersionResponse:
    result: int
    needUpdate: int

    @staticmethod
    def from_dict(data: dict) -> 'CheckAppVersionResponse':
        return CheckAppVersionResponse(
            result=data.get("result", 0),
            needUpdate=int(data.get("needUpdate", '0'))
        )


@dataclass(frozen=True)
class Login:
    home_id: str
    wallpad_id: str
    user_name: str
    user_id: str
    email: str
    dong: str
    ho: str
    user_distinct: str
    biz_id: str
    access_token: str
    join_device_type: str

    @staticmethod
    def from_dict(data: dict) -> 'Login':
        return Login(
            home_id=data.get("homeId", ""),
            wallpad_id=data.get("ihdId", ""),
            user_name=data.get("userName", ""),
            user_id=data.get("userId", ""),
            email=data.get("email", ""),
            dong=data.get("dong", ""),
            ho=data.get("ho", ""),
            user_distinct=data.get("userDstnct", ""),
            biz_id=data.get("bizId", ""),
            access_token=data.get("accessToken", ""),
            join_device_type=data.get("joinDeviceType", "")
        )