from dataclasses import dataclass


@dataclass(frozen=True)
class Cookie:
    JSESSIONID: str
    WMONID: str

    def to_header(self) -> dict:
        return {
            "Cookie": f"JSESSIONID={self.JSESSIONID}; WMONID={self.WMONID}"
        }

    def to_header_value(self) -> str:
        return f"JSESSIONID={self.JSESSIONID}; WMONID={self.WMONID}"