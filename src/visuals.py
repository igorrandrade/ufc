"""Camada de apresentação: gráficos estáticos (PNG) e painel HTML interativo.

O painel é um único HTML autossuficiente: os dados são incorporados ao arquivo
(sem servidor, sem conexão externa) e os filtros funcionam em JavaScript.
O mesmo HTML é exibido dentro do notebook (Colab) e salvo em docs/index.html.
"""
import json
import base64

import matplotlib
matplotlib.use('Agg')  # backend sem interface gráfica (funciona em servidor e Colab)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .conclusions import build as build_conclusions
from .pipeline import ROOT

# Paleta consistente em todo o projeto: azul = unânime/líder, vermelho = dividida/divergência.
BLUE, RED, INK = '#216aa0', '#b63540', '#122235'
HOLLAND_BOUT = '697efaf0d162e877'  # Holland x Della Maddalena (caso ilustrativo)


def _style():
    """Estilo comum dos gráficos (sem bordas superior/direita, tipografia legível)."""
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.spines.top': False,
                         'axes.spines.right': False, 'axes.titleweight': 'bold',
                         'axes.labelcolor': INK, 'text.color': INK})


def _forecast_html(out):
    """Apresenta o teste temporal mensal, sem confundir previsão com classificação."""
    f=pd.read_csv(out/'forecast_2024.csv')
    m=json.loads((out/'forecast_metrics.json').read_text())
    fig,ax=plt.subplots(figsize=(10,4.4))
    for column,label,color in [('rate','Observado',INK),('prediction','Ridge',BLUE),('baseline','Referência histórica','#137f76')]:
        ax.plot(range(12),100*f[column],marker='o',label=label,color=color)
    ax.set_xticks(range(12),[x[5:] for x in f.month]);ax.set_ylim(0,100)
    ax.set_xlabel('Mês de 2024');ax.set_ylabel('Concordância (%)')
    ax.set_title('Previsões feitas antes de observar cada mês',loc='left')
    ax.legend(loc='lower left');ax.grid(axis='y',alpha=.15);fig.tight_layout()
    fig.savefig(out/'forecast.png',dpi=160);plt.close(fig)
    image=base64.b64encode((out/'forecast.png').read_bytes()).decode()
    number=lambda x: f'{x:.2f}'.replace('.',',')
    rows=''.join(f'<tr><td>{x.month}</td><td>{int(x.n)}</td><td>{number(100*x.rate)}%</td><td>{number(100*x.prediction)}%</td><td>{number(100*x.baseline)}%</td><td>{x.feature_cutoff}</td></tr>' for x in f.itertuples())
    return f"""<h2>Concordância prevista para o mês seguinte</h2>
    <p>Alvo: proporção de vitórias do líder entre as decisões elegíveis do próximo mês. Cada previsão usa apenas os três meses anteriores, com coeficientes ajustados até 2023. Não prevê vencedores individuais.</p>
    <div class="cards"><article class="card"><small>Teste temporal</small><div class="value">12 meses</div><div class="caption">Janeiro a dezembro de 2024</div></article><article class="card"><small>Erro absoluto médio: Ridge</small><div class="value">{number(m['model']['mae_pp'])} p.p.</div></article><article class="card"><small>Erro da referência histórica</small><div class="value">{number(m['baseline']['mae_pp'])} p.p.</div><div class="caption">Menor erro é melhor</div></article></div>
    <p class="notice">A referência histórica teve menor erro que a regressão Ridge neste teste. Não há evidência de ganho do modelo mais complexo. A série tem apenas 36 meses e a avaliação é exploratória.</p>
    <article class="panel"><img alt="Concordância observada e prevista por mês em 2024" style="width:100%;max-width:1000px" src="data:image/png;base64,{image}"></article>
    <div class="panel tablewrap"><table><thead><tr><th>Mês</th><th>Lutas</th><th>Observado</th><th>Ridge</th><th>Referência</th><th>Dados até</th></tr></thead><tbody>{rows}</tbody></table><button id="exportforecast">Baixar 12 previsões mensais em CSV</button></div>
    <p>Projeção a partir de dezembro/2024 para janeiro/2025: {number(100*m['next_period']['predicted_rate'])}% pelo Ridge e {number(100*m['next_period']['baseline_rate'])}% pela referência. É uma projeção na origem histórica do estudo, sem verificação contra janeiro/2025, e não uma previsão atual.</p>
    <p class="caption">Treino: nove meses de 2022 após três meses de aquecimento. Seleção de alpha em 2023; reajuste em 21 meses de 2022–2023. Coeficientes congelados no teste de 2024. Alphas comparados: 0,1; 1; 10. Não foi calculado intervalo de previsão calibrado.</p>"""


def _dashboard(out, b, r, p, k, m, q):
    """Injeta os dados no modelo HTML e grava docs/index.html. Retorna o HTML."""
    checks = json.loads((out / 'source_checks.json').read_text()) if (out / 'source_checks.json').exists() else []
    mapping = {'__FC__': pd.read_csv(out/'forecast_2024.csv').to_json(orient='records'), '__DATA__': b.to_json(orient='records', force_ascii=False),
               '__ROUNDS__': r.to_json(orient='records', force_ascii=False),
               '__PRED__': p.to_json(orient='records', force_ascii=False),
               '__METRICS__': json.dumps(m, ensure_ascii=False),
               '__QUALITY__': json.dumps(q, ensure_ascii=False),
               '__CHECKS__': json.dumps(checks, ensure_ascii=False)}
    page = (ROOT / 'src/dashboard_template.html').read_text(encoding='utf-8')
    page = page.replace('__FORECAST_HTML__', _forecast_html(out))
    page = page.replace('__CONCLUSION__', build_conclusions()[1])
    for key, value in mapping.items():
        page = page.replace(key, value.replace('</', '<\\/'))  # evita fechar <script> por acidente
    (ROOT / 'docs/index.html').write_text(page, encoding='utf-8')
    return page


