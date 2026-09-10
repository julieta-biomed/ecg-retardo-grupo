import numpy as np
from scipy import signal as sg

def ecg_hrv(fs=500, dur=120.0, hr=62.0, amp_r=1.30, hrv=0.045, semilla=7,
            modulacion=True):
    """ECG con HRV realista y modulacion respiratoria de amplitud/anchura.

    Devuelve (t, x, picos_verdaderos). La modulacion hace que la morfologia
    cambie ligeramente entre latidos, como ocurre de verdad.
    """
    rng=np.random.default_rng(semilla)
    n=int(fs*dur); t=np.arange(n)/fs; x=np.zeros(n)
    base=[(-0.200,0.15,0.025),(-0.035,-0.10,0.008),(0.0,1.10,0.010),
          (0.035,-0.25,0.010),(0.280,0.30,0.045)]
    rr_medio=60.0/hr; tr=0.5; picos=[]
    while tr < dur-0.6:
        picos.append(tr)
        if modulacion:
            ka = 1 + 0.06*np.sin(2*np.pi*0.25*tr)      # amplitud, respiratoria
            kw = 1 + 0.05*np.sin(2*np.pi*0.25*tr+1.2)  # anchura
        else:
            ka=kw=1.0
        for c,a,s in base:
            x += a*ka*np.exp(-0.5*((t-(tr+c))/(s*kw))**2)
        # HRV con componentes LF y HF, como una serie RR real
        rr = rr_medio + 0.030*np.sin(2*np.pi*0.10*tr) + 0.022*np.sin(2*np.pi*0.25*tr) \
             + rng.normal(0,0.012)
        tr += max(0.35, rr)
    return t, x*(amp_r/1.10), np.array(picos)

def metricas(picos):
    rr=np.diff(picos)*1000
    return dict(SDNN=rr.std(ddof=1), RMSSD=np.sqrt(np.mean(np.diff(rr)**2)),
                media=rr.mean())

if __name__=='__main__':
    t,x,p = ecg_hrv()
    m=metricas(p)
    print(f'{len(p)} latidos en {t[-1]:.0f} s')
    print(f'RR medio {m["media"]:.1f} ms  |  SDNN {m["SDNN"]:.2f} ms  |  RMSSD {m["RMSSD"]:.2f} ms')
    np.save('base.npy', np.array([t,x])); np.save('picos.npy', p)
