"""Pipeline de dados: coleta versionada, limpeza, modelo relacional e KPIs.

Etapas (CRISP-DM: preparação dos dados):
    1. collect()          -> baixa/valida os 3 CSVs do snapshot fixado (SHA-256).
    2. select_bouts()     -> concilia aliases de eventos, aplica o recorte do projeto.
    3. build_bout_rows()  -> valida rounds, agrega por atleta e classifica C/D/E.
    4. create_database()  -> cria o SQLite a partir de sql/schema.sql (PK/FK/CHECK).
    5. build()            -> orquestra tudo e grava CSVs, KPIs e evidências de qualidade.

Execute da raiz do repositório:  python -m src.pipeline
Nenhum dado sintético integra a análise.
"""
from pathlib import Path
import hashlib
import json
import re
import sqlite3
from urllib.request import urlopen

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Constantes de reprodutibilidade
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]

# Commit do espelho Greco1899/scrape_ufc_stats identificado na Fase 1.
COMMIT = 'c742842f29466758fedc3906dbad28d6d320a8da'

# SHA-256 esperado de cada arquivo bruto: qualquer alteração interrompe o pipeline.
HASHES = {
    'ufc_event_details.csv': '07355c6e414bb5932a7a0f97e4088388ff7391876b7a9ab792433c83f5285841',
    'ufc_fight_results.csv': 'b99d94a82984f07ec34d9f04423fd7edd67ea28c365621a144e05aec64f3a840',
    'ufc_fight_stats.csv': 'f5b316d5e745bd89da921b2c9711ec9209c2fa39dcbcd80bcb063b62d9175bcb',
}

# Recorte analítico definido na Fase 1.
YEARS = (2022, 2024)
VALID_METHODS = ['Decision - Unanimous', 'Decision - Split']


# --------------------------------------------------------------------------
# 1. Coleta
# --------------------------------------------------------------------------
def collect():
    """Baixa somente os arquivos ausentes e exige os hashes do snapshot da Fase 1.

    Retorna um dicionário {nome do arquivo: DataFrame de strings}. Todos os campos
    são lidos como texto (dtype=str) para que valores vazios nunca virem zero.
    """
    raw = ROOT / 'data/raw'
    raw.mkdir(parents=True, exist_ok=True)
    manifest = []
    for name, expected in HASHES.items():
        path = raw / name
        url = f'https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/{COMMIT}/{name}'
        if not path.exists():
            with urlopen(url, timeout=90) as response:
                payload = response.read()
            if hashlib.sha256(payload).hexdigest() != expected:
                raise ValueError(f'Hash inesperado: {name}')
            path.write_bytes(payload)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != expected:  # integridade do dado bruto
            raise ValueError(f'Arquivo alterado: {name}')
        manifest.append(dict(file=name, bytes=path.stat().st_size, sha256=digest, url=url))
    (ROOT / 'outputs').mkdir(exist_ok=True)
    (ROOT / 'outputs/manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    return {n: pd.read_csv(raw / n, dtype=str, keep_default_na=False).apply(lambda c: c.str.strip())
            for n in HASHES}


# --------------------------------------------------------------------------
# Funções puras de transformação (cobertas por testes unitários)
# --------------------------------------------------------------------------
def pair(value):
    """Converte 'acertos of tentativas' em (acertos, tentativas).

    Exemplo: '12 of 30' -> (12, 30). Vazio ou malformado levanta ValueError,
    para que ausência de dado nunca seja confundida com zero.
    """
    match = re.fullmatch(r'(\d+) of (\d+)', str(value))
    if not match:
        raise ValueError('par ausente ou malformado')
    landed, attempted = map(int, match.groups())
    if landed > attempted:
        raise ValueError('acertos acima das tentativas')
    return landed, attempted


def outcome_winner(bout, outcome):
    """Obtém o vencedor a partir de 'A vs. B' e do OUTCOME ('W/L' = A venceu)."""
    names = bout.split(' vs. ')
    if len(names) != 2 or outcome not in ['W/L', 'L/W']:
        raise ValueError('vencedor ambíguo')
    return names[0 if outcome == 'W/L' else 1]


def classify(a, b, winner):
    """Classifica a luta: 'C' (líder venceu), 'D' (líder perdeu) ou 'E' (empate em golpes)."""
    if a['sig_landed'] == b['sig_landed']:
        return 'E'
    leader = a if a['sig_landed'] > b['sig_landed'] else b
    return 'C' if leader['fighter'] == winner else 'D'


