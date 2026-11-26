"""Conferência de acessibilidade das fichas oficiais (UFCStats) de uma amostra de 12 lutas.

Atenção: resposta HTTP 200 NÃO valida os campos. Só se considera a ficha
verificável se a página contiver a tabela da luta (classe `b-fight-details__table`);
caso contrário (bloqueio/verificação de navegador) registra-se "bloqueio de acesso".
Execute da raiz:  python -m src.source_check   (requer internet)
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.request import Request, urlopen
import json

import pandas as pd

from .pipeline import ROOT


def check(row):
    """Consulta uma ficha e devolve o registro da tentativa (nunca declara validação de campos)."""
    record = dict(row, checked_at=datetime.now(timezone.utc).isoformat(), field_validation='pendente')
    try:
        req = Request(row['url'], headers={'User-Agent': 'Mozilla/5.0 (academic data verification)'})
        with urlopen(req, timeout=12) as response:
            body = response.read()
            (ROOT / 'outputs/source_pages').mkdir(exist_ok=True)
            (ROOT / f"outputs/source_pages/{row['bout_id']}.html").write_bytes(body)
            valid_page = b'b-fight-details__table' in body
            record.update(http_status=response.status,
                          access='disponível; conferir campos' if valid_page
                          else 'bloqueio de acesso; resposta sem tabela da luta')
    except Exception as e:  # rede indisponível, timeout etc.: registra e segue
        record.update(http_status=None, access='indisponível', error=str(e))
    return record


if __name__ == '__main__':
    sample = pd.read_csv(ROOT / 'data/processed/source_check_sample.csv').to_dict('records')
    with ThreadPoolExecutor(max_workers=4) as pool:  # 4 consultas simultâneas, sem sobrecarregar a fonte
        results = list(pool.map(check, sample))
    (ROOT / 'outputs/source_checks.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print([(r['bout_id'], r['access']) for r in results])
