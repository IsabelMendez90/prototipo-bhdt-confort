"""Grey-box 2R2C surrogate calibrated against EnergyPlus ideal-loads results.
Inputs come only from the EPW plus the EnergyPlus internal-gain schedules."""
import numpy as np, json, sys, os
from scipy.optimize import least_squares
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from solar import solar_vertical
H=os.path.dirname(os.path.abspath(__file__))
e=np.load(os.path.join(H,'epw.npz'))
LAT,LON,TZ=25.6825,-100.2717,-6
I,cz=solar_vertical(e['month'],e['day'],e['hour'],LAT,LON,TZ,e['GHI'],e['DNI'],e['DHI'])
IS=I[2]; To=e['To']; GHI=e['GHI']
Tsky=(e['IR']/5.6697e-8)**0.25-273.15
def Wsat(T,P=95289.0):
    pv=611.2*np.exp(17.67*T/(T+243.5)); return 0.622*pv/(P-pv)
Wo=Wsat(e['Tdp'],e['P'])
CASES={k:dict(np.load(os.path.join(H,f'case_{k}.npz'))) for k in ['c2218','c2618','custom','ideal']}
base=CASES['c2218']; PPL=base['ppl']; LE=base['lit']+base['eqp']
SHR=0.7  # EnergyPlus IdealLoads default: ConstantSensibleHeatRatio 0.7
NAMES=['Ua','Um','Ham','Cm_MJ','Ca_MJ','a_s','a_r','g_s','f_sa','f_ca','f_ps','q0']
X0=[150,120,1500,15,1.5,0.03,0.3,1.85,0.4,0.6,0.6,200]
LB=[98,20,200,2,0.3,0,0,1.0,0,0.2,0.5,-500]
UB=[600,800,8000,80,8,0.1,1,2.8,1,1,0.8,1500]
def unpack(p):
    d=dict(zip(NAMES,p)); d['Cm']=d['Cm_MJ']*1e6; d['Ca']=d['Ca_MJ']*1e6; return d
def inputs(d,c):
    qs=d['g_s']*IS; qi=d['f_ps']*PPL+LE+d['q0']
    tsa=To+d['a_s']*GHI+d['a_r']*(Tsky-To)
    vent=c.get('vent',0) if c is not None else 0
    return qs,qi,tsa,vent
def load_mode(p,c):
    """Ta forced to EnergyPlus trajectory; returns modeled cooling and heating (W)."""
    d=unpack(p); qs,qi,tsa,vent=inputs(d,c); Ta=c['Ta']; dt=3600.0
    Tm=np.empty(8760); tm=Ta[0]+1
    for k in range(8760):
        rhs=d['Cm']*tm/dt+d['Um']*tsa[k]+d['Ham']*Ta[k]+(1-d['f_sa'])*qs[k]+(1-d['f_ca'])*qi[k]
        tm=rhs/(d['Cm']/dt+d['Um']+d['Ham']); Tm[k]=tm
    dTa=np.diff(Ta,prepend=Ta[-1])
    q=d['Ca']*dTa/dt-(d['Ua']*(To-Ta)+d['Ham']*(Tm-Ta)+d['f_sa']*qs+d['f_ca']*qi+vent)  # + = heating
    clg=np.maximum(0,-q)/SHR; htg=np.maximum(0,q)
    return clg,htg,Tm
def forward(p,c,tset_c,tset_h,sub=6):
    """Ideal-loads control with constant setpoints; vent from EnergyPlus as exogenous."""
    d=unpack(p); qs,qi,tsa,vent=inputs(d,c); dt=3600.0/sub
    ta,tm=21.0,22.0; clg=np.zeros(8760); htg=np.zeros(8760); TA=np.zeros(8760)
    if np.isscalar(vent): vent=np.zeros(8760)
    for k in range(8760):
        for s in range(sub):
            # implicit 2x2 with free air; then clamp
            a11=d['Ca']/dt+d['Ua']+d['Ham']; a12=-d['Ham']; a21=-d['Ham']; a22=d['Cm']/dt+d['Um']+d['Ham']
            b1=d['Ca']/dt*ta+d['Ua']*To[k]+d['f_sa']*qs[k]+d['f_ca']*qi[k]+vent[k]
            b2=d['Cm']/dt*tm+d['Um']*tsa[k]+(1-d['f_sa'])*qs[k]+(1-d['f_ca'])*qi[k]
            det=a11*a22-a12*a21; taf=(b1*a22-a12*b2)/det
            if taf>tset_c or taf<tset_h:
                tt=tset_c if taf>tset_c else tset_h
                tmn=(b2-a21*tt)/a22; q=a11*tt+a12*tmn-b1
                if q>0: htg[k]+=q/sub
                else: clg[k]+=(-q)/sub/SHR
                ta,tm=tt,tmn
            else:
                ta=taf; tm=(b2-a21*ta)/a22
        TA[k]=ta
    return clg,htg,TA
def resid(p):
    c=CASES['c2218']; clg,htg,_=load_mode(p,c)
    return np.r_[(clg-c['clg']),(htg-c['htg'])]/1000
if __name__=='__main__':
    r=least_squares(resid,X0,bounds=(LB,UB),x_scale='jac',max_nfev=400,verbose=0)
    P=dict(zip(NAMES,[float(x) for x in r.x])); print(json.dumps(P,indent=1)); print('cost',r.cost,r.status)
    json.dump(P,open(os.path.join(H,'params.json'),'w'),indent=1)
