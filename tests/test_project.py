"""Testes automatizados do projeto UFC BI & Analytics.

Quatro grupos:
    EdgeCases        - funções puras de limpeza e classificação (casos limites).
    Integration      - reconciliação entre CSVs, SQLite, KPIs e modelo.
    InferenceChecks  - intervalo de Wilson e integridade referencial dos CSVs.
    DatabaseSchema   - restrições PK/FK/CHECK do banco e consultas de sql/.

Execução (raiz do repositório):  python -m unittest discover -s tests -v
"""
import json
import sqlite3
import unittest

import pandas as pd

from src.analytics import FEATURES
from src.pipeline import ROOT, classify, kpis, outcome_winner, pair

DB = ROOT / 'data/processed/ufc.sqlite'


class EdgeCases(unittest.TestCase):
    """Casos limites das funções de transformação."""

    def test_pair_valid(self):
        self.assertEqual(pair('12 of 30'), (12, 30))

    def test_zero_is_valid(self):
        """'0 of 0' é um dado legítimo (nenhuma tentativa), diferente de ausência."""
        self.assertEqual(pair('0 of 0'), (0, 0))

    def test_missing_is_not_zero(self):
        with self.assertRaises(ValueError):
            pair('')

    def test_landed_cannot_exceed_attempted(self):
        with self.assertRaises(ValueError):
            pair('31 of 30')

    def test_negative_is_invalid(self):
        with self.assertRaises(ValueError):
            pair('-1 of 30')

    def test_outcome_orientation(self):
        """W/L: o primeiro nome do BOUT venceu; L/W: o segundo."""
        self.assertEqual(outcome_winner('A vs. B', 'W/L'), 'A')
        self.assertEqual(outcome_winner('A vs. B', 'L/W'), 'B')

    def test_tie_and_divergence(self):
        a = {'fighter': 'A', 'sig_landed': 10}
        b = {'fighter': 'B', 'sig_landed': 10}
        self.assertEqual(classify(a, b, 'A'), 'E')      # placares iguais => empate
        a['sig_landed'] = 11
        self.assertEqual(classify(a, b, 'B'), 'D')      # líder A perdeu
        self.assertEqual(classify(a, b, 'A'), 'C')      # líder A venceu

    def test_empty_filter(self):
        """Filtro sem lutas => KPI 'não calculável' (None), nunca 0%."""
        self.assertIsNone(kpis(pd.DataFrame({'status': []}))['concordance'])

    def test_only_ties(self):
        result = kpis(pd.DataFrame({'status': ['E', 'E']}))
        self.assertIsNone(result['concordance'])
        self.assertEqual(result['coverage'], 0)


class Integration(unittest.TestCase):
    """Reconciliação independente dos artefatos calculados."""

    @classmethod
    def setUpClass(cls):
        cls.b = pd.read_csv(ROOT / 'data/processed/bouts.csv')
        cls.r = pd.read_csv(ROOT / 'data/processed/rounds.csv')

    def test_grain(self):
        """Uma linha por luta; seis linhas (2 atletas x 3 rounds) por luta nos rounds."""
        self.assertFalse(self.b.bout_id.duplicated().any())
        self.assertFalse(self.r.duplicated(['bout_id', 'fighter', 'round']).any())
        self.assertTrue(self.r.groupby('bout_id').size().eq(6).all())

    def test_round_totals(self):
        """A soma dos rounds reproduz o total por atleta guardado em cada luta."""
        total = self.r.groupby(['bout_id', 'fighter']).sig_landed.sum()
        for x in self.b.itertuples():
            self.assertEqual(total.loc[x.bout_id, x.fighter_a], x.sig_a)
            self.assertEqual(total.loc[x.bout_id, x.fighter_b], x.sig_b)

    def test_count_reconciliation_all_filters(self):
        """C + D + E = N em todas as combinações de filtro do painel."""
        for year in [None, 2022, 2023, 2024]:
            for method in [None, 'Unânime', 'Dividida']:
                f = self.b.copy()
                if year:
                    f = f[f.year == year]
                if method:
                    f = f[f.method == method]
                k = kpis(f)
                self.assertEqual(k['C'] + k['D'] + k['E'], len(f))

    def test_sql_matches_python(self):
        """A visão SQL vw_bout_kpis coincide com o cálculo em Python."""
        with sqlite3.connect(DB) as c:
            s = pd.read_sql('SELECT * FROM vw_bout_kpis', c)
        for x in s.itertuples():
            k = kpis(self.b[(self.b.year == x.year) & (self.b.method == x.method)])
            self.assertAlmostEqual(k['concordance'], x.concordance_pct)

    def test_holland_example(self):
        row = self.b[self.b.bout_id == '697efaf0d162e877'].iloc[0]
        self.assertEqual(row.winner, 'Jack Della Maddalena')
        self.assertEqual(row.status, 'D')
        self.assertEqual({row.sig_a, row.sig_b}, {127, 105})

    def test_no_result_feature(self):
        """Nenhuma variável do modelo carrega o resultado (anti-vazamento)."""
        self.assertFalse(set(FEATURES) & {'winner', 'method', 'status', 'target', 'OUTCOME', 'DETAILS', 'date', 'year'})

    def test_test_set_is_temporal_and_unique(self):
        """O teste é só de 2024 e nenhuma luta dele aparece no treino."""
        p = pd.read_csv(ROOT / 'outputs/predictions_2024.csv')
        self.assertTrue(p.date.str.startswith('2024').all())
        self.assertFalse(p.bout_id.duplicated().any())
        train = self.b[self.b.year < 2024]
        self.assertFalse(set(train.bout_id) & set(p.bout_id))

    def test_model_matrix(self):
        """Acertos das previsões individuais = diagonal da matriz de confusão publicada."""
        p = pd.read_csv(ROOT / 'outputs/predictions_2024.csv')
        m = json.loads((ROOT / 'outputs/model_metrics.json').read_text())
        self.assertEqual(int((p.predicted == p.target).sum()),
                         sum(m['test_model']['confusion_matrix'][i][i] for i in [0, 1]))


