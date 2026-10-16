import re

def normalize_index_data(text: str) -> list[dict]:
    """Parse the documented iFinD index_data markdown table into the shared model."""
    rows=[]
    for line in (text or '').splitlines():
        if not line.startswith('|') or '证券代码' in line or '---' in line: continue
        cells=[x.strip() for x in line.strip().strip('|').split('|')]
        if len(cells)<6: continue
        def num(v):
            raw=v.replace(',',''); m=re.search(r'-?[\d.]+',raw)
            if not m: return None
            value=float(m.group())
            if '万亿' in raw: value*=1e12
            elif '亿' in raw: value*=1e8
            elif '万' in raw: value*=1e4
            return value
        rows.append({'symbol':cells[0],'name':cells[1],'date':cells[2],'close':num(cells[3]),'volume':num(cells[4]),'turnover':num(cells[5]),'source':'iFinD MCP','status':'REAL'})
    return rows
