"""Gera gráficos documentais e o dashboard interativo incorporável ao Colab."""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .pipeline import ROOT

def build():
    out=ROOT/'outputs';b=pd.read_csv(ROOT/'data/processed/bouts.csv');r=pd.read_csv(ROOT/'data/processed/rounds.csv');p=pd.read_csv(out/'predictions_2024.csv')
    k=json.loads((out/'kpis.json').read_text());m=json.loads((out/'model_metrics.json').read_text());q=json.loads((out/'quality.json').read_text())
    checks=json.loads((out/'source_checks.json').read_text()) if (out/'source_checks.json').exists() else []
    mapping={'__DATA__':b.to_json(orient='records',force_ascii=False),'__ROUNDS__':r.to_json(orient='records',force_ascii=False),
             '__PRED__':p.to_json(orient='records',force_ascii=False),'__METRICS__':json.dumps(m,ensure_ascii=False),
             '__QUALITY__':json.dumps(q,ensure_ascii=False),'__CHECKS__':json.dumps(checks,ensure_ascii=False)}
    page=(ROOT/'src/dashboard_template.html').read_text(encoding='utf-8')
    for key,value in mapping.items():page=page.replace(key,value.replace('</','<\\/'))
    (ROOT/'docs/index.html').write_text(page,encoding='utf-8')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','axes.labelcolor':'#122235','text.color':'#122235'})
    fig,ax=plt.subplots(figsize=(9.4,4.5));keys=['Unânime','Dividida'];v=[k['by_method'][x]['concordance'] for x in keys]
    ax.barh(keys[::-1],v[::-1],color=['#b63540','#216aa0'],height=.48);ax.set_xlim(0,100);ax.set_xlabel('Concordância (%) entre lutas sem empate em golpes');ax.set_title('A contagem acompanha mais as decisões unânimes',loc='left',pad=18)
    for i,key in enumerate(keys[::-1]):
        a=k['by_method'][key];ax.text(a['concordance']+1,i,f"{a['concordance']:.2f}%\n{a['C']}/{a['C']+a['D']}",va='center',fontsize=11)
    fig.tight_layout();fig.savefig(out/'concordance.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9.4,4.3));ys=[2022,2023,2024]
    for key,color in zip(keys,['#216aa0','#b63540']):
        v=[k['by_year_method'][f'{y} {key}']['concordance'] for y in ys]
        ax.plot(ys,v,'o-',label=key,color=color,linewidth=2.4)
        for x,y in zip(ys,v):ax.annotate(f'{y:.1f}%',(x,y),xytext=(0,9),textcoords='offset points',ha='center',fontsize=10)
    ax.set_ylim(0,100);ax.set_xticks(ys);ax.set_ylabel('Concordância (%)');ax.set_title('A diferença mantém a mesma direção nos três anos',loc='left',pad=18);ax.legend(loc='lower right');ax.grid(axis='y',alpha=.15);fig.tight_layout();fig.savefig(out/'years.png',dpi=180);plt.close(fig)
    g=r[r.bout_id=='697efaf0d162e877'];fig,ax=plt.subplots(figsize=(9.4,4.3));xx=np.arange(3)
    for i,(name,color) in enumerate([('Kevin Holland','#216aa0'),('Jack Della Maddalena','#b63540')]):
        d=g[g.fighter==name].sort_values('round');pos=xx+(i-.5)*.36;bars=ax.bar(pos,d.sig_landed,width=.34,label=name,color=color);ax.bar_label(bars,padding=3)
    ax.set_xticks(xx,['Round 1','Round 2','Round 3']);ax.set_ylim(0,60);ax.set_ylabel('Golpes significativos conectados');ax.set_title('Holland liderou 127 a 105; Della Maddalena venceu',loc='left',pad=18);ax.legend(loc='upper right',fontsize=9);fig.tight_layout();fig.savefig(out/'holland.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9.4,4.4));mat=np.array(m['test_model']['confusion_matrix']);ax.imshow(mat,cmap='Blues',vmin=0,vmax=198)
    for (i,j),v in np.ndenumerate(mat):ax.text(j,i,str(v),ha='center',va='center',fontsize=26,color='white' if v>100 else '#122235')
    ax.set_xticks([0,1],['Divergência','Concordância']);ax.set_yticks([0,1],['Divergência','Concordância']);ax.set_xlabel('Previsto');ax.set_ylabel('Observado');ax.set_title('25 das 49 divergências foram identificadas no teste',pad=18);fig.tight_layout();fig.savefig(out/'confusion.png',dpi=180);plt.close(fig)
    print('Dashboard e quatro gráficos gerados.');return page

if __name__=='__main__':build()
