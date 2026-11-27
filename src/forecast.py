"""Previsão mensal da concordância, feita antes de observar o mês previsto.

Complemento à classificação retrospectiva e às hipóteses descritivas do estudo.
Alvo: C/(C+D) no mês seguinte, para o mesmo recorte de decisões elegíveis.
Treino: 2022 (após aquecimento de três meses); validação: 2023; teste: 2024.
Cada previsão usa somente indicadores de meses encerrados. A avaliação de 2024
é móvel de um passo: o mês anterior já observado entra nas defasagens, mas os
coeficientes ficam congelados em 2022–2023. Não prevê o vencedor de uma luta.
"""
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from .pipeline import ROOT

FEATURES = ['lag_1', 'lag_2', 'lag_3']
ALPHAS = (0.1, 1.0, 10.0)

def monthly_series(bouts):
    b = bouts[bouts.status.isin(['C', 'D'])].copy()
    b['month'] = pd.to_datetime(b.date).dt.to_period('M')
    b['concordant'] = (b.status == 'C').astype(int)
    g = b.groupby('month').concordant.agg(['sum', 'count']).rename(columns={'sum':'C','count':'n'})
    g = g.reindex(pd.period_range(g.index.min(), g.index.max(), freq='M'))
    if g['n'].isna().any() or (g.n == 0).any():
        raise ValueError('Mês sem denominador: não imputar taxa mensal.')
    g['rate'] = g.C / g.n
    g.index.name = 'month'
    return g

def feature_frame(monthly):
    f = monthly.copy()
    for lag in range(1,4):
        f[f'lag_{lag}'] = f.rate.shift(lag)
    # A referência também só vê o passado, sem usar o denominador do mês-alvo.
    f['baseline'] = f.C.shift(1).expanding().sum() / f.n.shift(1).expanding().sum()
    f['feature_cutoff'] = [(p-1).end_time.strftime('%Y-%m-%d') for p in f.index]
    return f.dropna(subset=FEATURES+['baseline'])

def estimator(alpha):
    return make_pipeline(StandardScaler(), Ridge(alpha=alpha))

def scores(actual, predicted):
    return {'mae_pp': float(100*mean_absolute_error(actual,predicted)),
            'rmse_pp': float(100*np.sqrt(mean_squared_error(actual,predicted)))}

def run():
    monthly = monthly_series(pd.read_csv(ROOT/'data/processed/bouts.csv'))
    f = feature_frame(monthly)
    train, val, test = (f[f.index.year == y] for y in (2022,2023,2024))
    assert train.index.max() < val.index.min() < test.index.min()
    trials=[]
    for alpha in ALPHAS:
        m=estimator(alpha).fit(train[FEATURES],train.rate)
        p=np.clip(m.predict(val[FEATURES]),0,1)
        trials.append({'alpha':alpha,**scores(val.rate,p)})
    chosen=min(trials,key=lambda t:(t['mae_pp'],t['alpha']))['alpha']
    dev=pd.concat([train,val])
    model=estimator(chosen).fit(dev[FEATURES],dev.rate)
    pred=np.clip(model.predict(test[FEATURES]),0,1)
    out=test[['C','n','rate','feature_cutoff',*FEATURES,'baseline']].copy()
    out['prediction']=pred
    out['error_pp']=100*(out.prediction-out.rate)
    out.to_csv(ROOT/'outputs/forecast_2024.csv')
    monthly.to_csv(ROOT/'data/processed/monthly_concordance.csv')
    # Projeção de um passo na última origem do estudo. Não é previsão atual de 2026.
    final=estimator(chosen).fit(f[FEATURES],f.rate)
    next_x=pd.DataFrame([[monthly.rate.iloc[-i] for i in (1,2,3)]],columns=FEATURES)
    next_rate=float(np.clip(final.predict(next_x)[0],0,1))
    result={'task':'Prever C/(C+D) do mês seguinte antes de observar suas lutas.',
            'cohort':'Mesmo recorte descritivo: decisões unânimes/divididas de três rounds completos, UFC 2022–2024.',
            'features':FEATURES,'selected_alpha':chosen,'validation_trials':trials,
            'split':{'train_months':len(train),'validation_months':len(val),'final_train_months':len(dev),'test_months':len(test)},
            'model':scores(test.rate,pred),'baseline':scores(test.rate,test.baseline),
            'validation_baseline': scores(val.rate,val.baseline),
            'baseline_definition':'Concordância acumulada ponderada pelo número de lutas, apenas até o mês anterior.',
            'protocol':'Previsões de um mês à frente; coeficientes congelados até dezembro/2023 no teste de 2024. Meses anteriores de 2024 alimentam somente as defasagens e a baseline.',
            'next_period':{'origin':str(monthly.index.max()),'month':str(monthly.index.max()+1),'predicted_rate':next_rate,
                           'baseline_rate':float(monthly.C.sum()/monthly.n.sum()),
                           'status':'Projeção na origem histórica do estudo, sem avaliação contra janeiro/2025 e sem uso de dados após 2024.'},
            'limitations':'Apenas 36 meses, 12 no teste; denominadores variáveis e atletas repetidos. Sem intervalo de previsão calibrado. Não prevê vencedor individual nem demonstra causalidade. Uso exploratório para planejamento editorial.'}
    (ROOT/'outputs/forecast_metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    artifact={'features':FEATURES,'alpha':chosen,'training_last_month':str(dev.index.max()),
              'mean':model[0].mean_.tolist(),'scale':model[0].scale_.tolist(),
              'coef':model[1].coef_.tolist(),'intercept':float(model[1].intercept_)}
    (ROOT/'outputs/forecast_model.json').write_text(json.dumps(artifact,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result

if __name__=='__main__':
    run()
