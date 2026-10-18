import numpy as np, json, sys, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import calib as C
P=json.load(open(os.path.join(C.H,'params.json'))); p=[P[n] for n in C.NAMES]
mon=C.e['month']
def g14(m,s,p_=1):
    n=len(m); mb=m.mean(); return 100*(m-s).sum()/((n-p_)*mb), 100*np.sqrt(((m-s)**2).sum()/(n-p_))/mb
def agg(x,groups):
    return np.array([x[groups==g].sum() for g in np.unique(groups)])/1000  # kWh
bim=(mon-1)//2
SET={'c2218':(22,18),'c2618':(26,18),'ideal':(24.4,21.7)}
rows=[]
for k,c in C.CASES.items():
    for mode in ['load','forward']:
        if mode=='load': clg,htg,_=C.load_mode(p,c)
        else:
            if k not in SET: continue
            clg,htg,TA=C.forward(p,c,*SET[k])
        for var,mm,ss in [('clg',c['clg'],clg),('hvac',c['clg']+c['htg'],clg+htg)]:
            r={'case':k,'mode':mode,'var':var,'annual_E+_kWh':round(mm.sum()/1000),'annual_RC_kWh':round(ss.sum()/1000)}
            for lab,gr in [('bimonthly',bim),('monthly',mon)]:
                a,b=g14(agg(mm,gr),agg(ss,gr)); r[lab+'_NMBE']=round(a,1); r[lab+'_CV']=round(b,1)
            a,b=g14(mm,ss); r['hourly_NMBE']=round(a,1); r['hourly_CV']=round(b,1)
            rows.append(r)
import pandas as pd
df=pd.DataFrame(rows); pd.set_option('display.width',250); print(df.to_string(index=False))
df.to_csv(os.path.join(C.H,'g14_report.csv'),index=False)
