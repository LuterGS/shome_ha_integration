from dataclasses import dataclass


@dataclass(frozen=True)
class Pagination:
    offset: int
    limit: int
    total: int

    @staticmethod
    def from_dict(data: dict) -> 'Pagination':
        return Pagination(
            offset=data.get("offset", 0),
            limit=data.get("limit", 0),
            total=data.get("total", 0)
        )
