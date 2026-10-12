within;
package OxygenCoupled
  model Cell
    import U=FCSys.Units;
    parameter Real oxygenOrder(min=0)=1 "Zero: native control; one: diagnostic";
    final parameter FCSys.Quantities.PressureAbsolute pO2_ref=0.14603527167717584*U.atm;
    extends DCell.PaperTen(load(V=0.65),air_sccm=50,
      cell(caCL(subregions(graphite('e-Transfer'(qO2=
        {{{(cell.caCL.subregions[1,1,1].gas.O2.p/pO2_ref)^oxygenOrder},
          {(cell.caCL.subregions[1,2,1].gas.O2.p/pO2_ref)^oxygenOrder},
          {(cell.caCL.subregions[1,3,1].gas.O2.p/pO2_ref)^oxygenOrder},
          {(cell.caCL.subregions[1,4,1].gas.O2.p/pO2_ref)^oxygenOrder},
          {(cell.caCL.subregions[1,5,1].gas.O2.p/pO2_ref)^oxygenOrder},
          {(cell.caCL.subregions[1,6,1].gas.O2.p/pO2_ref)^oxygenOrder},
          {(cell.caCL.subregions[1,7,1].gas.O2.p/pO2_ref)^oxygenOrder},
          {(cell.caCL.subregions[1,8,1].gas.O2.p/pO2_ref)^oxygenOrder},
          {(cell.caCL.subregions[1,9,1].gas.O2.p/pO2_ref)^oxygenOrder},
          {(cell.caCL.subregions[1,10,1].gas.O2.p/pO2_ref)^oxygenOrder}}}))))));
  equation
    for j in 1:10 loop
      assert(cell.caCL.subregions[1,j,1].gas.O2.p>0,"Positive reaction-site oxygen required; no clamp");
    end for;
    annotation(experiment(StartTime=0,StopTime=180,Interval=0.36,Tolerance=1e-6));
  end Cell;
end OxygenCoupled;
