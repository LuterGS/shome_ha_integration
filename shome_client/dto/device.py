from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Device:
    id: str
    root_id: str
    model_id: str
    model_name: str
    model_type_name: str
    model_type_id: str
    unique_num: str
    bad_edge_status: bool
    status: bool
    nick_name: str
    battery: int
    zigbee_signal_strength: int
    auto_re_lock: bool
    dummy_mode: bool
    created_at: datetime
    device_total_count: int

    @staticmethod
    def from_dict(data: dict) -> 'Device':
        return Device(
            id=data.get("thngId", ""),
            root_id=data.get("rootThngId", ""),
            model_id=data.get("thngModelId", ""),
            model_name=data.get("thngModelName", ""),
            model_type_id=data.get("thngModelTypeId", ""),
            model_type_name=data.get("thngModelTypeName", ""),
            unique_num=data.get("uniqueNum", ""),
            bad_edge_status=data.get("badEdgeStatus", False),
            status=data.get("status", False),
            nick_name=data.get("nickname", ""),
            battery=data.get("battery", 0),
            zigbee_signal_strength=data.get("zigStrength", 0),
            auto_re_lock=data.get("autoReLock", False),
            dummy_mode=data.get("dummyMode", False),
            created_at=datetime.fromisoformat(data.get("createdAt", "1970-01-01T00:00:00Z").replace('Z', '+00:00')),
            device_total_count=data.get("deviceTotalCount", 0)
        )