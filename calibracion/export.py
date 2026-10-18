import numpy as np, json, sys, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import calib as C
P=json.load(open(os.path.join(C.H,'params.json'))); p=[P[n] for n in C.NAMES]
def g14(m,s,p_=1):
    n=len(m); mb=m.mean(); return 100*(m-s).sum()/((n-p_)*mb), 100*np.sqrt(((m-s)**2).sum()/(n-p_))/mb
mon=C.e['month']; bim=(mon-1)//2
BIM=['Ene–Feb','Mar–Abr','May–Jun','Jul–Ago','Sep–Oct','Nov–Dic']
cal={}
for key,k,sp,role in [('22CLG-18HTG','c2218',(22,18),'entrenamiento'),('26clg18htg','c2618',(26,18),'validación'),('ideal','ideal',(24.4,21.7),'validación'),('custom','custom',None,'validación, horario')]:
    c=C.CASES[k]; clg,htg,TA=(C.forward(p,c,*sp) if sp else C.load_mode(p,c))
    m=np.array([c['clg'][bim==b].sum() for b in range(6)])/1000; s=np.array([clg[bim==b].sum() for b in range(6)])/1000
    mm=np.array([c['clg'][mon==b].sum() for b in range(1,13)])/1000; ss=np.array([clg[mon==b].sum() for b in range(1,13)])/1000
    nb,cb=g14(m,s); nm,cm=g14(mm,ss); nh,ch=g14(c['clg'],clg)
    cal[key]=dict(role=role,setpoints=sp,bimonthly=[dict(periodo=BIM[i],m=round(float(m[i])),s=round(float(s[i]))) for i in range(6)],
      annual_m=round(float(m.sum())),annual_s=round(float(s.sum())),
      NMBE_bim=round(nb,1),CV_bim=round(cb,1),NMBE_mon=round(nm,1),CV_mon=round(cm,1),NMBE_h=round(nh,1),CV_h=round(ch,1))
print(json.dumps(cal,ensure_ascii=False,indent=0)[:1500])
base=C.CASES['c2218']
gains=(P['f_ps']*base['ppl']+base['lit']+base['eqp']).round(0).astype(int).tolist()
elec=(base['lit']+base['eqp']).round(0).astype(int).tolist()
Tsky=C.Tsky
data=dict(station='Monterrey NLE MEX SRC-TMYx WMO 763930',lat=C.LAT,lon=C.LON,tz=C.TZ,
  To=[round(float(x),1) for x in C.To],Tsky=[round(float(x),1) for x in Tsky],GHI=[int(x) for x in C.GHI],
  DNI=[int(x) for x in C.e['DNI']],DHI=[int(x) for x in C.e['DHI']],month=[int(x) for x in mon],day=[int(x) for x in C.e['day']],
  gains=gains,elec=elec,params=P,shr=C.SHR,cal=cal,
  house=dict(zones='Cocina, estancia y recámara (63.2 m² acondicionados); baño sin equipo',volume=157.75))
s='const DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';'
open(os.path.join(C.H,'data.js'),'w').write(s); print('bytes',len(s))
# verify JS solar port later: export reference south irradiance first 48 daylight values
np.save(os.path.join(C.H,'IS_ref.npy'),C.IS)
