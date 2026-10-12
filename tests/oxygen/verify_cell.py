from pathlib import Path
import json,hashlib,sys
import numpy as np
from scipy.io import loadmat
ROOT=Path(__file__).resolve().parents[4];B=Path(__file__).resolve().parents[1];kind=sys.argv[1];assert kind in ['native0','native1']
W=B/'work/released-OxygenCoupled_Cell-translate';p=W/(kind+'.mat')
run=json.loads((B/'results'/(kind+'.json')).read_text());assert run['accepted']
def reader(path):
 m=loadmat(path,chars_as_strings=False);ix={''.join(x).rstrip():i for i,x in enumerate(m['name'].T)};t=m['data_2'][0]
 def get(n):
  ds,row=m['dataInfo'][:2,ix[n]];v=m[f'data_{ds}'][abs(row)-1]*np.sign(row)
  return v if ds==2 else np.full(len(t),v[-1])
 return m,t,get
m,t,s=reader(p);late=t>=144;gamma=0 if kind=='native0' else 1
et="graphite.'e-Transfer'."
def a(tail,layer='caCL'):return np.array([s(f'cell.{layer}.subregions[1,{j},1].'+tail) for j in range(1,11)])
uv=a(et+'E_A')[0,0]/.75;uk=s('environment.T')[0]/303.15;uatm=s('environment.p')[0];ua=s('anFlowSet.k')[0]/s('h2_equivalent_current_A')[0]
rawI=a(et+'I');I=-rawI/ua;T=a(et+'T');eta=-a(et+'Deltag')/uv;pO2=a('gas.O2.p')/uatm;q=a(et+'qO2')
expectedq=(pO2/.14603527167717584)**gamma
pred=-2*a(et+'I0')*expectedq*np.exp(-a(et+'E_A')*(1/T-1/(300*uk)))*np.sinh(a(et+'Deltag')/(2*T))/ua
contacts=np.array([-s(f'caAdapt[{j},1].pin.i') for j in range(1,11)])
an=np.array([s(f'anAdapt[{j},1].pin.i') for j in range(1,11)])
kcl=max(float(np.max(abs(an.sum(axis=0)-s('load.i')))),float(np.max(abs(contacts.sum(axis=0)-s('load.i')))))
cv=max([float(np.max(abs(s(f'caAdapt[{j},1].pin.v')-s('load.p.v')))) for j in range(1,11)]+[float(np.max(abs(s(f'anAdapt[{j},1].pin.v')-s('load.n.v')))) for j in range(1,11)])
chem=a('gas.O2.chemical[1].Ndot').sum(axis=0)
dn=sum(s(f'der(cell.{layer}.subregions[1,{j},1].gas.O2.N)') for layer in ['caFP','caGDL','caCL'] for j in range(1,11))
feed=-s('caSource[1,1].boundary.gas.O2.Ndot');sink=s('caSink[1,1].boundary.gas.O2.Ndot')
o2res=feed-sink+chem-.01*dn;o2rel=float(np.max(abs(o2res))/max(np.max(abs(feed)),1e-20))
components={'water':.5*a('gas.H2O.g')/uv,'proton':-a("ionomer.'H+'.g")/uv,'oxygen':-.25*a('gas.O2.g')/uv,'electron':-a("graphite.'e-'.g")/uv}
orr_res=float(np.max(abs(sum(components.values())-a(et+'Deltag')/uv)))
rate=float(np.max(abs(I[:,late]-pred[:,late])/np.maximum(abs(I[:,late]),1e-10)))
electron=float(np.max(abs(a(et+'positive.Ndot')+a(et+'negative.Ndot')))/ua)
energyraw=a(et+'Deltag')*rawI+a(et+'inert.Qdot');energy=float(np.max(abs(energyraw)/(uv*ua)))
stoich=float(np.max(abs(4*a('gas.O2.chemical[1].Ndot')[:,late]/rawI[:,late]-1)))
drift=float(np.max(abs(contacts[:,-1]-contacts[:,late][:,0])/np.maximum(abs(contacts[:,-1]),1e-30)))
endpoint=dict(reaction_current_A=I[:,-1].tolist(),contact_current_A=contacts[:,-1].tolist(),eta_V=eta[:,-1].tolist(),temperature_K=(T[:,-1]/uk).tolist(),pO2_CL_atm=pO2[:,-1].tolist(),pO2_channel_atm=(a('gas.O2.p','caFP')[:,-1]/uatm).tolist(),qO2=q[:,-1].tolist(),load_current_A=float(s('load.i')[-1]),oxygen_utilization=float((feed[-1]-sink[-1])/feed[-1]),chemical_potential_contributions_V={k:v[:,-1].tolist() for k,v in components.items()})
gates=dict(process=True,finite=bool(np.isfinite(m['data_2']).all()),horizon=abs(t[0])<1e-6 and abs(t[-1]-180)<1e-6 and bool(np.all(np.diff(t)>=0)),
  voltage=float(np.max(abs(s('load.v')-.65)))<=1e-8,air_sccm=bool(np.all(s('air_sccm')==50)),gamma=bool(np.all(s('oxygenOrder')==gamma)),
  environment=bool(abs(s('environment.T')[-1]/uk-303.15)<1e-8 and s('environment.RH')[-1]==1 and abs(s('environment.psi_O2_dry')[-1]-.20946)<1e-12),
  registered_feeds=bool(np.all(s('standard_T_K')==298.15) and np.all(s('standard_p_Pa')==100000) and np.all(s('anode_sccm')==25) and np.max(abs(s('anFlowSet.y')-s('h2_equivalent_current_A')*ua))<=1e-12 and np.max(abs(s('caFlowSet.y')-s('air_equivalent_current_A')*ua))<=1e-12),
  positive=bool((I[:,late]>0).all() and (contacts[:,late]>0).all() and (pO2>0).all()),
  qlaw=float(np.max(abs(q-expectedq)))<1e-8,rate=rate<1e-8,stoichiometry=stoich<1e-8,electron_balance=electron<1e-10,ET_energy=energy<1e-10,
  orr=orr_res<1e-8,kcl=kcl<=1e-7,contact_voltage=cv<=1e-8,oxygen=o2rel<=1e-7,settled=drift<=1e-4)
