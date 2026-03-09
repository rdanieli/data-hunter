import asyncio
import httpx
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class LoteLeilao:
    id: str
    descricao: str
    preco_minimo: float
    valor_avaliacao: float
    desconto_pct: float
    tipo: str
    data_leilao: Optional[str]
    bairro: str
    cidade: str
    url: str
    fonte: str


async def scrape_caixa_leiloes(estado: str = 'PE') -> list:
    lotes = []
    url = 'https://venda-imoveis.caixa.gov.br/sistema/download-lista.asp'
    params = {'UF': estado, 'idTipoImovel': '', 'idSubTipoImovel': '', 'valorInicial': '', 'valorFinal': ''}
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            for row in soup.select('table tr')[1:]:
                cols = row.find_all('td')
                if len(cols) < 8:
                    continue
                try:
                    avaliacao = _preco(cols[5].text)
                    minimo = _preco(cols[6].text)
                    if avaliacao <= 0 or minimo <= 0:
                        continue
                    desconto = 1 - (minimo / avaliacao)
                    lotes.append(LoteLeilao(
                        id='caixa_' + cols[0].text.strip(),
                        descricao=cols[3].text.strip(),
                        preco_minimo=minimo,
                        valor_avaliacao=avaliacao,
                        desconto_pct=round(desconto * 100, 1),
                        tipo='imovel',
                        data_leilao=None,
                        bairro=cols[4].text.strip(),
                        cidade=cols[2].text.strip(),
                        url='https://venda-imoveis.caixa.gov.br',
                        fonte='caixa'
                    ))
                except (IndexError, ValueError):
                    continue
        except Exception as e:
            print(f'[Caixa] Erro: {e}')
    return lotes


async def scrape_megaleiloes(paginas: int = 3) -> list:
    lotes = []
    async with httpx.AsyncClient(timeout=30) as client:
        for page in range(1, paginas + 1):
            try:
                resp = await client.get(f'https://www.megaleiloes.com.br/lotes?page={page}')
                soup = BeautifulSoup(resp.text, 'html.parser')
                for card in soup.select('.lote-card, [class*=lote]'):
                    desc = card.select_one('[class*=title], h2, h3')
                    val_el = card.select_one('[class*=value], [class*=valor]')
                    aval_el = card.select_one('[class*=avaliacao]')
                    link = card.select_one('a[href]')
                    if not val_el:
                        continue
                    minimo = _preco(val_el.text)
                    avaliacao = _preco(aval_el.text) if aval_el else minimo * 1.5
                    lotes.append(LoteLeilao(
                        id='mega_' + str(hash(link['href'] if link else '')),
                        descricao=desc.text.strip() if desc else '',
                        preco_minimo=minimo,
                        valor_avaliacao=avaliacao,
                        desconto_pct=round((1 - minimo / avaliacao) * 100, 1) if avaliacao > 0 else 0,
                        tipo='imovel',
                        data_leilao=None,
                        bairro='', cidade='',
                        url='https://www.megaleiloes.com.br' + (link['href'] if link else ''),
                        fonte='megaleiloes'
                    ))
            except Exception as e:
                print(f'[MegaLeiloes] Erro p{page}: {e}')
    return lotes


def _preco(texto: str) -> float:
    n = re.sub(r'[^\d]', '', str(texto))
    return float(n) if n else 0.0


async def coletar_leiloes(estado: str = 'PE') -> list:
    tasks = [scrape_caixa_leiloes(estado), scrape_megaleiloes()]
    resultados = await asyncio.gather(*tasks, return_exceptions=True)
    todos = [item for r in resultados if isinstance(r, list) for item in r]
    print(f'[ok] Coletados {len(todos)} lotes de leilao')
    return todos
