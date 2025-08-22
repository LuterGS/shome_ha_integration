from dataclasses import dataclass

from .device import SHomeDevice
from .pagination import Pagination


@dataclass(frozen=True)
class SHomeInfo:
    pagination: Pagination
    devices: list[SHomeDevice]
