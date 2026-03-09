import asyncio, httpx, re
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional

HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'pt-BR,pt;q=0.9'}

@dataclass
class ListingImovel:
    id: str
    titulo: str
    preco: float
    area_m2: Optional[float]
    quartos: Optional[int]
    bairro: str
    cidade: str
    url: str
    fonte: str
    tipo: str

def _preco(t): n = re.sub(r'[^\d]', '', str(t)); return float(n) if n else 0.0
def _area(t): m = re.search(r'(\d+)\s*m2', t, re.I); return float(m.group(1)) if m else None
def _qts(t): m = re.search(r'(\d+)\s*(quarto|dorm|suite)', t, re.I); return int(m.group(1)) if m else None

async def scrape_olx(cidade, tipo='apartamento', max_pages=5):
    out = []
    async with httpx.AsyncClient(headers=HEADERS, timeout=30) as c:
        for p in range(max_pages):
            try:
                r = await c.get('https://www.olx.com.br/api/ad-search/v2/search',
                    params={'category': '1080', 'location': cidade, 'q': tipo, 'size': 50, 'page': p})
                r.raise_for_status()
                for ad in r.json().get('ads', []):
                    preco = _preco(ad.get('price', {}).get('value', '0'))
                    if preco < 10_000: continue
                    out.append(ListingImovel(
                        id=f'olx_{ad["id"]}', titulo=ad.get('title', ''), preco=preco,
                        area_m2=_area(ad.get('title', '')), quartos=_qts(ad.get('title', '')),
                        bairro=ad.get('location', {}).get('neighbourhood', ''),
                        cidade=ad.get('location', {}).get('city', cidade),
                        url=ad.get('url', ''), fonte='olx', tipo=tipo))
            except Exception as e: print(f'[OLX] p{p}: {e}')
    return out

async def scrape_zap(cidade, tipo='apartamento', max_pages=5):
    out = []
    slug = cidade.lower().replace(' ', '-')
    async with httpx.AsyncClient(headers=HEADERS, timeout=30) as c:
        for p in range(1, max_pages + 1):
            try:
                r = await c.get(f'https://www.zapimoveis.com.br/venda/{tipo}s/{slug}/?pagina={p}')
                r.raise_for_status()
                soup = BeautifulSoup(r.text, 'html.parser')
                for card in soup.select('[data-type="property"]'):
                    preco_el = card.select_one('[class*="price"]')
                    titulo_el = card.select_one('[class*="title"]')
                    bairro_el = card.select_one('[class*="address"]')
                    area_el = card.select_one('[class*="area"]')
                    link_el = card.select_one('a[href]')
                    if not preco_el: continue
                    preco = _preco(preco_el.text)
                    if preco < 10_000: continue
                    out.append(ListingImovel(
                        id=f'zap_{hash(link_el["href"] if link_el else "")}',
                        titulo=titulo_el.text.strip() if titulo_el else '',
                        preco=preco, area_m2=_area(area_el.text if area_el else ''),
                        quartos=_qts(titulo_el.text if titulo_el else ''),
                        bairro=bairro_el.text.strip() if bairro_el else '', cidade=cidade,
                        url='https://www.zapimoveis.com.br' + (link_el['href'] if link_el else ''),
                        fonte='zap', tipo=tipo))
            except Exception as e: print(f'[ZAP] p{p}: {e}')
    return out

async def coletar_todos(cidade, tipo='apartamento'):
    resultados = await asyncio.gather(scrape_olx(cidade, tipo), scrape_zap(cidade, tipo), return_exceptions=True)
    todos = [item for r in resultados if isinstance(r, list) for item in r]
    print(f'[v] {len(todos)} imoveis em {cidade}')
    return todos
