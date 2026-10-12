within;
package DCell
  model Two
    extends FCSys.Assemblies.Cells.Examples.KulikovskyDistributed.TestStandDistributedFixedFlowSegmented(
      cell(anGDL(subregions(each graphite('e-'(useXNegativeAfterShearClosure=true)))),
        caGDL(subregions(each graphite('e-'(useXPositiveAfterShearClosure=true)))),
        anFP(subregions(graphite('e-'(useYNegativeBeforeShearClosure={{{if j == 1 then false else true for k in 1:1} for j in 1:n_y} for i in 1:1}, normalizeYPositiveBeforeShearForce={{{if j < n_y then true else false for k in 1:1} for j in 1:n_y} for i in 1:1})))),
        caFP(subregions(graphite('e-'(useYNegativeBeforeShearClosure={{{if j == 1 then false else true for k in 1:1} for j in 1:n_y} for i in 1:1}, normalizeYPositiveBeforeShearForce={{{if j < n_y then true else false for k in 1:1} for j in 1:n_y} for i in 1:1}))))));

    initial equation
      for j in 1:n_y loop
        assert(cell.anGDL.subregions[1,j,1].inclTransX and not cell.anGDL.subregions[1,j,1].inclTransY and not cell.anGDL.subregions[1,j,1].inclTransZ,
          "distributed shear closure requires GDL x-only transport");
        assert(cell.anFP.subregions[1,j,1].inclTransX and cell.anFP.subregions[1,j,1].inclTransY and not cell.anFP.subregions[1,j,1].inclTransZ,
          "distributed shear closure requires FP x-y transport");
        assert(cell.anGDL.subregions[1,j,1].graphite.'e-'.n_trans == 1,
          "distributed shear closure requires one GDL transport axis");
        assert(cell.anFP.subregions[1,j,1].graphite.'e-'.n_trans == 2,
          "distributed shear closure requires two FP transport axes");
        assert(cell.anGDL.subregions[1,j,1].graphite.'e-'.consRot == false,
          "distributed shear closure requires direct GDL force mapping");
        assert(cell.anFP.subregions[1,j,1].graphite.'e-'.consRot == false,
          "distributed shear closure requires direct FP force mapping");
        assert(cell.anGDL.subregions[1,j,1].graphite.'e-'.upstreamX == false,
          "distributed shear closure requires non-upstream GDL x transport");
        assert(cell.anFP.subregions[1,j,1].graphite.'e-'.upstreamX == false,
          "distributed shear closure requires non-upstream FP x transport");
        assert(cell.anGDL.subregions[1,j,1].graphite.'e-'.Nu_Phi[FCSys.Species.Enumerations.Axis.y] == 4,
          "distributed shear closure requires Nu_Phi y=4 in GDL");
        assert(cell.anFP.subregions[1,j,1].graphite.'e-'.Nu_Phi[FCSys.Species.Enumerations.Axis.y] == 4,
          "distributed shear closure requires Nu_Phi y=4 in FP");
        assert((cell.anGDL.subregions[1,j,1].graphite.V / cell.anGDL.subregions[1,j,1].L[FCSys.Species.Enumerations.Axis.x]) > 0,
          "distributed shear closure requires positive GDL area");
        assert((cell.anFP.subregions[1,j,1].graphite.V / cell.anFP.subregions[1,j,1].L[FCSys.Species.Enumerations.Axis.x]) > 0,
          "distributed shear closure requires positive FP area");
        assert(cell.anGDL.subregions[1,j,1].graphite.'e-'.kL[1] > 0,
          "distributed shear closure requires positive GDL kL");
        assert(cell.anFP.subregions[1,j,1].graphite.'e-'.kL[1] > 0,
          "distributed shear closure requires positive FP kL");
        assert(cell.anGDL.subregions[1,j,1].graphite.'e-'.eta > 0 and
          cell.anGDL.subregions[1,j,1].graphite.'e-'.eta == cell.anFP.subregions[1,j,1].graphite.'e-'.eta,
          "distributed shear closure requires equal positive fluidity");
        assert(cell.anFP.subregions[1,j,1].graphite.'e-'.kL[1] == cell.anFP.subregions[1,j,1].graphite.'e-'.kL[2],
          "distributed shear closure requires equal FP kL");
      end for;

      assert(n_y >= 2, "shear family diagnostic requires at least two sections");
      for j in 1:n_y loop
        assert(cell.caGDL.subregions[1,j,1].graphite.'e-'.n_trans == 1, "shear family caGDL axis count");
        assert(cell.caGDL.subregions[1,j,1].inclTransX and not cell.caGDL.subregions[1,j,1].inclTransY and not cell.caGDL.subregions[1,j,1].inclTransZ, "shear family caGDL axis set");
        assert(not cell.caGDL.subregions[1,j,1].graphite.'e-'.consRot and not cell.caGDL.subregions[1,j,1].graphite.'e-'.upstreamX, "shear family caGDL direct non-upstream x law");
        assert(cell.caGDL.subregions[1,j,1].graphite.'e-'.Nu_Phi[FCSys.Species.Enumerations.Axis.y] == 4, "shear family caGDL y factor");
        assert(cell.caGDL.subregions[1,j,1].graphite.'e-'.kL[1] > 0 and (cell.caGDL.subregions[1,j,1].graphite.V / cell.caGDL.subregions[1,j,1].L[FCSys.Species.Enumerations.Axis.x]) > 0, "shear family caGDL positive geometry");
        assert(cell.caFP.subregions[1,j,1].graphite.'e-'.n_trans == 2, "shear family caFP axis count");
        assert(cell.caFP.subregions[1,j,1].inclTransX and cell.caFP.subregions[1,j,1].inclTransY and not cell.caFP.subregions[1,j,1].inclTransZ, "shear family caFP axis set");
        assert(not cell.caFP.subregions[1,j,1].graphite.'e-'.consRot and not cell.caFP.subregions[1,j,1].graphite.'e-'.upstreamX, "shear family caFP direct non-upstream x law");
        assert(cell.caFP.subregions[1,j,1].graphite.'e-'.Nu_Phi[FCSys.Species.Enumerations.Axis.y] == 4, "shear family caFP y factor");
        assert(cell.caFP.subregions[1,j,1].graphite.'e-'.kL[1] > 0 and (cell.caFP.subregions[1,j,1].graphite.V / cell.caFP.subregions[1,j,1].L[FCSys.Species.Enumerations.Axis.x]) > 0, "shear family caFP positive geometry");
        assert(cell.caFP.subregions[1,j,1].graphite.'e-'.kL[1] == cell.caFP.subregions[1,j,1].graphite.'e-'.kL[2], "shear family caFP fixed kL");
        assert(cell.caGDL.subregions[1,j,1].graphite.'e-'.eta > 0 and cell.caGDL.subregions[1,j,1].graphite.'e-'.eta == cell.caFP.subregions[1,j,1].graphite.'e-'.eta, "shear family cathode equal eta");
        assert(not cell.anFP.subregions[1,j,1].graphite.'e-'.upstreamY and not cell.anFP.subregions[1,j,1].graphite.'e-'.consRot and cell.anFP.subregions[1,j,1].graphite.'e-'.Nu_Phi[FCSys.Species.Enumerations.Axis.x] == 4 and cell.anFP.subregions[1,j,1].graphite.'e-'.kL[2] > 0 and (cell.anFP.subregions[1,j,1].graphite.V / cell.anFP.subregions[1,j,1].L[FCSys.Species.Enumerations.Axis.y]) > 0, "shear family anFP y-law prerequisites");
        assert(not cell.caFP.subregions[1,j,1].graphite.'e-'.upstreamY and not cell.caFP.subregions[1,j,1].graphite.'e-'.consRot and cell.caFP.subregions[1,j,1].graphite.'e-'.Nu_Phi[FCSys.Species.Enumerations.Axis.x] == 4 and cell.caFP.subregions[1,j,1].graphite.'e-'.kL[2] > 0 and (cell.caFP.subregions[1,j,1].graphite.V / cell.caFP.subregions[1,j,1].L[FCSys.Species.Enumerations.Axis.y]) > 0, "shear family caFP y-law prerequisites");
      end for;
      for j in 2:n_y loop
        assert(cell.anFP.subregions[1,j-1,1].graphite.'e-'.eta > 0 and cell.anFP.subregions[1,j-1,1].graphite.'e-'.eta == cell.anFP.subregions[1,j,1].graphite.'e-'.eta, "shear family anFP y equal eta");
        assert(cell.caFP.subregions[1,j-1,1].graphite.'e-'.eta > 0 and cell.caFP.subregions[1,j-1,1].graphite.'e-'.eta == cell.caFP.subregions[1,j,1].graphite.'e-'.eta, "shear family caFP y equal eta");
      end for;

    equation
      for j in 1:n_y loop
        cell.anGDL.subregions[1,j,1].graphite.'e-'.xNegativeAfterShearClosure =
          ((cell.anFP.subregions[1,j,1].graphite.V / cell.anFP.subregions[1,j,1].L[FCSys.Species.Enumerations.Axis.x]) *
           cell.anGDL.subregions[1,j,1].graphite.'e-'.kL[1]) /
          ((cell.anGDL.subregions[1,j,1].graphite.V / cell.anGDL.subregions[1,j,1].L[FCSys.Species.Enumerations.Axis.x]) *
           cell.anFP.subregions[1,j,1].graphite.'e-'.kL[1] +
           (cell.anFP.subregions[1,j,1].graphite.V / cell.anFP.subregions[1,j,1].L[FCSys.Species.Enumerations.Axis.x]) *
           cell.anGDL.subregions[1,j,1].graphite.'e-'.kL[1]) *
          cell.anFP.subregions[1,j,1].graphite.'e-'.phi[2];
      end for;
      for j in 1:n_y loop
        cell.caGDL.subregions[1,j,1].graphite.'e-'.xPositiveAfterShearClosure =
          ((cell.caFP.subregions[1,j,1].graphite.V / cell.caFP.subregions[1,j,1].L[FCSys.Species.Enumerations.Axis.x]) * cell.caGDL.subregions[1,j,1].graphite.'e-'.kL[1]) /
          ((cell.caGDL.subregions[1,j,1].graphite.V / cell.caGDL.subregions[1,j,1].L[FCSys.Species.Enumerations.Axis.x]) * cell.caFP.subregions[1,j,1].graphite.'e-'.kL[1] + (cell.caFP.subregions[1,j,1].graphite.V / cell.caFP.subregions[1,j,1].L[FCSys.Species.Enumerations.Axis.x]) * cell.caGDL.subregions[1,j,1].graphite.'e-'.kL[1]) * cell.caFP.subregions[1,j,1].graphite.'e-'.phi[2];
      end for;
      for j in 2:n_y loop
        cell.anFP.subregions[1,j,1].graphite.'e-'.yNegativeBeforeShearClosure =
          ((cell.anFP.subregions[1,j-1,1].graphite.V / cell.anFP.subregions[1,j-1,1].L[FCSys.Species.Enumerations.Axis.y]) * cell.anFP.subregions[1,j,1].graphite.'e-'.kL[2] * cell.anFP.subregions[1,j-1,1].graphite.'e-'.phi[1] + (cell.anFP.subregions[1,j,1].graphite.V / cell.anFP.subregions[1,j,1].L[FCSys.Species.Enumerations.Axis.y]) * cell.anFP.subregions[1,j-1,1].graphite.'e-'.kL[2] * cell.anFP.subregions[1,j,1].graphite.'e-'.phi[1]) /
          ((cell.anFP.subregions[1,j-1,1].graphite.V / cell.anFP.subregions[1,j-1,1].L[FCSys.Species.Enumerations.Axis.y]) * cell.anFP.subregions[1,j,1].graphite.'e-'.kL[2] + (cell.anFP.subregions[1,j,1].graphite.V / cell.anFP.subregions[1,j,1].L[FCSys.Species.Enumerations.Axis.y]) * cell.anFP.subregions[1,j-1,1].graphite.'e-'.kL[2]);
        cell.caFP.subregions[1,j,1].graphite.'e-'.yNegativeBeforeShearClosure =
          ((cell.caFP.subregions[1,j-1,1].graphite.V / cell.caFP.subregions[1,j-1,1].L[FCSys.Species.Enumerations.Axis.y]) * cell.caFP.subregions[1,j,1].graphite.'e-'.kL[2] * cell.caFP.subregions[1,j-1,1].graphite.'e-'.phi[1] + (cell.caFP.subregions[1,j,1].graphite.V / cell.caFP.subregions[1,j,1].L[FCSys.Species.Enumerations.Axis.y]) * cell.caFP.subregions[1,j-1,1].graphite.'e-'.kL[2] * cell.caFP.subregions[1,j,1].graphite.'e-'.phi[1]) /
          ((cell.caFP.subregions[1,j-1,1].graphite.V / cell.caFP.subregions[1,j-1,1].L[FCSys.Species.Enumerations.Axis.y]) * cell.caFP.subregions[1,j,1].graphite.'e-'.kL[2] + (cell.caFP.subregions[1,j,1].graphite.V / cell.caFP.subregions[1,j,1].L[FCSys.Species.Enumerations.Axis.y]) * cell.caFP.subregions[1,j-1,1].graphite.'e-'.kL[2]);
      end for;
  end Two;

  model Six
    extends Two(n_y=6);
  end Six;


  model TenControl
    extends Two(n_y=10);
  end TenControl;

  model PaperTen
    import U=FCSys.Units;
    parameter Real standard_T_K=298.15;
    parameter Real standard_p_Pa=100000;
    parameter Real dry_air_O2_fraction=0.20946;
    parameter Real R_SI=8.3144621;
    parameter Real F_SI=96485.3365;
    parameter Real sccm_to_m3_per_s=1e-6/60;
    parameter Real anode_sccm=25;
    parameter Real air_sccm(min=20, max=50)=50 "Registered air case (20 or 50 sccm)";
    parameter Real h2_equivalent_current_A=2*F_SI*anode_sccm*sccm_to_m3_per_s*standard_p_Pa/(R_SI*standard_T_K);
    parameter Real air_equivalent_current_A=4*F_SI*dry_air_O2_fraction*air_sccm*sccm_to_m3_per_s*standard_p_Pa/(R_SI*standard_T_K);
    extends Two(
      n_y=10,
      anFlowSet(k=h2_equivalent_current_A*U.A),
      caFlowSet(k=air_equivalent_current_A*U.A),
      cell(
        L_y=fill(110*U.mm/10,10),
        L_z={2*U.mm},
        anFP(epsilon=0.05,D=1*U.mm,L_channel=110*U.mm,subregions(each gas(k={0.01,1,1}))),
        caFP(epsilon=0.05,D=1*U.mm,L_channel=110*U.mm,subregions(each gas(k={0.01,1,1})))),
      environment(T=303.15*U.K,p=U.atm,RH=1),
      testConditions(anRH=1,caRH=1),
      load(V=0.75));
    initial equation
      assert(air_sccm == 20 or air_sccm == 50, "air_sccm must be exactly 20 or 50");
      assert(standard_T_K == 298.15 and standard_p_Pa == 100000 and dry_air_O2_fraction == 0.20946, "registered standard state/composition is immutable");
      assert(R_SI == 8.3144621 and F_SI == 96485.3365 and sccm_to_m3_per_s == 1e-6/60 and anode_sccm == 25, "registered conversion constants are immutable");
  end PaperTen;
end DCell;
