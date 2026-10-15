import sys
from pathlib import Path
from typing import Any
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError: pass

class IFIndProvider:
    name = "iFinD MCP"
    def __init__(self, caller=None):
        self.caller = caller
    def index_history(self, symbol: str = "沪深300", periods: int = 20) -> dict[str, Any]:
        query=f"{symbol}过去{periods}个交易日的涨跌幅和收盘点数"
        if self.caller is None:
            sys.path.insert(0, str(Path(__file__).parents[3] / '.codex'))
            from call import call
            self.caller = call
        result=self.caller("index", "index_data", {"query": query})
        return {"source": self.name, "query": query, "raw": result}
