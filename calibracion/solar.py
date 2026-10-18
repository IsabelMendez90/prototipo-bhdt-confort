import numpy as np
def solar_vertical(month,day,hour,lat,lon,tz,GHI,DNI,DHI,rho=0.2):
    doy=np.array([sum([31,28,31,30,31,30,31,31,30,31,30,31][:m-1])+d for m,d in zip(month,day)])
    t=hour-0.5  # hour-ending -> mid-hour
    B=2*np.pi*(doy-81)/364; eot=9.87*np.sin(2*B)-7.53*np.cos(B)-1.5*np.sin(B)
    solar_t=t+(4*(lon-15*tz)+eot)/60
    ha=np.radians(15*(solar_t-12)); dec=np.radians(23.45*np.sin(2*np.pi*(284+doy)/365)); la=np.radians(lat)
    cz=np.sin(la)*np.sin(dec)+np.cos(la)*np.cos(dec)*np.cos(ha); cz=np.clip(cz,0,1)
    alt=np.arcsin(cz); 
    az=np.arctan2(np.sin(ha), np.cos(ha)*np.sin(la)-np.tan(dec)*np.cos(la))  # from south, west positive
    out=[]
    for faz in (np.pi, -np.pi/2, 0, np.pi/2):  # N,E,S,W (from south, west +)
        ci=np.cos(alt)*np.cos(az-faz); ci=np.clip(ci,0,None)
        out.append(DNI*ci*(cz>0)+0.5*DHI+0.5*rho*GHI)
    return np.stack(out), cz
