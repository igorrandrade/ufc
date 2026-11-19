"""Responde à pergunta e às hipóteses da Fase 1 usando os KPIs calculados."""
import json
from html import escape
from .pipeline import ROOT


def build():
    k = json.loads((ROOT / 'outputs/kpis.json').read_text())
    a, u, d = k['all'], k['by_method']['Unânime'], k['by_method']['Dividida']
    fmt = lambda x: f'{x:.2f}'.replace('.', ',')
    annual = [k['by_year_method'][f'{y} Unânime']['concordance'] -
              k['by_year_method'][f'{y} Dividida']['concordance'] for y in (2022, 2023, 2024)]
    supported = a['concordance'] > 50 and u['concordance'] > d['concordance']
    if not supported:
        raise ValueError('Os dados não sustentam a conclusão desta versão; revisar o texto.')
    paragraphs = [
        ('Resposta à pergunta central',
         f'Sim, liderar em golpes significativos conectados foi um indicador associado à vitória nas decisões analisadas. '
         f'O líder venceu {a["C"]} das {a["C"] + a["D"]} lutas classificáveis ({fmt(a["concordance"])}%) '
         f'e perdeu {a["D"]} ({fmt(a["divergence"])}%). Portanto, a liderança acompanhou a vitória na maioria dos casos, '
         'mas não garantiu o resultado. Esta conclusão descreve o UFC de 2022–2024, com três rounds completos e decisão unânime ou dividida.'),
        ('H1 recebe apoio descritivo',
         f'A concordância de {fmt(a["concordance"])}% superou em {fmt(k["H1_excess_pp"])} pontos percentuais '
         'a referência de 50% definida na Fase 1. Escolher o líder em golpes acertou mais resultados históricos que a referência '
         'de escolher aleatoriamente um dos dois atletas. Não se trata de um teste de significância estatística.'),
        ('H2 recebe apoio descritivo',
         f'Nas decisões unânimes, o líder venceu {u["C"]}/{u["C"] + u["D"]} lutas ({fmt(u["concordance"])}%); '
         f'nas divididas, {d["C"]}/{d["C"] + d["D"]} ({fmt(d["concordance"])}%). A diferença foi de '
         f'{fmt(k["H2_difference_pp"])} pontos percentuais a favor das unânimes. A mesma direção apareceu em '
         f'2022, 2023 e 2024: {", ".join(fmt(x) for x in annual)} pontos percentuais, respectivamente. '
         'A contagem, assim, acompanhou menos frequentemente o vencedor nas decisões divididas.'),
        ('Empates e robustez',
         f'As {a["n"]} lutas válidas incluem {a["E"]} empates em golpes, mantidos no painel e retirados apenas '
         f'do denominador da concordância. A cobertura classificável foi {fmt(a["coverage"])}%. '
         f'Atribuir todos os empates aos extremos produz {fmt(a["sensitivity_low"])}% a {fmt(a["sensitivity_high"])}% '
         'de concordância no total válido, ainda acima de 50%. A direção de H2 também permanece nas atribuições extremas. '
         'Esses limites são uma análise de sensibilidade, não intervalos de confiança.'),
        ('O que significa fazer diferença',
         'Os resultados mostram utilidade da liderança em golpes para interpretar o resultado histórico. Não quantificam '
         'o efeito causal de um golpe adicional, o peso isolado da contagem no voto de cada juiz ou a probabilidade de uma '
         'luta futura. A base não contém os votos individuais por round; as divergências não demonstram erro ou viés de arbitragem. '
         'Também não se conclui que vencer a contagem de um round equivale a vencê-lo nos cartões.'),
        ('Aplicação para o analista de cobertura esportiva',
         f'Usar a contagem como evidência contextual, informando período, tipo de decisão e denominador. Nas divididas, '
         f'{d["D"]}/{d["C"] + d["D"]} lutas ({fmt(d["divergence"])}%) tiveram vitória do atleta com menos golpes, '
         'o que exige cuidado ao interpretar apenas o total. O caso Holland × Della Maddalena ilustra uma dessas divergências; '
         'a conclusão provém do conjunto de lutas, não desse exemplo.'),
        ('Cumprimento dos objetivos da Fase 1',
         'A base relacional foi integrada; concordâncias, divergências, empates e denominadores foram calculados; '
         'as decisões foram comparadas no conjunto e em cada ano; o painel permite consultar luta e rounds. '
         'O quarto objetivo específico permanece parcialmente atendido: as consultas foram reconciliadas internamente, '
         'mas a conferência dos campos das 12 fichas oficiais segue pendente por bloqueio de acesso. '
         'Os resultados referem-se ao espelho versionado e devem ser revistos se essa conferência identificar discrepâncias.'),
        ('Papel complementar do Analytics',
         'O modelo com sete variáveis acrescenta uma análise preditiva retrospectiva exigida na Fase 2. '
         'Sua melhora agregada sobre a regra de escolher o líder não mede a contribuição isolada dos golpes significativos '
         'e não é a evidência usada para responder a H1 e H2. As hipóteses são respondidas pelas contagens e proporções acima.')
    ]
    md = '# Conclusão e respostas à Fase 1\n\n' + '\n\n'.join(f'## {title}\n\n{text}' for title, text in paragraphs)
    html = '<h2>Conclusão e respostas à Fase 1</h2><p class="caption">Recorte completo de 2022–2024; esta conclusão não muda com os filtros do Panorama.</p>' + ''.join(
        f'<h3>{escape(title)}</h3><p>{escape(text)}</p>' for title, text in paragraphs)
    (ROOT / 'docs/CONCLUSAO.md').write_text(md, encoding='utf-8')
    return md, html


if __name__ == '__main__':
    print(build()[0])
