from dataclasses import dataclass
from typing import Optional
import statistics


@dataclass
class AnomaliaPreco:
    listing_id: str
    titulo: str
    preco_anunciado: float
    preco_mercado_estimado: float
    desconto_pct: float
    score_oportunidade: float
    motivo: str
    vertical: str
    url: str
    fonte: str
    bairro: str


class MotorPreco:
    DESCONTO_MINIMO = 0.15
    SCORE_BOOST_LEILAO = 10

    def analisar_lote(self, lote, todos_lotes):
        if lote.valor_avaliacao <= 0:
            return None
        desconto = 1 - (lote.preco_minimo / lote.valor_avaliacao)
        if desconto < self.DESCONTO_MINIMO:
            return None
        score = min(100, desconto * 200 + self.SCORE_BOOST_LEILAO)
        return AnomaliaPreco(
            listing_id=lote.id, titulo=lote.descricao[:80],
            preco_anunciado=lote.preco_minimo,
            preco_mercado_estimado=lote.valor_avaliacao,
            desconto_pct=round(desconto * 100, 1),
            score_oportunidade=round(score, 1),
            motivo='Leilao abaixo da avaliacao oficial',
            vertical='leilao', url=lote.url, fonte=lote.fonte, bairro=lote.bairro)

    def analisar_imovel(self, imovel, mercado):
        comp = [m for m in mercado if m.id != imovel.id and m.tipo == imovel.tipo
                and (m.bairro == imovel.bairro or m.cidade == imovel.cidade) and m.preco > 0]
        if len(comp) < 5:
            comp = [m for m in mercado if m.tipo == imovel.tipo and m.preco > 0]
        if len(comp) < 3:
            return None
        precos = [c.preco for c in comp]
        mediana = statistics.median(precos)
        desvio = statistics.stdev(precos) if len(precos) > 1 else mediana * 0.3
        z = (imovel.preco - mediana) / desvio if desvio > 0 else 0
        desconto = 1 - (imovel.preco / mediana)
        if z > -1.5 or desconto < self.DESCONTO_MINIMO:
            return None
        return AnomaliaPreco(
            listing_id=imovel.id, titulo=imovel.titulo[:80],
            preco_anunciado=imovel.preco, preco_mercado_estimado=mediana,
            desconto_pct=round(desconto * 100, 1),
            score_oportunidade=round(min(100, abs(z) * 20 + desconto * 100), 1),
            motivo=str(round(desconto*100)) + '% abaixo da mediana do bairro',
            vertical='imovel', url=imovel.url, fonte=imovel.fonte, bairro=imovel.bairro)

    def processar_tudo(self, imoveis, lotes):
        anomalias = [a for i in imoveis for a in [self.analisar_imovel(i, imoveis)] if a]
        anomalias += [a for l in lotes for a in [self.analisar_lote(l, lotes)] if a]
        return sorted(anomalias, key=lambda x: x.score_oportunidade, reverse=True)