class InferenceChecks(unittest.TestCase):
    """Inferência complementar e integridade referencial dos CSVs."""

    def test_wilson_matches_scipy(self):
        """Implementação própria de Wilson confere com a do SciPy (inclui extremos 0 e n)."""
        from scipy.stats import binomtest
        from src.inference import wilson
        for successes, total in [(0, 10), (10, 10), (514, 660)]:
            reference = binomtest(successes, total).proportion_ci(method='wilson')
            low, high = wilson(successes, total)
            self.assertAlmostEqual(low / 100, reference.low, places=5)
            self.assertAlmostEqual(high / 100, reference.high, places=5)

    def test_wilson_rejects_empty_denominator(self):
        from src.inference import wilson
        with self.assertRaises(ValueError):
            wilson(0, 0)

    def test_round_foreign_keys(self):
        """Todo round pertence a uma luta existente e aos dois atletas dela."""
        b = pd.read_csv(ROOT / 'data/processed/bouts.csv')
        r = pd.read_csv(ROOT / 'data/processed/rounds.csv')
        self.assertFalse(set(r.bout_id) - set(b.bout_id))
        for bout in b.itertuples():
            self.assertEqual(set(r[r.bout_id == bout.bout_id].fighter), {bout.fighter_a, bout.fighter_b})


class DatabaseSchema(unittest.TestCase):
    """O banco rejeita dados inválidos por si só (restrições declarativas)."""

    def setUp(self):
        self.conn = sqlite3.connect(DB)
        self.conn.execute('PRAGMA foreign_keys = ON')

    def tearDown(self):
        self.conn.close()

    def test_objects_exist(self):
        names = {r[0] for r in self.conn.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")}
        self.assertTrue({'dim_fighter', 'fact_bout', 'fact_round',
                         'vw_bout_kpis', 'vw_divergences', 'vw_round_detail'} <= names)

    def test_integrity_and_foreign_keys(self):
        self.assertEqual(self.conn.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        self.assertEqual(self.conn.execute('PRAGMA foreign_key_check').fetchall(), [])

    def test_row_counts_match_csv(self):
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM fact_bout').fetchone()[0], 665)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM fact_round').fetchone()[0], 665 * 6)

    def test_check_rejects_invalid_status(self):
        """CHECK impede status fora de C/D/E (transação desfeita ao final)."""
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("UPDATE fact_bout SET status = 'X' WHERE rowid = 1")
        self.conn.rollback()

    def test_foreign_key_rejects_orphan_round(self):
        """FK impede round sem luta correspondente."""
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("INSERT INTO fact_round VALUES ('inexistente', 1, 1, 5, 10, 0, 0, 0)")
        self.conn.rollback()

    def test_primary_key_rejects_duplicate_round(self):
        """A chave composta (luta, atleta, round) impede duplicidade."""
        row = self.conn.execute('SELECT * FROM fact_round LIMIT 1').fetchone()
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute('INSERT INTO fact_round VALUES (?,?,?,?,?,?,?,?)', row)
        self.conn.rollback()

    def test_reference_queries_run(self):
        """Todas as consultas de sql/consultas.sql executam e a auditoria Q7 retorna vazio."""
        sql = (ROOT / 'sql/consultas.sql').read_text(encoding='utf-8')
        statements = [s.strip() for s in sql.split(';') if 'SELECT' in s]
        self.assertEqual(len(statements), 7)
        for statement in statements:
            self.conn.execute(statement).fetchall()
        self.assertEqual(self.conn.execute(statements[-1]).fetchall(), [])


if __name__ == '__main__':
    unittest.main()
