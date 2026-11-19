"""Coleta versionada, qualidade, modelo relacional e KPIs do UFC.

Execute da raiz: python -m src.pipeline. Nenhum dado sintético integra a análise.
"""
from pathlib import Path
import hashlib
import json
import re
import sqlite3
from urllib.request import urlopen
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
COMMIT = 'c742842f29466758fedc3906dbad28d6d320a8da'
HASHES = {
 'ufc_event_details.csv': '07355c6e414bb5932a7a0f97e4088388ff7391876b7a9ab792433c83f5285841',
 'ufc_fight_results.csv': 'b99d94a82984f07ec34d9f04423fd7edd67ea28c365621a144e05aec64f3a840',
 'ufc_fight_stats.csv': 'f5b316d5e745bd89da921b2c9711ec9209c2fa39dcbcd80bcb063b62d9175bcb'}

def collect():
    """Baixa somente arquivos ausentes e exige os hashes do snapshot da Fase 1."""
    raw = ROOT/'data/raw'; raw.mkdir(parents=True, exist_ok=True)
    manifest=[]
    for name, expected in HASHES.items():
        path=raw/name
        url=f'https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/{COMMIT}/{name}'
        if not path.exists():
            with urlopen(url, timeout=90) as response: payload=response.read()
            if hashlib.sha256(payload).hexdigest()!=expected: raise ValueError(f'Hash inesperado: {name}')
            path.write_bytes(payload)
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest!=expected: raise ValueError(f'Arquivo alterado: {name}')
        manifest.append(dict(file=name,bytes=path.stat().st_size,sha256=digest,url=url))
    (ROOT/'outputs').mkdir(exist_ok=True)
    (ROOT/'outputs/manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    return {n:pd.read_csv(raw/n,dtype=str,keep_default_na=False).apply(lambda c:c.str.strip()) for n in HASHES}

def pair(value):
    """Converte 'acertos of tentativas'; vazio nunca vira zero."""
    match=re.fullmatch(r'(\d+) of (\d+)',str(value))
    if not match: raise ValueError('par ausente ou malformado')
    landed,attempted=map(int,match.groups())
    if landed>attempted: raise ValueError('acertos acima das tentativas')
    return landed,attempted

def outcome_winner(bout,outcome):
    names=bout.split(' vs. ')
    if len(names)!=2 or outcome not in ['W/L','L/W']: raise ValueError('vencedor ambíguo')
    return names[0 if outcome=='W/L' else 1]

def classify(a,b,winner):
    if a['sig_landed']==b['sig_landed']: return 'E'
    leader=a if a['sig_landed']>b['sig_landed'] else b
    return 'C' if leader['fighter']==winner else 'D'

def kpis(frame):
    c=int((frame.status=='C').sum());d=int((frame.status=='D').sum());e=int((frame.status=='E').sum());n=c+d+e
    return dict(n=n,C=c,D=d,E=e,concordance=100*c/(c+d) if c+d else None,
                divergence=100*d/(c+d) if c+d else None,coverage=100*(c+d)/n if n else None,
                sensitivity_low=100*c/n if n else None,sensitivity_high=100*(c+e)/n if n else None)

def optional_int(value):
    try:
        x=float(value)
        return int(x) if x>=0 and x.is_integer() else np.nan
    except ValueError: return np.nan

def control_seconds(value):
    match=re.fullmatch(r'(\d+):([0-5]\d)',value)
    if not match:return np.nan
    m,s=map(int,match.groups());return 60*m+s if 60*m+s<=300 else np.nan

def build():
    tables=collect();ev=tables['ufc_event_details.csv'];res=tables['ufc_fight_results.csv'];st=tables['ufc_fight_stats.csv']
    audit={'raw_rows':{k:len(v) for k,v in tables.items()}}
    ev['date']=pd.to_datetime(ev.DATE,format='%B %d, %Y',errors='coerce')
    if ev.EVENT.duplicated().any(): raise ValueError('Evento ambíguo no catálogo')
    res=res.merge(ev[['EVENT','date','LOCATION']],on='EVENT',how='left',validate='many_to_one')
    audit['result_rows_without_date_before_alias']=int(res.date.isna().sum())
    # A URL concilia nomes alternativos. Uma URL não pode ter duas datas conhecidas.
    if res.groupby('URL').date.nunique().gt(1).any():raise ValueError('Datas conflitantes para a mesma URL')
    res['date']=res.groupby('URL').date.transform('max')
    audit['result_rows_without_date_after_alias']=int(res.date.isna().sum())
    p=ROOT/'data/processed';p.mkdir(exist_ok=True)
    res[res.date.isna()][['EVENT','BOUT','URL']].to_csv(p/'unresolved_dates.csv',index=False)
    in_period=res[res.date.dt.year.between(2022,2024)].copy()
    audit['bouts_in_period']=int(in_period.URL.nunique())
    mask=(in_period['TIME FORMAT']=='3 Rnd (5-5-5)')&(in_period.ROUND=='3')&(in_period.TIME=='5:00')&in_period.METHOD.isin(['Decision - Unanimous','Decision - Split'])&in_period.OUTCOME.isin(['W/L','L/W'])
    candidates=in_period[mask].copy();audit['eligible_result_rows']=len(candidates)
    # Consistência dos resultados duplicados antes de remover aliases.
    for col in ['BOUT','OUTCOME','METHOD','ROUND','TIME','TIME FORMAT','WEIGHTCLASS']:
        if candidates.groupby('URL')[col].nunique().gt(1).any():raise ValueError(f'Resultado conflitante: {col}')
    mapping=candidates[['EVENT','BOUT','URL']].drop_duplicates()
    if mapping.duplicated(['EVENT','BOUT']).any():raise ValueError('Chave textual ambígua no recorte')
    candidates=candidates.sort_values(['URL','EVENT']).drop_duplicates('URL')
    audit['eligible_bouts']=len(candidates)
    joined=st.merge(mapping,on=['EVENT','BOUT'],how='inner',validate='many_to_one')
    audit['round_rows_before_dedup']=len(joined)
    keys=['URL','FIGHTER','ROUND'];vals=[c for c in st.columns if c not in ['EVENT','BOUT']+keys]
    conflict=joined.groupby(keys)[vals].nunique().max(axis=1).gt(1)
    bad_urls=set(conflict[conflict].index.get_level_values(0))
    joined=joined.drop_duplicates(keys)
    audit['round_rows_after_dedup']=len(joined)
    groups={url:g for url,g in joined.groupby('URL')}
    exclusions=[];rounds=[];bouts=[]
    for _,r in candidates.iterrows():
        try:
            if r.URL in bad_urls:raise ValueError('duplicatas conflitantes')
            names=r.BOUT.split(' vs. ');g=groups.get(r.URL,pd.DataFrame())
            expected={(f,f'Round {i}') for f in names for i in (1,2,3)}
            if len(names)!=2 or len(g)!=6 or set(zip(g.FIGHTER,g.ROUND))!=expected:raise ValueError('grade de atletas/rounds incompleta')
            rr=[]
            for _,s in g.iterrows():
                landed,attempted=pair(s['SIG.STR.'])
                try:td,_=pair(s['TD'])
                except ValueError:td=np.nan
                rr.append(dict(bout_id=r.URL.rsplit('/',1)[-1],fighter=s.FIGHTER,round=int(s.ROUND[-1]),sig_landed=landed,sig_attempted=attempted,
                               td_landed=td,kd=optional_int(s.KD),control_seconds=control_seconds(s.CTRL)))
            total=pd.DataFrame(rr).groupby('fighter')[['sig_landed','sig_attempted','td_landed','kd','control_seconds']].agg(lambda x:x.sum(min_count=len(x)))
            totals=[dict(fighter=f,**total.loc[f].to_dict()) for f in names];winner=outcome_winner(r.BOUT,r.OUTCOME)
            status=classify(*totals,winner)
            a,b=sorted(totals,key=lambda x:(-x['sig_landed'],x['fighter']))
            ar=[x for x in rr if x['fighter']==a['fighter']];br=[x for x in rr if x['fighter']==b['fighter']]
            ar=sorted(ar,key=lambda x:x['round']);br=sorted(br,key=lambda x:x['round'])
            row=dict(bout_id=rr[0]['bout_id'],date=r.date.strftime('%Y-%m-%d'),year=int(r.date.year),event=r.EVENT,
                     method='Unânime' if r.METHOD.endswith('Unanimous') else 'Dividida',weightclass=r.WEIGHTCLASS,
                     fighter_a=names[0],fighter_b=names[1],winner=winner,status=status,
                     leader=a['fighter'] if status!='E' else '',other=b['fighter'] if status!='E' else '',
                     sig_a=int(totals[0]['sig_landed']),sig_b=int(totals[1]['sig_landed']),url=r.URL)
            row['sig_margin']=a['sig_landed']-b['sig_landed']
            row['attempt_margin']=a['sig_attempted']-b['sig_attempted']
            row['accuracy_margin']=(a['sig_landed']/a['sig_attempted'] if a['sig_attempted'] else np.nan)-(b['sig_landed']/b['sig_attempted'] if b['sig_attempted'] else np.nan)
            row['round_margin']=sum(int(x['sig_landed']>y['sig_landed'])-int(x['sig_landed']<y['sig_landed']) for x,y in zip(ar,br))
            for col in ['td_landed','kd','control_seconds']:row[col+'_margin']=a[col]-b[col]
            bouts.append(row);rounds.extend(rr)
        except (ValueError,AttributeError) as error: exclusions.append(dict(url=r.URL,reason=str(error)))
    b=pd.DataFrame(bouts).sort_values(['date','bout_id']).reset_index(drop=True);rd=pd.DataFrame(rounds)
    b.to_csv(p/'bouts.csv',index=False);rd.to_csv(p/'rounds.csv',index=False)
    pd.DataFrame(exclusions,columns=['url','reason']).to_csv(p/'exclusions.csv',index=False)
    audit.update(valid_bouts=len(b),excluded_bouts=len(exclusions),valid_round_rows=len(rd),optional_missing=rd.isna().sum().to_dict())
    summary={'all':kpis(b),'by_method':{str(m):kpis(g) for m,g in b.groupby('method')},'by_year':{str(y):kpis(g) for y,g in b.groupby('year')},
             'by_year_method':{f'{y} {m}':kpis(g) for (y,m),g in b.groupby(['year','method'])}}
    summary['H1_excess_pp']=summary['all']['concordance']-50
    summary['H2_difference_pp']=summary['by_method']['Unânime']['concordance']-summary['by_method']['Dividida']['concordance']
    for name,obj in [('quality',audit),('kpis',summary)]:
        (ROOT/f'outputs/{name}.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
    # Modelo normalizado: resultados por luta, dimensão atleta e estatísticas por atleta/round.
    db=p/'ufc.sqlite'
    if db.exists():db.unlink()
    with sqlite3.connect(db) as conn:
        conn.execute('PRAGMA foreign_keys=ON')
        names=sorted(set(rd.fighter));ath=pd.DataFrame({'fighter_id':range(1,len(names)+1),'fighter':names})
        ath.to_sql('dim_fighter',conn,index=False);conn.execute('CREATE UNIQUE INDEX ux_fighter ON dim_fighter(fighter_id)')
        b.to_sql('fact_bout',conn,index=False);conn.execute('CREATE UNIQUE INDEX ux_bout ON fact_bout(bout_id)')
        rd.merge(ath,on='fighter',validate='many_to_one').drop(columns='fighter').to_sql('fact_round',conn,index=False)
        conn.execute('CREATE UNIQUE INDEX ux_round ON fact_round(bout_id,fighter_id,round)')
        conn.execute('CREATE VIEW vw_bout_kpis AS SELECT year,method,COUNT(*) AS n,SUM(status="C") AS concordances,SUM(status="D") AS divergences,SUM(status="E") AS ties,100.0*SUM(status="C")/NULLIF(SUM(status IN ("C","D")),0) AS concordance_pct FROM fact_bout GROUP BY year,method')
        check=pd.read_sql('SELECT SUM(n) n FROM vw_bout_kpis',conn).iloc[0,0]
        assert int(check)==len(b)
    sample=b.groupby(['year','method'],group_keys=False).apply(lambda g:g.sort_values('url').head(2),include_groups=False).reset_index()
    sample[['bout_id','url']].to_csv(p/'source_check_sample.csv',index=False)
    print(json.dumps({'quality':audit,'kpis':summary},ensure_ascii=False,indent=2))
    return b,rd

if __name__=='__main__':build()
