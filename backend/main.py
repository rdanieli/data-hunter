import asyncio, json
from datetime import datetime
from scraper_imoveis import coletar_todos as coletar_imoveis
from scraper_leiloes import coletar_leiloes
from price_engine import MotorPreco


async def rodar_ciclo(cidade='Recife', estado='PE'):
    print('[1/3] Coletando dados...')
    imoveis, lotes = await asyncio.gather(
        coletar_imoveis(cidade, 'apartamento'),
        coletar_leiloes(estado)
    )

    print('[2/3] Analisando anomalias...')
    anomalias = MotorPreco().processar_tudo(imoveis, lotes)

    print('[3/3] Oportunidades encontradas:')
    for i, a in enumerate(anomalias[:10], 1):
        print(f'#{i} score={a.score_oportunidade} | {a.titulo}')
        print(f'   R$ {a.preco_anunciado:,.0f} vs mercado R$ {a.preco_mercado_estimado:,.0f}')
        print(f'   {a.motivo}')

    with open('output_alertas.json', 'w') as f:
        json.dump({'anomalias': [vars(a) for a in anomalias]}, f, indent=2, ensure_ascii=False)
    return anomalias


if __name__ == '__main__':
    asyncio.run(rodar_ciclo())