def kpis(frame):
    """Calcula os KPIs de um conjunto de lutas (coluna `status` com C/D/E).

    concordance = 100*C/(C+D)   divergence = 100*D/(C+D)   coverage = 100*(C+D)/N
    sensitivity_low/high atribuem todos os empates à divergência / à concordância.
    Denominador zero devolve None (indicador "não calculável").
    """
    c = int((frame.status == 'C').sum())
    d = int((frame.status == 'D').sum())
    e = int((frame.status == 'E').sum())
    n = c + d + e
    return dict(n=n, C=c, D=d, E=e,
                concordance=100 * c / (c + d) if c + d else None,
                divergence=100 * d / (c + d) if c + d else None,
                coverage=100 * (c + d) / n if n else None,
                sensitivity_low=100 * c / n if n else None,
                sensitivity_high=100 * (c + e) / n if n else None)


def optional_int(value):
    """Inteiro não negativo opcional (ex.: knockdowns); inválido vira NaN, não zero."""
    try:
        x = float(value)
        return int(x) if x >= 0 and x.is_integer() else np.nan
    except ValueError:
        return np.nan


def control_seconds(value):
    """Converte tempo de controle 'm:ss' em segundos (0 a 300); inválido vira NaN."""
    match = re.fullmatch(r'(\d+):([0-5]\d)', value)
    if not match:
        return np.nan
    m, s = map(int, match.groups())
    return 60 * m + s if 60 * m + s <= 300 else np.nan


# --------------------------------------------------------------------------
# 2. Seleção das lutas do recorte
# --------------------------------------------------------------------------
def select_bouts(tables, audit):
    """Aplica datas, concilia aliases de evento e filtra o recorte do projeto.

    Retorna (candidates, joined, bad_urls):
        candidates : uma linha por luta elegível (resultado oficial)
        joined     : estatísticas por atleta/round já ligadas à URL, sem duplicatas
        bad_urls   : lutas cujas duplicatas divergem entre si (serão excluídas)
    """
    ev, res, st = tables['ufc_event_details.csv'], tables['ufc_fight_results.csv'], tables['ufc_fight_stats.csv']
    audit['raw_rows'] = {k: len(v) for k, v in tables.items()}

    # Datas do catálogo de eventos; o nome do evento precisa ser único.
    ev['date'] = pd.to_datetime(ev.DATE, format='%B %d, %Y', errors='coerce')
    if ev.EVENT.duplicated().any():
        raise ValueError('Evento ambíguo no catálogo')
    res = res.merge(ev[['EVENT', 'date', 'LOCATION']], on='EVENT', how='left', validate='many_to_one')
    audit['result_rows_without_date_before_alias'] = int(res.date.isna().sum())

    # A URL concilia nomes alternativos do mesmo evento; uma URL não pode ter duas datas.
    if res.groupby('URL').date.nunique().gt(1).any():
        raise ValueError('Datas conflitantes para a mesma URL')
    res['date'] = res.groupby('URL').date.transform('max')
    audit['result_rows_without_date_after_alias'] = int(res.date.isna().sum())

    # Registros sem data identificável ficam isolados; não se inventa ano.
    processed = ROOT / 'data/processed'
    processed.mkdir(exist_ok=True)
    res[res.date.isna()][['EVENT', 'BOUT', 'URL']].to_csv(processed / 'unresolved_dates.csv', index=False)

    # Recorte: período, 3 rounds de 5 min encerrados em 5:00, decisão unânime/dividida, vencedor definido.
    in_period = res[res.date.dt.year.between(*YEARS)].copy()
    audit['bouts_in_period'] = int(in_period.URL.nunique())
    mask = ((in_period['TIME FORMAT'] == '3 Rnd (5-5-5)') & (in_period.ROUND == '3') & (in_period.TIME == '5:00')
            & in_period.METHOD.isin(VALID_METHODS) & in_period.OUTCOME.isin(['W/L', 'L/W']))
    candidates = in_period[mask].copy()
    audit['eligible_result_rows'] = len(candidates)

    # Duplicatas (aliases) só podem ser removidas se forem idênticas entre si.
    for col in ['BOUT', 'OUTCOME', 'METHOD', 'ROUND', 'TIME', 'TIME FORMAT', 'WEIGHTCLASS']:
        if candidates.groupby('URL')[col].nunique().gt(1).any():
            raise ValueError(f'Resultado conflitante: {col}')
    mapping = candidates[['EVENT', 'BOUT', 'URL']].drop_duplicates()
    if mapping.duplicated(['EVENT', 'BOUT']).any():
        raise ValueError('Chave textual ambígua no recorte')
    candidates = candidates.sort_values(['URL', 'EVENT']).drop_duplicates('URL')
    audit['eligible_bouts'] = len(candidates)

    # Estatísticas por round ligadas à luta via (EVENT, BOUT); depois, deduplicação.
    joined = st.merge(mapping, on=['EVENT', 'BOUT'], how='inner', validate='many_to_one')
    audit['round_rows_before_dedup'] = len(joined)
    keys = ['URL', 'FIGHTER', 'ROUND']
    values = [c for c in st.columns if c not in ['EVENT', 'BOUT'] + keys]
    conflict = joined.groupby(keys)[values].nunique().max(axis=1).gt(1)
    bad_urls = set(conflict[conflict].index.get_level_values(0))
    joined = joined.drop_duplicates(keys)
    audit['round_rows_after_dedup'] = len(joined)
    return candidates, joined, bad_urls


