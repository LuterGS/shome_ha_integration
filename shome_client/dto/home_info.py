from dataclasses import dataclass

from .device import Device
from .pagination import Pagination


@dataclass(frozen=True)
class HomeInfo:
    pagination: Pagination
    devices: list[Device]
