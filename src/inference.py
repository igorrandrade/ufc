"""Inferência complementar aos KPIs descritivos (análise exploratória).

* Intervalo de confiança de 95% de Wilson para as taxas de concordância.
* H1: teste binomial bilateral da concordância global contra 50% (acaso).
* H2: teste exato de Fisher bilateral, unânimes x divididas.

O plano da Fase 1 é descritivo; estes testes são um complemento exploratório
e não alteram a resposta às hipóteses. Lê outputs/kpis.json e grava
outputs/inference.json.   Execute da raiz:  python -m src.inference
"""
import json
from math import sqrt

from scipy import stats

from .pipeline import ROOT


def wilson(k, n, z=None):
    """Intervalo de Wilson (em %) para a proporção k/n.

    Preferível ao intervalo normal simples quando a proporção é alta ou n é pequeno.
    `z` padrão = quantil 0,975 da normal (≈ 1,96), para IC de 95%.
    """
    if z is None:
        z = float(stats.norm.ppf(0.975))
    if n <= 0 or not 0 <= k <= n:
        raise ValueError('Wilson exige 0 <= k <= n e n > 0')
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * (centre - half), 100 * (centre + half)


def run():
    """Calcula ICs e testes a partir dos KPIs e exporta o resultado em JSON."""
    k = json.loads((ROOT / 'outputs/kpis.json').read_text(encoding='utf-8'))
    a, u, d = k['all'], k['by_method']['Unânime'], k['by_method']['Dividida']
    out = {
        # H1: sucessos = concordâncias; ensaios = lutas com líder único.
        'H1_binomial_p_vs_50': float(stats.binomtest(a['C'], a['C'] + a['D'], 0.5, alternative='two-sided').pvalue),
        'concordance_ci95': wilson(a['C'], a['C'] + a['D']),
        'unanime_ci95': wilson(u['C'], u['C'] + u['D']),
        'dividida_ci95': wilson(d['C'], d['C'] + d['D']),
    }
    # H2: tabela 2x2 [[C, D] unânimes; [C, D] divididas].
    odds, p = stats.fisher_exact([[u['C'], u['D']], [d['C'], d['D']]], alternative='two-sided')
    out.update(H2_fisher_odds_ratio=float(odds), H2_fisher_p=float(p),
               alternative='two-sided', confidence_level=0.95, wilson_z=float(stats.norm.ppf(0.975)),
               interpretation='Análise exploratória adicional ao plano descritivo da Fase 1.',
               limitations='O recorte reúne todos os confrontos elegíveis do snapshot, não uma amostra aleatória. '
                           'Há atletas repetidos entre lutas; os testes não ajustam essa dependência nem fatores de '
                           'confusão. ICs e p-valores são condicionais ao modelo de independência, não validação '
                           'causal ou garantia de generalização.')
    (ROOT / 'outputs/inference.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    return out


if __name__ == '__main__':
    print(run())
