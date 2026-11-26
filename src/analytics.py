"""Analytics: classificação retrospectiva do resultado de decisões, após três rounds.

Pergunta: dado o desempenho nos três rounds, qual a probabilidade de o líder
em golpes significativos ser o vencedor oficial?

Esta NÃO é uma previsão pré-luta. O modelo usa estatísticas do combate já
concluído e nunca usa vencedor, método da decisão, votos ou placares como entrada.

Protocolo de validação (temporal, sem vazamento de dados):
    treino 2022  ->  escolha de C em 2023 (menor log loss)  ->  reajuste em 2022-23  ->  teste em 2024.
O conjunto de 2024 só é avaliado depois de fixados todos os hiperparâmetros.

Execute da raiz:  python -m src.analytics
"""
import json
import platform

import numpy as np
import pandas as pd
import sklearn
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, brier_score_loss, confusion_matrix,
                             f1_score, log_loss, precision_score, recall_score, roc_auc_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .pipeline import ROOT

# Sete diferenças "líder menos adversário" calculadas em pipeline.build_bout_rows().
FEATURES = ['sig_margin', 'attempt_margin', 'accuracy_margin', 'round_margin',
            'td_landed_margin', 'kd_margin', 'control_seconds_margin']

# Grade de regularização testada (C menor = regularização mais forte).
C_GRID = (0.1, 1.0, 10.0)
THRESHOLD = 0.5  # limiar de classificação, fixado a priori


def metrics(y, p):
    """Métricas de classificação binária a partir do alvo `y` e das probabilidades `p`.

    Alvo 1 = concordância; alvo 0 = divergência. Inclui métricas de probabilidade
    (AUC, log loss, Brier) e a matriz de confusão [[VN, FP], [FN, VP]].
    """
    predicted = (p >= THRESHOLD).astype(int)
    return dict(n=len(y),
                accuracy=float(accuracy_score(y, predicted)),
                balanced_accuracy=float(balanced_accuracy_score(y, predicted)),
                auc=float(roc_auc_score(y, p)),
                log_loss=float(log_loss(y, p, labels=[0, 1])),
                brier=float(brier_score_loss(y, p)),
                precision_concordance=float(precision_score(y, predicted, zero_division=0)),
                recall_concordance=float(recall_score(y, predicted, zero_division=0)),
                f1_concordance=float(f1_score(y, predicted, zero_division=0)),
                recall_divergence=float(recall_score(y, predicted, pos_label=0, zero_division=0)),
                confusion_matrix=confusion_matrix(y, predicted, labels=[0, 1]).tolist())


def estimator(c):
    """Pipeline do scikit-learn: imputação pela mediana -> padronização -> regressão logística.

    As transformações são ajustadas apenas nos dados de treino (sem vazamento).
    """
    return Pipeline([('imputer', SimpleImputer(strategy='median')),
                     ('scaler', StandardScaler()),
                     ('model', LogisticRegression(C=c, max_iter=3000, random_state=42))])


def run():
    """Treina, seleciona, testa e exporta métricas, previsões e parâmetros do modelo."""
    b = pd.read_csv(ROOT / 'data/processed/bouts.csv')
    b = b[b.status.isin(['C', 'D'])].copy()          # empates não têm líder: fora só da classificação
    b['target'] = (b.status == 'C').astype(int)

    # Divisão temporal por ano; a asserção impede sobreposição de datas entre as partes.
    train, val, test = b[b.year == 2022], b[b.year == 2023], b[b.year == 2024]
    assert train.date.max() < val.date.min() < test.date.min()

    # 1) Seleção de hiperparâmetro em 2023 (critério: menor log loss; empate -> menor C).
    trials = []
    for c in C_GRID:
        model = estimator(c).fit(train[FEATURES], train.target)
        trials.append({'C': c, **metrics(val.target, model.predict_proba(val[FEATURES])[:, 1])})
    chosen = min(trials, key=lambda x: (x['log_loss'], x['C']))['C']

    # 2) Reajuste em 2022-2023 e avaliação única em 2024.
    dev = pd.concat([train, val]).sort_values('date')
    model = estimator(chosen).fit(dev[FEATURES], dev.target)
    probabilities = model.predict_proba(test[FEATURES])[:, 1]

    # Baseline: probabilidade constante = taxa de concordância do treino final (76,51%).
    baseline = np.full(len(test), dev.target.mean())

    result = {
        'task': 'Probabilidade de o líder único em golpes significativos vencer a decisão, dados os três rounds completos.',
        'prediction_time': 'Após os três rounds; avaliação retrospectiva em decisões unânimes/divididas. Não é previsão pré-luta nem serviço ao vivo.',
        'target': '1 = concordância; 0 = divergência', 'features': FEATURES, 'validation': trials, 'selected_C': chosen,
        'split': {'train_2022': len(train), 'validation_2023': len(val),
                  'final_train_2022_2023': len(dev), 'test_2024': len(test)},
        'test_model': metrics(test.target, probabilities), 'test_baseline': metrics(test.target, baseline),
        'baseline_probability': float(dev.target.mean()),
        'environment': {'python': platform.python_version(), 'numpy': np.__version__,
                        'pandas': pd.__version__, 'sklearn': sklearn.__version__}}

    # Previsões individuais (auditáveis) e desempenho por tipo de decisão.
    pred = test[['bout_id', 'date', 'method', 'leader', 'other', 'winner', 'status', 'target']].copy()
    pred['probability'] = probabilities
    pred['predicted'] = (probabilities >= THRESHOLD).astype(int)
    pred['baseline_probability'] = baseline
    pred.to_csv(ROOT / 'outputs/predictions_2024.csv', index=False)
    result['test_by_method'] = {str(m): metrics(g.target, g.probability.to_numpy()) for m, g in pred.groupby('method')}
    (ROOT / 'outputs/model_metrics.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

    # Parâmetros em JSON transparente (evita desserialização de pickle) e permitem
    # reproduzir a inferência manualmente: logit = coef . ((x - mean) / scale) + intercept.
    artifact = {'features': FEATURES, 'imputer': model['imputer'].statistics_.tolist(),
                'mean': model['scaler'].mean_.tolist(), 'scale': model['scaler'].scale_.tolist(),
                'coef': model['model'].coef_[0].tolist(), 'intercept': float(model['model'].intercept_[0]),
                'training_last_date': dev.date.max(), 'C': chosen}
    (ROOT / 'outputs/model.json').write_text(json.dumps(artifact, indent=2), encoding='utf-8')

    # Verificação cruzada: o JSON reproduz exatamente as probabilidades do scikit-learn.
    x = ((test[FEATURES].fillna(dict(zip(FEATURES, artifact['imputer']))) - artifact['mean']) / artifact['scale']).to_numpy()
    logits = x @ np.array(artifact['coef']) + artifact['intercept']
    assert np.allclose(1 / (1 + np.exp(-logits)), probabilities)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == '__main__':
    run()
