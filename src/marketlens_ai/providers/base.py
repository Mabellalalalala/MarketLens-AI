from typing import Protocol
class MarketDataProvider(Protocol):
    name: str
    def index_history(self, symbol: str, periods: int) -> dict: ...
