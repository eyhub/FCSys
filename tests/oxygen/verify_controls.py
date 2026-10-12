from pathlib import Path
import json,hashlib,sys,numpy as np
from scipy.io import loadmat
R=Path(__file__).resolve().parents[4];B=Path(__file__).resolve().parents[1];kind=sys.argv[1];scale={'scale05':.5,'scale1':1,'scale2':2}[kind];W=B/'work/released-OxygenControls_Matrix-translate';p=W/(kind+'.mat');assert json.loads((B/'results'/(kind+'.json')).read_text())['accepted']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def reader(p):
 m=loadmat(p,chars_as_strings=False);ix={''.join(x).rstrip():i for i,x in enumerate(m['name'].T)};t=m['data_2'][0]
 def s(n):
  ds,k=m['dataInfo'][:2,ix[n]];v=m[f'data_{ds}'][abs(k)-1]*np.sign(k);return v if ds==2 else np.full(len(t),v[-1])
 return m,t,s
m,t,s=reader(p);assert np.isfinite(m['data_2']).all() and abs(t[0])<1e-12 and abs(t[-1]-.1)<1e-12 and np.all(np.diff(t)>=0)
assert np.all(s('I0_scale')==scale);pressure=s('pO2_atm');pref=.14603527167717584;assert abs(pressure[0]-.026)<1e-12 and abs(pressure[-1]-.22)<1e-12
old=R/'runs/fcsys-port/oxygen-variable-binding-20260929T170713Z';ref=old/'attempts/local/work/released-OxygenLocal_Matrix-translate/native-algebraic.mat';pin=json.loads((old/'results/local-verification.json').read_text())['mat_sha256'];assert sha(ref)==pin
_,to,so=reader(ref);rows=[]
for arm in ['native','disabled','candidate']:
 for j,eta in enumerate([.45,.49,.53],1):
  v=lambda n:s(f'{arm}[{j}].'+n);current=v('current_A');uv=v('EA_set')[0]/.75;uk=v('T_set')[0]/303.78;vt=v('et.T')/uv;ua=-v('et.I')/current
  q=pressure/pref if arm=='candidate' else np.ones(len(t));pred=scale*.00000506*np.exp(.75*(1/(300*uk/uv)-1/vt))*q*2*np.sinh(eta/(2*vt))
  order=float(np.polyfit(np.log(pressure),np.log(current/(2*np.sinh(eta/(2*vt)))),1)[0]);parent=np.interp(t,to,so(f'{arm}[{j}].current_A'))
  errors=dict(rate=float(np.max(abs(current/pred-1))),q=float(np.max(abs(v('et.qO2')-q))),eta_V=float(np.max(abs(v('local_eta_V')-eta))),T_K=float(np.max(abs(v('temperature_K')-303.78))),oxygen=float(np.max(abs(4*v('oxygen_consumption_A')/current-1))),electron_A=float(np.max(abs(v('electron_balance_A')))),energy_W=float(np.max(abs(v('energy_residual_W')))),order=abs(order-(1 if arm=='candidate' else 0)),actual_I0_relative=float(np.max(abs(v('et.I0')/ua/(scale*.00000506)-1))),amplitude_scaling_relative=float(np.max(abs(current/(scale*parent)-1))))
  assert (current>0).all() and all(x<1e-8 for x in errors.values()),errors
  assert errors['electron_A']<1e-10 and errors['energy_W']<1e-10
  np.testing.assert_allclose(v('electron_eq_V')-v('electron_eq_V')[0],-vt/4*np.log(pressure/pressure[0]),atol=1e-10,rtol=0)
  if arm=='disabled':np.testing.assert_allclose(current,s(f'native[{j}].current_A'),rtol=1e-8,atol=1e-10)
  k=int(np.argmin(abs(pressure-pref)));assert abs(pressure[k]-pref)<1e-10
  if arm=='candidate':np.testing.assert_allclose(current[k],s(f'native[{j}].current_A')[k],rtol=1e-8,atol=1e-10)
  rows.append(dict(arm=arm,eta_V=eta,pressure_order=order,reference_current_A=float(current[k]),range_A=[float(current.min()),float(current.max())],errors=errors))
out=dict(status='PASS',scale=scale,time_bounds_s=[float(t[0]),float(t[-1])],samples=len(t),T_K=303.78,p_ref_atm=pref,pressure_bounds_atm=[float(pressure[0]),float(pressure[-1])],rows=rows,mat_sha256=sha(p),parent_mat_sha256=pin,limits=['Prescribed-reservoir actual-component test, not full-cell gas reconstruction','Amplitude sensitivity, not fitted or experimentally validated calibration'])
(B/'results'/(kind+'-verification.json')).write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status=out['status'],scale=scale,samples=len(t),orders=[r['pressure_order'] for r in rows],max_rate=max(r['errors']['rate'] for r in rows),max_scaling=max(r['errors']['amplitude_scaling_relative'] for r in rows)),indent=2))