def _concordance(out, k):
    """Gráfico 1: concordância por tipo de decisão (H2)."""
    keys = ['Unânime', 'Dividida']
    v = [k['by_method'][x]['concordance'] for x in keys]
    fig, ax = plt.subplots(figsize=(9.4, 4.5))
    ax.barh(keys[::-1], v[::-1], color=[RED, BLUE], height=.48)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Concordância (%) entre lutas sem empate em golpes')
    ax.set_title('A contagem acompanha mais as decisões unânimes', loc='left', pad=18)
    for i, key in enumerate(keys[::-1]):
        a = k['by_method'][key]
        ax.text(a['concordance'] + 1, i, f"{a['concordance']:.2f}%\n{a['C']}/{a['C'] + a['D']}", va='center', fontsize=11)
    fig.tight_layout(); fig.savefig(out / 'concordance.png', dpi=180); plt.close(fig)


def _years(out, k):
    """Gráfico 2: estabilidade da diferença entre unânimes e divididas por ano."""
    keys, ys = ['Unânime', 'Dividida'], [2022, 2023, 2024]
    fig, ax = plt.subplots(figsize=(9.4, 4.3))
    for key, color in zip(keys, [BLUE, RED]):
        v = [k['by_year_method'][f'{y} {key}']['concordance'] for y in ys]
        ax.plot(ys, v, 'o-', label=key, color=color, linewidth=2.4)
        for x, y in zip(ys, v):
            ax.annotate(f'{y:.1f}%', (x, y), xytext=(0, 9), textcoords='offset points', ha='center', fontsize=10)
    ax.set_ylim(0, 100); ax.set_xticks(ys); ax.set_ylabel('Concordância (%)')
    ax.set_title('A diferença mantém a mesma direção nos três anos', loc='left', pad=18)
    ax.legend(loc='lower right'); ax.grid(axis='y', alpha=.15)
    fig.tight_layout(); fig.savefig(out / 'years.png', dpi=180); plt.close(fig)


def _holland(out, r):
    """Gráfico 3: caso ilustrativo de divergência, golpes por round."""
    g = r[r.bout_id == HOLLAND_BOUT]
    fig, ax = plt.subplots(figsize=(9.4, 4.3))
    xx = np.arange(3)
    for i, (name, color) in enumerate([('Kevin Holland', BLUE), ('Jack Della Maddalena', RED)]):
        d = g[g.fighter == name].sort_values('round')
        bars = ax.bar(xx + (i - .5) * .36, d.sig_landed, width=.34, label=name, color=color)
        ax.bar_label(bars, padding=3)
    ax.set_xticks(xx, ['Round 1', 'Round 2', 'Round 3']); ax.set_ylim(0, 60)
    ax.set_ylabel('Golpes significativos conectados')
    ax.set_title('Holland liderou 127 a 105; Della Maddalena venceu', loc='left', pad=18)
    ax.legend(loc='upper right', fontsize=9)
    fig.tight_layout(); fig.savefig(out / 'holland.png', dpi=180); plt.close(fig)


def _confusion(out, m):
    """Gráfico 4: matriz de confusão do teste de 2024."""
    mat = np.array(m['test_model']['confusion_matrix'])
    fig, ax = plt.subplots(figsize=(9.4, 4.4))
    ax.imshow(mat, cmap='Blues', vmin=0, vmax=198)
    for (i, j), v in np.ndenumerate(mat):
        ax.text(j, i, str(v), ha='center', va='center', fontsize=26, color='white' if v > 100 else INK)
    ax.set_xticks([0, 1], ['Divergência', 'Concordância']); ax.set_yticks([0, 1], ['Divergência', 'Concordância'])
    ax.set_xlabel('Previsto'); ax.set_ylabel('Observado')
    ax.set_title('25 das 49 divergências foram identificadas no teste', pad=18)
    fig.tight_layout(); fig.savefig(out / 'confusion.png', dpi=180); plt.close(fig)


def build():
    """Gera o painel (docs/index.html) e os quatro gráficos de outputs/. Retorna o HTML."""
    out = ROOT / 'outputs'
    b = pd.read_csv(ROOT / 'data/processed/bouts.csv')
    r = pd.read_csv(ROOT / 'data/processed/rounds.csv')
    p = pd.read_csv(out / 'predictions_2024.csv')
    k = json.loads((out / 'kpis.json').read_text())
    m = json.loads((out / 'model_metrics.json').read_text())
    q = json.loads((out / 'quality.json').read_text())
    page = _dashboard(out, b, r, p, k, m, q)
    _style()
    _concordance(out, k); _years(out, k); _holland(out, r); _confusion(out, m)
    print('Dashboard e quatro gráficos gerados.')
    return page


if __name__ == '__main__':
    build()
