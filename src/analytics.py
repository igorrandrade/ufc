"""Classificação retrospectiva do resultado de decisões, após três rounds.

Não é uma previsão pré-luta. O modelo usa indicadores do combate concluído,
mas nunca usa vencedor, método de decisão, votos ou placares como entrada.
Escolha de C em 2023. Teste final em 2024, sem ajuste após observá-lo.
"""
import json
import platform
from pathlib import Path
import numpy as np
import pandas as pd
import sklearn
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score,balanced_accuracy_score,roc_auc_score,log_loss,brier_score_loss,confusion_matrix,precision_score,recall_score,f1_score
from .pipeline import ROOT

FEATURES=['sig_margin','attempt_margin','accuracy_margin','round_margin','td_landed_margin','kd_margin','control_seconds_margin']

def metrics(y,p):
    predicted=(p>=0.5).astype(int)
    return dict(n=len(y),accuracy=float(accuracy_score(y,predicted)),balanced_accuracy=float(balanced_accuracy_score(y,predicted)),
                auc=float(roc_auc_score(y,p)),log_loss=float(log_loss(y,p,labels=[0,1])),brier=float(brier_score_loss(y,p)),
                precision_concordance=float(precision_score(y,predicted,zero_division=0)),recall_concordance=float(recall_score(y,predicted,zero_division=0)),
                f1_concordance=float(f1_score(y,predicted,zero_division=0)),recall_divergence=float(recall_score(y,predicted,pos_label=0,zero_division=0)),
                confusion_matrix=confusion_matrix(y,predicted,labels=[0,1]).tolist())

def estimator(c):
    return Pipeline([('imputer',SimpleImputer(strategy='median')),('scaler',StandardScaler()),
                     ('model',LogisticRegression(C=c,max_iter=3000,random_state=42))])

def run():
    b=pd.read_csv(ROOT/'data/processed/bouts.csv');b=b[b.status.isin(['C','D'])].copy()
    b['target']=(b.status=='C').astype(int)
    train=b[b.year==2022];val=b[b.year==2023];test=b[b.year==2024]
    assert train.date.max()<val.date.min()<test.date.min()
    trials=[]
    for c in (0.1,1.0,10.0):
        model=estimator(c).fit(train[FEATURES],train.target)
        trials.append({'C':c,**metrics(val.target,model.predict_proba(val[FEATURES])[:,1])})
    chosen=min(trials,key=lambda x:(x['log_loss'],x['C']))['C']
    dev=pd.concat([train,val]).sort_values('date')
    model=estimator(chosen).fit(dev[FEATURES],dev.target)
    probabilities=model.predict_proba(test[FEATURES])[:,1]
    baseline=np.full(len(test),dev.target.mean())
    result={'task':'Probabilidade de o líder único em golpes significativos vencer a decisão, dados os três rounds completos.',
            'prediction_time':'Após os três rounds; avaliação retrospectiva em decisões unânimes/divididas. Não é previsão pré-luta nem serviço ao vivo.',
            'target':'1 = concordância; 0 = divergência','features':FEATURES,'validation':trials,'selected_C':chosen,
            'split':{'train_2022':len(train),'validation_2023':len(val),'final_train_2022_2023':len(dev),'test_2024':len(test)},
            'test_model':metrics(test.target,probabilities),'test_baseline':metrics(test.target,baseline),
            'baseline_probability':float(dev.target.mean()),'environment':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'sklearn':sklearn.__version__}}
    pred=test[['bout_id','date','method','leader','other','winner','status','target']].copy()
    pred['probability']=probabilities;pred['predicted']=(probabilities>=0.5).astype(int);pred['baseline_probability']=baseline
    pred.to_csv(ROOT/'outputs/predictions_2024.csv',index=False)
    result['test_by_method']={str(m):metrics(g.target,g.probability.to_numpy()) for m,g in pred.groupby('method')}
    (ROOT/'outputs/model_metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    # JSON transparente evita desserialização de pickle. Permite reproduzir inferências.
    artifact={'features':FEATURES,'imputer':model['imputer'].statistics_.tolist(),'mean':model['scaler'].mean_.tolist(),
              'scale':model['scaler'].scale_.tolist(),'coef':model['model'].coef_[0].tolist(),'intercept':float(model['model'].intercept_[0]),
              'training_last_date':dev.date.max(),'C':chosen}
    (ROOT/'outputs/model.json').write_text(json.dumps(artifact,indent=2),encoding='utf-8')
    logits=((test[FEATURES].fillna(dict(zip(FEATURES,artifact['imputer'])))-artifact['mean'])/artifact['scale']).to_numpy()@np.array(artifact['coef'])+artifact['intercept']
    assert np.allclose(1/(1+np.exp(-logits)),probabilities)
    print(json.dumps(result,ensure_ascii=False,indent=2));return result

if __name__=='__main__':run()