# --------------------------------------------------------------------------
# 3. Validação por luta e construção dos registros
# --------------------------------------------------------------------------
def build_bout_rows(candidates, joined, bad_urls):
    """Valida cada luta e devolve (lutas, rounds, exclusões).

    Uma luta só é aceita com 2 atletas x 3 rounds (6 linhas) e números válidos.
    Qualquer violação gera um registro em `exclusions` em vez de dado parcial.
    """
    groups = {url: g for url, g in joined.groupby('URL')}
    exclusions, rounds, bouts = [], [], []
    for _, r in candidates.iterrows():
        try:
            if r.URL in bad_urls:
                raise ValueError('duplicatas conflitantes')
            names = r.BOUT.split(' vs. ')
            g = groups.get(r.URL, pd.DataFrame())
            expected = {(f, f'Round {i}') for f in names for i in (1, 2, 3)}
            if len(names) != 2 or len(g) != 6 or set(zip(g.FIGHTER, g.ROUND)) != expected:
                raise ValueError('grade de atletas/rounds incompleta')

            # Linhas por atleta e round (grão do fato fact_round).
            rr = []
            for _, s in g.iterrows():
                landed, attempted = pair(s['SIG.STR.'])
                try:
                    td, _ = pair(s['TD'])
                except ValueError:  # quedas ausentes: NaN, nunca zero
                    td = np.nan
                rr.append(dict(bout_id=r.URL.rsplit('/', 1)[-1], fighter=s.FIGHTER, round=int(s.ROUND[-1]),
                               sig_landed=landed, sig_attempted=attempted, td_landed=td,
                               kd=optional_int(s.KD), control_seconds=control_seconds(s.CTRL)))

            # Totais por atleta (soma dos 3 rounds; min_count preserva ausências).
            total = pd.DataFrame(rr).groupby('fighter')[
                ['sig_landed', 'sig_attempted', 'td_landed', 'kd', 'control_seconds']
            ].agg(lambda x: x.sum(min_count=len(x)))
            totals = [dict(fighter=f, **total.loc[f].to_dict()) for f in names]
            winner = outcome_winner(r.BOUT, r.OUTCOME)
            status = classify(*totals, winner)

            # Líder (a) e adversário (b); desempate por nome mantém a ordem determinística.
            a, b = sorted(totals, key=lambda x: (-x['sig_landed'], x['fighter']))
            ar = sorted([x for x in rr if x['fighter'] == a['fighter']], key=lambda x: x['round'])
            br = sorted([x for x in rr if x['fighter'] == b['fighter']], key=lambda x: x['round'])

            row = dict(bout_id=rr[0]['bout_id'], date=r.date.strftime('%Y-%m-%d'), year=int(r.date.year),
                       event=r.EVENT, method='Unânime' if r.METHOD.endswith('Unanimous') else 'Dividida',
                       weightclass=r.WEIGHTCLASS, fighter_a=names[0], fighter_b=names[1], winner=winner,
                       status=status, leader=a['fighter'] if status != 'E' else '',
                       other=b['fighter'] if status != 'E' else '',
                       sig_a=int(totals[0]['sig_landed']), sig_b=int(totals[1]['sig_landed']), url=r.URL)

            # Variáveis do modelo preditivo: sempre "líder menos adversário".
            row['sig_margin'] = a['sig_landed'] - b['sig_landed']
            row['attempt_margin'] = a['sig_attempted'] - b['sig_attempted']
            row['accuracy_margin'] = ((a['sig_landed'] / a['sig_attempted'] if a['sig_attempted'] else np.nan)
                                      - (b['sig_landed'] / b['sig_attempted'] if b['sig_attempted'] else np.nan))
            # Saldo de rounds em que cada um liderou a contagem (não são rounds dos cartões).
            row['round_margin'] = sum(int(x['sig_landed'] > y['sig_landed']) - int(x['sig_landed'] < y['sig_landed'])
                                      for x, y in zip(ar, br))
            for col in ['td_landed', 'kd', 'control_seconds']:
                row[col + '_margin'] = a[col] - b[col]
            bouts.append(row)
            rounds.extend(rr)
        except (ValueError, AttributeError) as error:
            exclusions.append(dict(url=r.URL, reason=str(error)))
    return bouts, rounds, exclusions