equivalence={}
if gamma==0:
 old=ROOT/'runs/fcsys-port/kulikovsky-fig8-stable-asinh-20260921T154441Z/work/released-DCell_PaperTen-translate/sweep-air50-V650.mat'
 pins=json.loads((ROOT/'outputs/science/paperten-kinetic-regime-map-20260929/mat-pins.json').read_text())
 pin=next(x for x in pins if x['path']==old.relative_to(ROOT).as_posix())
 assert hashlib.sha256(old.read_bytes()).hexdigest()==pin['sha256']
 _,_,getold=reader(old)
 for key,values,tail,scale in [('reaction_current_A',I[:,-1],et+'I',-ua),('eta_V',eta[:,-1],et+'Deltag',-uv),('temperature_K',T[:,-1]/uk,et+'T',uk),('pO2_CL_atm',pO2[:,-1],'gas.O2.p',uatm)]:
  ref=np.array([getold(f'cell.caCL.subregions[1,{j},1].'+tail)[-1]/scale for j in range(1,11)])
  ok=bool(np.all(abs(values-ref)<=np.maximum(1e-7,1e-4*abs(ref))))
  equivalence[key]=dict(pass_gate=ok,max_abs=float(np.max(abs(values-ref))),max_relative=float(np.max(abs(values/ref-1))))
 ref=np.array([-getold(f'caAdapt[{j},1].pin.i')[-1] for j in range(1,11)])
 values=contacts[:,-1]
 equivalence['contact_current_A']=dict(pass_gate=bool(np.all(abs(values-ref)<=np.maximum(1e-7,1e-4*abs(ref)))),max_abs=float(np.max(abs(values-ref))),max_relative=float(np.max(abs(values/ref-1))))
 gates['native_equivalence']=all(v['pass_gate'] for v in equivalence.values())
out=dict(status='PASS' if all(gates.values()) else 'FAIL',model='OxygenCoupled.Cell',gamma=gamma,mat_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),time_bounds_s=[float(t[0]),float(t[-1])],samples=len(t),gates=gates,endpoint=endpoint,
 residuals=dict(rate_relative=rate,oxygen_relative=o2rel,stoichiometry_relative=stoich,orr_V=orr_res,kcl_A=kcl,contact_voltage_V=cv,electron_A=electron,ET_energy_W=energy,contact_drift=drift),native_equivalence=equivalence)
(B/'results'/('cell-'+kind+'-verification.json')).write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2));raise SystemExit(out['status']!='PASS')
