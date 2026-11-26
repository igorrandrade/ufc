"""Integridade temporal da previsão mensal e reconciliação com as lutas."""
import json
import unittest
import numpy as np
import pandas as pd
from src.pipeline import ROOT
from src.forecast import FEATURES, feature_frame, monthly_series, scores

class ForecastChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=pd.read_csv(ROOT/'data/processed/bouts.csv')
        cls.m=monthly_series(cls.b)
        cls.p=pd.read_csv(ROOT/'outputs/forecast_2024.csv')

    def test_monthly_totals(self):
        self.assertEqual(int(self.m.C.sum()),514)
        self.assertEqual(int(self.m.n.sum()),660)

    def test_monthly_rates_use_classifiable_denominator(self):
        self.assertTrue(np.allclose(self.m.rate,self.m.C/self.m.n))

    def test_future_changes_do_not_change_past_features(self):
        changed=self.m.copy();changed.loc['2024-06':,'rate']=0.0
        a=feature_frame(self.m);b=feature_frame(changed)
        pd.testing.assert_frame_equal(a.loc[:'2024-06',FEATURES],b.loc[:'2024-06',FEATURES])

    def test_lag_excludes_target(self):
        f=feature_frame(self.m)
        for month,row in f.iterrows():
            self.assertEqual(row.lag_1,self.m.loc[month-1,'rate'])
            self.assertLess(pd.Timestamp(row.feature_cutoff),month.start_time)

    def test_test_period_and_training_cutoff(self):
        self.assertEqual(self.p.month.tolist(),[f'2024-{i:02d}' for i in range(1,13)])
        a=json.loads((ROOT/'outputs/forecast_model.json').read_text())
        self.assertEqual(a['training_last_month'],'2023-12')

    def test_metrics_and_probabilities(self):
        self.assertTrue(self.p.prediction.between(0,1).all())
        m=json.loads((ROOT/'outputs/forecast_metrics.json').read_text())
        self.assertAlmostEqual(scores(self.p.rate,self.p.prediction)['mae_pp'],m['model']['mae_pp'])

    def test_json_reproduces_predictions(self):
        a=json.loads((ROOT/'outputs/forecast_model.json').read_text())
        x=(self.p[FEATURES].to_numpy()-a['mean'])/a['scale']
        pred=np.clip(x@np.array(a['coef'])+a['intercept'],0,1)
        self.assertTrue(np.allclose(pred,self.p.prediction))

if __name__=='__main__':unittest.main()
