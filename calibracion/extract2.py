import sqlite3, numpy as np, os, sys
H=os.path.dirname(os.path.abspath(__file__))
PREF={'k':'KITCHEN_','l':'LIVING_ROOM_','r':'ROOM_1_','b':'BATHROOM_'}; AREA={'k':10.5,'l':42.2,'r':10.5}
def load(name):
    c=sqlite3.connect(os.path.join(H,name+'.sql')); c.text_factory=lambda b:b.decode('latin-1')
    dd=[(r[0],r[1],r[2]) for r in c.execute("select ReportDataDictionaryIndex,KeyValue,Name from ReportDataDictionary")]
    def S(var,z,suffix=''):
        idx=[i for i,k,n in dd if n==var and k.startswith(PREF[z]) and k.endswith(suffix)]
        if not idx: return np.zeros(8760)
        return np.array([v for (v,) in c.execute(f"select Value from ReportData where ReportDataDictionaryIndex={idx[0]} order by TimeIndex")])
    Z='klr'; out={}
    out['Ta']=sum(S('Zone Mean Air Temperature',z)*AREA[z] for z in Z)/sum(AREA.values())
    out['Tz']=np.stack([S('Zone Mean Air Temperature',z) for z in Z]); out['Tbath']=S('Zone Mean Air Temperature','b')
    out['clg']=sum(S('Zone Ideal Loads Zone Total Cooling Energy',z,'IDEAL LOADS AIR SYSTEM') for z in Z)/3600
    out['htg']=sum(S('Zone Ideal Loads Zone Total Heating Energy',z,'IDEAL LOADS AIR SYSTEM') for z in Z)/3600
    out['ppl']=sum(S('Zone People Total Heating Energy',z) for z in Z)/3600
    out['lit']=sum(S('Zone Lights Electricity Energy',z) for z in Z)/3600
    out['eqp']=sum(S('Zone Electric Equipment Electricity Energy',z) for z in Z)/3600
    out['sol']=sum(S('Enclosure Windows Total Transmitted Solar Radiation Energy',z) for z in Z)/3600
    out['vent']=(S('Zone Ventilation Sensible Heat Gain Energy','l')-S('Zone Ventilation Sensible Heat Loss Energy','l'))/3600
    return out
if __name__=='__main__':
    for n in ['c2218','c2618','custom','ideal']:
        o=load(n); np.savez(os.path.join(H,'case_'+n+'.npz'),**o)
        h=np.arange(8760)%24; d=np.arange(8760)//24; jul=(d>181)&(d<212); jan=d<31
        print(n,'clg MWh',round(o['clg'].sum()/1e6,2),'htg',round(o['htg'].sum()/1e6,2),'vent W',round(o['vent'].mean(),1),'Ta',round(o['Ta'].min(),1),round(o['Ta'].max(),1),'sol W',round(o['sol'].mean(),1))
        print('   Jul Ta',[round(o['Ta'][(h==x)&jul].mean(),1) for x in range(0,24,2)])
        print('   Jul clg',[round(o['clg'][(h==x)&jul].mean()) for x in range(0,24,2)])