# --------------------------------------------------------------------------
# 4. Banco de dados relacional
# --------------------------------------------------------------------------
def create_database(bouts, rounds, path):
    """Cria o SQLite a partir de sql/schema.sql e carrega os dados tratados.

    As restrições PK/FK/CHECK do esquema validam a carga. Ao final executa
    `integrity_check` e `foreign_key_check`; qualquer problema interrompe o pipeline.
    """
    if path.exists():
        path.unlink()
    with sqlite3.connect(path) as conn:
        conn.executescript((ROOT / 'sql/schema.sql').read_text(encoding='utf-8'))
        fighters = pd.DataFrame({'fighter_id': range(1, rounds.fighter.nunique() + 1),
                                 'fighter': sorted(set(rounds.fighter))})
        fighters.to_sql('dim_fighter', conn, index=False, if_exists='append')
        bouts.to_sql('fact_bout', conn, index=False, if_exists='append')
        (rounds.merge(fighters, on='fighter', validate='many_to_one').drop(columns='fighter')
               [['bout_id', 'fighter_id', 'round', 'sig_landed', 'sig_attempted', 'td_landed', 'kd', 'control_seconds']]
               .to_sql('fact_round', conn, index=False, if_exists='append'))
        assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert conn.execute('PRAGMA foreign_key_check').fetchall() == []
        # Reconciliação: a visão de KPIs deve cobrir todas as lutas carregadas.
        total = pd.read_sql('SELECT SUM(n) n FROM vw_bout_kpis', conn).iloc[0, 0]
        assert int(total) == len(bouts)


# --------------------------------------------------------------------------
# 5. Orquestração
# --------------------------------------------------------------------------
def build():
    """Executa a preparação completa e devolve (DataFrame de lutas, DataFrame de rounds)."""
    audit = {}
    tables = collect()
    candidates, joined, bad_urls = select_bouts(tables, audit)
    bouts, rounds, exclusions = build_bout_rows(candidates, joined, bad_urls)

    p = ROOT / 'data/processed'
    b = pd.DataFrame(bouts).sort_values(['date', 'bout_id']).reset_index(drop=True)
    rd = pd.DataFrame(rounds)
    b.to_csv(p / 'bouts.csv', index=False)
    rd.to_csv(p / 'rounds.csv', index=False)
    pd.DataFrame(exclusions, columns=['url', 'reason']).to_csv(p / 'exclusions.csv', index=False)
    audit.update(valid_bouts=len(b), excluded_bouts=len(exclusions), valid_round_rows=len(rd),
                 optional_missing=rd.isna().sum().to_dict())

    # KPIs globais e por recorte (método, ano e ano x método).
    summary = {'all': kpis(b),
               'by_method': {str(m): kpis(g) for m, g in b.groupby('method')},
               'by_year': {str(y): kpis(g) for y, g in b.groupby('year')},
               'by_year_method': {f'{y} {m}': kpis(g) for (y, m), g in b.groupby(['year', 'method'])}}
    summary['H1_excess_pp'] = summary['all']['concordance'] - 50
    summary['H2_difference_pp'] = (summary['by_method']['Unânime']['concordance']
                                   - summary['by_method']['Dividida']['concordance'])
    for name, obj in [('quality', audit), ('kpis', summary)]:
        (ROOT / f'outputs/{name}.json').write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

    create_database(b, rd, p / 'ufc.sqlite')

    # Amostra de 2 lutas por ano e método para a conferência externa das fichas.
    sample = (b.groupby(['year', 'method'], group_keys=False)
               .apply(lambda g: g.sort_values('url').head(2), include_groups=False).reset_index())
    sample[['bout_id', 'url']].to_csv(p / 'source_check_sample.csv', index=False)
    print(json.dumps({'quality': audit, 'kpis': summary}, ensure_ascii=False, indent=2))
    return b, rd


if __name__ == '__main__':
    build()
