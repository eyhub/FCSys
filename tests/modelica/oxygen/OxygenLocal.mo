within;
package OxygenLocal
  import U = FCSys.Units;
  import Q = FCSys.Quantities;

  model Reservoir
    input Q.Potential g_set;
    FCSys.Connectors.Chemical chemical(n_trans=1);
  equation
    chemical.g = g_set;
    chemical.phi = {0};
    chemical.sT = 0;
  end Reservoir;

  model Bath
    parameter Q.TemperatureAbsolute T_set=303.78*U.K;
    FCSys.Connectors.Inert inert(n_trans=1);
  equation
    inert.T = T_set;
    inert.phi = {0};
  end Bath;

  partial model SiteCore
    parameter Real eta_V=0.2;
    parameter Q.TemperatureAbsolute T_set=303.78*U.K;
    parameter Q.Current I0_set=0.00506*U.mA;
    parameter Q.Potential EA_set=0.75*U.V;
    input Real pO2_atm;
    package OxygenData = FCSys.Characteristics.O2.Gas(b_v=[1],n_v={-1,0});
    package WaterData = FCSys.Characteristics.H2O.Gas(b_v=[1],n_v={-1,0});
    parameter Q.Potential gH=0;
    parameter Q.Potential gW=WaterData.g(T_set,0.122*U.atm);
    Q.Potential gO=OxygenData.g(T_set,pO2_atm*U.atm);
    Q.Potential gElectronEq=0.5*gW-gH-0.25*gO;
    Reservoir oxygen(g_set=gO);
    Reservoir water(g_set=gW);
    Reservoir proton(g_set=gH);
    Reservoir bulkElectron(g_set=gElectronEq+eta_V*U.V);
    Bath bath(T_set=T_set);
    FCSys.Chemistry.ORR orr(n_trans=1);
    output Real electron_eq_V=gElectronEq/U.V;
    output Real oxygen_consumption_A=orr.chemO2.Ndot/U.A;
  equation
    assert(pO2_atm>0,"Positive oxygen required");
    connect(oxygen.chemical,orr.chemO2);
    connect(water.chemical,orr.chemH2O);
    connect(proton.chemical,orr.'chemH+');
  end SiteCore;

  model NativeSite
    extends SiteCore;
    FCSys.Chemistry.Electrochemistry.ElectronTransfer et(
      n_trans=1,fromI=true,I0=I0_set,E_A=EA_set,alpha=0.5);
    output Real current_A=-et.I/U.A;
    output Real local_eta_V=-et.Deltag/U.V;
    output Real temperature_K=et.T/U.K;
    output Real heat_W=et.inert.Qdot/U.W;
    output Real electron_balance_A=(et.positive.Ndot+et.negative.Ndot)/U.A;
    output Real energy_residual_W=(et.Deltag*et.I+et.inert.Qdot)/U.W;
  equation
    connect(et.positive,orr.'cheme-');
    connect(et.negative,bulkElectron.chemical);
    connect(et.inert,bath.inert);
  end NativeSite;

  model CandidateSite
    parameter Real gamma=1;
    final parameter Q.PressureAbsolute pO2_ref=0.14603527167717584*U.atm;
    extends SiteCore;
    FCSys.Chemistry.Electrochemistry.ElectronTransfer et(
      n_trans=1,fromI=true,I0=I0_set,E_A=EA_set,alpha=0.5,
      qO2=(pO2_atm*U.atm/pO2_ref)^gamma);
    output Real current_A=-et.I/U.A;
    output Real local_eta_V=-et.Deltag/U.V;
    output Real temperature_K=et.T/U.K;
    output Real heat_W=et.inert.Qdot/U.W;
    output Real electron_balance_A=(et.positive.Ndot+et.negative.Ndot)/U.A;
    output Real energy_residual_W=(et.Deltag*et.I+et.inert.Qdot)/U.W;
  equation
    connect(et.positive,orr.'cheme-');
    connect(et.negative,bulkElectron.chemical);
    connect(et.inert,bath.inert);
  end CandidateSite;

  model Matrix
    inner FCSys.Conditions.Environment environment(T=303.78*U.K,analysis=false);
    parameter Real pressure_atm[5]={0.026,0.11074759273907943,0.14603527167717584,0.20027847961304046,0.22};
    parameter Real eta_V[3]={0.45,0.49,0.53};
    Real pO2_atm;
    NativeSite native[3](eta_V=eta_V,each pO2_atm=pO2_atm);
    CandidateSite disabled[3](eta_V=eta_V,each pO2_atm=pO2_atm,each gamma=0);
    CandidateSite candidate[3](eta_V=eta_V,each pO2_atm=pO2_atm,each gamma=1);
  equation
    pO2_atm=if time<0.025 then pressure_atm[1]+(pressure_atm[2]-pressure_atm[1])*time/0.025
      elseif time<0.05 then pressure_atm[2]+(pressure_atm[3]-pressure_atm[2])*(time-0.025)/0.025
      elseif time<0.075 then pressure_atm[3]+(pressure_atm[4]-pressure_atm[3])*(time-0.05)/0.025
      else pressure_atm[4]+(pressure_atm[5]-pressure_atm[4])*(time-0.075)/0.025;
    annotation(experiment(StartTime=0,StopTime=0.1,Interval=0.0002,Tolerance=1e-8));
  end Matrix;
end OxygenLocal;
