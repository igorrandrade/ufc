"""Casos limites e reconciliação independente dos artefatos calculados."""
import json
import sqlite3
import unittest
import pandas as pd
from src.pipeline import ROOT,pair,outcome_winner,classify,kpis
from src.analytics import FEATURES

class EdgeCases(unittest.TestCase):
    def test_pair_valid(self):self.assertEqual(pair('12 of 30'),(12,30))
    def test_zero_is_valid(self):self.assertEqual(pair('0 of 0'),(0,0))
    def test_missing_is_not_zero(self):
        with self.assertRaises(ValueError):pair('')
    def test_landed_cannot_exceed_attempted(self):
        with self.assertRaises(ValueError):pair('31 of 30')
    def test_negative_is_invalid(self):
        with self.assertRaises(ValueError):pair('-1 of 30')
    def test_outcome_orientation(self):
        self.assertEqual(outcome_winner('A vs. B','W/L'),'A');self.assertEqual(outcome_winner('A vs. B','L/W'),'B')
    def test_tie_and_divergence(self):
        a={'fighter':'A','sig_landed':10};b={'fighter':'B','sig_landed':10}
        self.assertEqual(classify(a,b,'A'),'E');a['sig_landed']=11
        self.assertEqual(classify(a,b,'B'),'D');self.assertEqual(classify(a,b,'A'),'C')
    def test_empty_filter(self):self.assertIsNone(kpis(pd.DataFrame({'status':[]}))['concordance'])
    def test_only_ties(self):
        result=kpis(pd.DataFrame({'status':['E','E']}));self.assertIsNone(result['concordance']);self.assertEqual(result['coverage'],0)

class Integration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=pd.read_csv(ROOT/'data/processed/bouts.csv');cls.r=pd.read_csv(ROOT/'data/processed/rounds.csv')
    def test_grain(self):
        self.assertFalse(self.b.bout_id.duplicated().any());self.assertFalse(self.r.duplicated(['bout_id','fighter','round']).any())
        self.assertTrue(self.r.groupby('bout_id').size().eq(6).all())
    def test_round_totals(self):
        total=self.r.groupby(['bout_id','fighter']).sig_landed.sum()
        for x in self.b.itertuples():
            self.assertEqual(total.loc[x.bout_id,x.fighter_a],x.sig_a);self.assertEqual(total.loc[x.bout_id,x.fighter_b],x.sig_b)
    def test_count_reconciliation_all_filters(self):
        for year in [None,2022,2023,2024]:
            for method in [None,'Unânime','Dividida']:
                f=self.b.copy()
                if year:f=f[f.year==year]
                if method:f=f[f.method==method]
                k=kpis(f);self.assertEqual(k['C']+k['D']+k['E'],len(f))
    def test_sql_matches_python(self):
        with sqlite3.connect(ROOT/'data/processed/ufc.sqlite') as c:s=pd.read_sql('SELECT * FROM vw_bout_kpis',c)
        for x in s.itertuples():
            k=kpis(self.b[(self.b.year==x.year)&(self.b.method==x.method)])
            self.assertAlmostEqual(k['concordance'],x.concordance_pct)
    def test_holland_example(self):
        row=self.b[self.b.bout_id=='697efaf0d162e877'].iloc[0]
        self.assertEqual(row.winner,'Jack Della Maddalena');self.assertEqual(row.status,'D');self.assertEqual({row.sig_a,row.sig_b},{127,105})
    def test_no_result_feature(self):
        self.assertFalse(set(FEATURES)&{'winner','method','status','target','OUTCOME','DETAILS','date','year'})
    def test_test_set_is_temporal_and_unique(self):
        p=pd.read_csv(ROOT/'outputs/predictions_2024.csv');self.assertTrue(p.date.str.startswith('2024').all());self.assertFalse(p.bout_id.duplicated().any())
        train=self.b[self.b.year<2024];self.assertFalse(set(train.bout_id)&set(p.bout_id))
    def test_model_matrix(self):
        p=pd.read_csv(ROOT/'outputs/predictions_2024.csv');m=json.loads((ROOT/'outputs/model_metrics.json').read_text())
        self.assertEqual(int((p.predicted==p.target).sum()),sum(m['test_model']['confusion_matrix'][i][i] for i in [0,1]))

class InferenceChecks(unittest.TestCase):
    def test_wilson_matches_scipy(self):
        from scipy.stats import binomtest
        from src.inference import wilson
        for successes, total in [(0,10),(10,10),(514,660)]:
            reference=binomtest(successes,total).proportion_ci(method='wilson')
            low,high=wilson(successes,total)
            self.assertAlmostEqual(low/100,reference.low,places=5)
            self.assertAlmostEqual(high/100,reference.high,places=5)
    def test_wilson_rejects_empty_denominator(self):
        from src.inference import wilson
        with self.assertRaises(ValueError):wilson(0,0)
    def test_round_foreign_keys(self):
        b=pd.read_csv(ROOT/'data/processed/bouts.csv')
        r=pd.read_csv(ROOT/'data/processed/rounds.csv')
        self.assertFalse(set(r.bout_id)-set(b.bout_id))
        for bout in b.itertuples():
            self.assertEqual(set(r[r.bout_id==bout.bout_id].fighter),{bout.fighter_a,bout.fighter_b})

if __name__=='__main__':unittest.main()
