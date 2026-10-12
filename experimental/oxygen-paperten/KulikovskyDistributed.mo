within FCSys.Assemblies.Cells.Examples;
package KulikovskyDistributed "Run-local distributed electrical collection candidates"
      model TestStandDistributed "Distributed electrical collection variant of TestStand"
        import 'Datae-' = FCSys.Characteristics.'e-'.Graphite;
        import DataH2 = FCSys.Characteristics.H2.Gas;
        import DataH2O = FCSys.Characteristics.H2O.Gas;
        import DataO2 = FCSys.Characteristics.O2.Gas;
        import average = FCSys.Utilities.Means.arithmetic;
        extends Modelica.Icons.Example;

        // Aliases
        Q.Current zI "Electrical current";

        // Auxiliary variables (for analysis)
        output Q.Potential w=load.v*U.V "Potential";
        output Q.CurrentAreic J=zI/cell.caFP.A[Axis.x] "Current density";
        output Q.Number J_Apercm2=J*U.cm^2/U.A "Current density, in A/cm2";
        output Q.PressureAbsolute p_an_in=average(average(anSource.gas.H2.boundary.p
             + anSource.gas.H2O.boundary.p)) if environment.analysis
          "Total pressure at the anode inlet";
        output Q.PressureAbsolute p_ca_in=average(average(caSource.gas.H2O.boundary.p
             + p_N2_in + caSource.gas.O2.boundary.p)) if environment.analysis
          "Total pressure at the cathode inlet";
        output Q.Pressure Deltap_an=environment.p - p_an_in if environment.analysis
          "Pressure difference down the anode channel";
        output Q.Pressure Deltap_ca=environment.p - p_ca_in if environment.analysis
          "Pressure difference down the cathode channel";
        output Q.Potential Deltaw_O2=(DataO2.g(caSource[1, 1].gas.O2.boundary.T,
            caSource[1, 1].gas.O2.boundary.p) - cell.caCL.subregions[1, 1, 1].gas.O2.g)
            /4 if environment.analysis "Voltage loss due to O2 supply";
        output Q.Potential Deltaw_H2O=(DataH2O.g(caSource[1, 1].gas.H2O.boundary.T,
            caSource[1, 1].gas.H2O.boundary.p) - cell.caCL.subregions[1, 1, 1].gas.H2O.g)
            /2 if environment.analysis "Voltage loss due to H2O removal";
        output Q.Potential Deltaw_H2=(DataH2.g(anSource[1, 1].gas.H2.boundary.T,
            anSource[1, 1].gas.H2.boundary.p) - cell.anCL.subregions[1, 1, 1].gas.H2.g)
            /2 if environment.analysis "Voltage loss due to H2 supply";
        output Q.Potential 'Deltaw_e-'=cell.caFP.subregions[1, 1, 1].graphite.
            'e-'.g_boundaries[1, Side.p] - cell.caCL.subregions[1, 1, 1].graphite.
            'e-'.g + cell.anCL.subregions[1, 1, 1].graphite.'e-'.g - cell.anFP.subregions[
            1, 1, 1].graphite.'e-'.g_boundaries[1, Side.n] if environment.analysis
          "Voltage loss due to e- transport";
        output Q.Potential 'Deltaw_H+'=cell.anCL.subregions[1, 1, 1].ionomer.
            'H+'.g - cell.caCL.subregions[1, 1, 1].ionomer.'H+'.g if
          environment.analysis "Voltage loss due to H+ transport";
        output Q.Potential Deltaw_an=cell.anCL.subregions[1, 1, 1].graphite.
            'e-Transfer'.Deltag if environment.analysis "Anode overpotential";
        output Q.Potential Deltaw_ca=-cell.caCL.subregions[1, 1, 1].graphite.
            'e-Transfer'.Deltag if environment.analysis "Cathode overpotential";

        replaceable Cell cell(inclN2=environment.psi_O2_dry < 1 - Modelica.Constants.eps)
          constrainedby FCSys.Icons.Cell "Fuel cell" annotation (
          __Dymola_choicesFromPackage=true,
          choicesAllMatching=true,
          Placement(transformation(extent={{-10,-10},{10,10}})));

        // Conditions
        Conditions.ByConnector.BoundaryBus.Single.Sink anBC[cell.n_y, cell.n_z]
          (each graphite('inclC+'=true, redeclare
              Conditions.ByConnector.ThermalDiffusive.Single.Temperature 'C+'(
                set(y=environment.T))))
          "Boundary condition for the anode end plate, except electrical"
          annotation (Placement(transformation(
              extent={{10,-10},{-10,10}},
              rotation=90,
              origin={-24,0})));

        Conditions.ByConnector.BoundaryBus.Single.Source anSource[cell.anFP.n_x,
          cell.n_z](each gas(
            inclH2=true,
            inclH2O=true,
            H2(materialSet(y=-testConditions.Ndot_H2), thermalSet(y=environment.T)),

            H2O(materialSet(y=-testConditions.Ndot_H2O_an), thermalSet(y=
                    environment.T)))) "Source for the anode reactant stream"
          annotation (Placement(transformation(
              extent={{10,-10},{-10,10}},
              rotation=180,
              origin={-56,-24})));

        Conditions.ByConnector.BoundaryBus.Single.Sink anSink[cell.anFP.n_x,
          cell.n_z](gas(
            each inclH2=true,
            each inclH2O=true,
            H2(redeclare each function materialSpec =
                  Conditions.ByConnector.Boundary.Single.Material.current,
                materialSet(y=anSink.gas.H2O.boundary.Ndot .* cell.anFP.subregions[
                    :, cell.n_y, :].gas.H2O.v ./ cell.anFP.subregions[:, cell.n_y,
                    :].gas.H2.v)),
            H2O(materialSet(y=fill(
                          environment.p,
                          cell.anFP.n_x,
                          cell.n_z) - anSink.gas.H2.p))), each liquid(inclH2O=
                cell.inclLiq, H2O(materialSet(y=environment.p))))
          "Sink for the anode reactant stream" annotation (Placement(
              transformation(
              extent={{-10,-10},{10,10}},
              rotation=0,
              origin={-56,24})));

        Conditions.ByConnector.BoundaryBus.Single.Source caBC[cell.n_y, cell.n_z]
          (each graphite('inclC+'=true, 'C+'(set(y=environment.T))))
          "Boundary condition for the cathode end plate, except electrical"
          annotation (Placement(transformation(
              extent={{10,10},{-10,-10}},
              rotation=90,
              origin={24,0})));

        Conditions.ByConnector.BoundaryBus.Single.Source caSource[cell.caFP.n_x,
          cell.n_z](gas(
            each inclH2O=true,
            each inclN2=cell.inclN2,
            each inclO2=true,
            each H2O(materialSet(y=-testConditions.Ndot_H2O_ca), thermalSet(y=
                    environment.T)),
            N2(
              each materialSet(y=-testConditions.Ndot_N2),
              each thermalSet(y=environment.T),
              redeclare function materialMeas =
                  Conditions.ByConnector.Boundary.Single.Material.pressure),
            each O2(materialSet(y=-testConditions.Ndot_O2),thermalSet(y=
                    environment.T)))) "Source for the cathode reactant stream"
          annotation (Placement(transformation(
              extent={{10,-10},{-10,10}},
              rotation=180,
              origin={56,-24})));

        Conditions.ByConnector.BoundaryBus.Single.Sink caSink[cell.caFP.n_x,
          cell.n_z](gas(
            each inclO2=true,
            each inclN2=cell.inclN2,
            each inclH2O=true,
            H2O(materialSet(y=fill(
                          environment.p,
                          cell.caFP.n_x,
                          cell.n_z) - p_N2_out - caSink.gas.O2.p)),
            N2(
              redeclare function materialSpec =
                  Conditions.ByConnector.Boundary.Single.Material.current,
              materialSet(y=caSink.gas.H2O.boundary.Ndot .* cell.caFP.subregions[
                    :, cell.n_y, :].gas.H2O.v ./ cell.caFP.subregions[:, cell.n_y,
                    :].gas.N2.v),
              redeclare function materialMeas =
                  Conditions.ByConnector.Boundary.Single.Material.pressure),
            O2(redeclare function materialSpec =
                  Conditions.ByConnector.Boundary.Single.Material.current,
                materialSet(y=caSink.gas.H2O.boundary.Ndot .* cell.caFP.subregions[
                    :, cell.n_y, :].gas.H2O.v ./ cell.caFP.subregions[:, cell.n_y,
                    :].gas.O2.v))), each liquid(inclH2O=cell.inclLiq, H2O(
                materialSet(y=environment.p))))
          "Sink for the cathode reactant stream" annotation (Placement(
              transformation(
              extent={{-10,-10},{10,10}},
              rotation=0,
              origin={56,24})));

        inner Conditions.Environment environment(
          a={0,0,0},
          RH=testConditions.anRH,
          T=333.13*U.K,
          p=U.from_kPag(48.3)) "Environmental conditions"
          annotation (Placement(transformation(extent={{-30,30},{-10,50}})));

        replaceable Modelica.Electrical.Analog.Sources.ConstantVoltage load(
          V=0.8) constrainedby
          Modelica.Electrical.Analog.Interfaces.TwoPin "Electrical load"
          annotation (Placement(transformation(extent={{10,-60},{-10,-40}})));
        Modelica.Electrical.Analog.Basic.Ground ground
          annotation (Placement(transformation(extent={{-20,-80},{0,-60}})));
        Conditions.Adapters.MSL.Electronic anAdapt[cell.n_y, cell.n_z]
          "Interface with Modelica.Electrical on the anode side" annotation (
            Placement(transformation(
              extent={{-10,-10},{10,10}},
              rotation=270,
              origin={-10,-30})));
        Conditions.Adapters.MSL.Electronic caAdapt[cell.n_y, cell.n_z]
          "Interface with Modelica.Electrical on the cathode side" annotation (
            Placement(transformation(
              extent={{-10,-10},{10,10}},
              rotation=270,
              origin={10,-30})));

        Conditions.Router anRouter[cell.anFP.n_x, cell.n_z]
          "Switch to route the anode for reverse flow" annotation (Dialog,
            Placement(transformation(
              extent={{10,-10},{-10,10}},
              rotation=0,
              origin={-48,0})));
        Conditions.Router caRouter[cell.anFP.n_x, cell.n_z]
          "Switch to route the cathode for reverse flow" annotation (Dialog,
            Placement(transformation(
              extent={{10,-10},{-10,10}},
              rotation=0,
              origin={48,0})));

        TestConditions testConditions(I_ca=2*zI, I_an=1.5*zI) "Test conditions"
          annotation (Dialog, Placement(transformation(extent={{10,30},{30,50}})));

      protected
        connector NitrogenPressureSignal = Real;
        NitrogenPressureSignal p_N2_in[cell.caFP.n_x, cell.n_z](each unit=
              "M/(L.T2)") "Pressure of N2 at inlet";
        NitrogenPressureSignal p_N2_out[cell.caFP.n_x, cell.n_z](each unit=
              "M/(L.T2)") "Pressure of N2 at outlet";

        Connectors.ThermalDiffusive anThermalNode[cell.n_y,cell.n_z]
          "Declared thermal junction for the anode end plate" annotation(HideResult=true);
        Connectors.ThermalDiffusive caThermalNode[cell.n_y,cell.n_z]
          "Declared thermal junction for the cathode end plate" annotation(HideResult=true);


      equation
        // Aliases
        zI = load.i*U.A;

        // Nitrogen pressures (since N2 is conditionally included)
        if cell.inclN2 then
          connect(p_N2_in, caSource.y.gas.N2.material) "Not shown in diagram";
          connect(p_N2_out, caSink.y.gas.N2.material) "Not shown in diagram";
        else
          p_N2_in = zeros(cell.caFP.n_x, cell.n_y);
          p_N2_out = zeros(cell.caFP.n_x, cell.n_y);
        end if;

        for j in 1:cell.n_y loop
          for k in 1:cell.n_z loop
            connect(cell.an[j, k].graphite.'e-', anAdapt[j, k].boundary.graphite.'e-');
            connect(cell.ca[j, k].graphite.'e-', caAdapt[j, k].boundary.graphite.'e-');
          end for;
        end for;
        connect(cell.an.graphite.'C+', anThermalNode) annotation (Line(
            points={{-10,0},{-20,0}},
            color={127,127,127},
            thickness=0.5,
            smooth=Smooth.None));
        connect(anThermalNode, anBC.boundary.graphite.'C+') annotation (Line(
            points={{-10,0},{-20,0}},
            color={127,127,127},
            thickness=0.5,
            smooth=Smooth.None));
        connect(cell.ca.graphite.'C+', caThermalNode) annotation (Line(
            points={{10,0},{20,0}},
            color={127,127,127},
            thickness=0.5,
            smooth=Smooth.None));
        connect(caThermalNode, caBC.boundary.graphite.'C+') annotation (Line(
            points={{10,0},{20,0}},
            color={127,127,127},
            thickness=0.5,
            smooth=Smooth.None));
        connect(anRouter.positive2.gas, anSink.boundary.gas) annotation (Line(
            points={{-56,4},{-56,20}},
            color={240,0,0},
            thickness=0.5,
            smooth=Smooth.None));
        for j in 1:cell.anFP.n_x loop
          for k in 1:cell.n_z loop
            if anSink[j,k].liquid.inclH2O then
              connect(anRouter[j,k].positive2.liquid, anSink[j,k].boundary.liquid) annotation (Line(
            points={{-56,4},{-56,20}},
            color={240,0,0},
            thickness=0.5,
            smooth=Smooth.None));
            end if;
          end for;
        end for;
        connect(anRouter.positive1.gas, anSource.boundary.gas) annotation (Line(
            points={{-56,-4},{-56,-20}},
            color={240,0,0},
            thickness=0.5,
            smooth=Smooth.None));
        for j in 1:cell.anFP.n_x loop
          for k in 1:cell.n_z loop
            if anSource[j,k].liquid.inclH2O then
              connect(anRouter[j,k].positive1.liquid, anSource[j,k].boundary.liquid) annotation (Line(
            points={{-56,-4},{-56,-20}},
            color={240,0,0},
            thickness=0.5,
            smooth=Smooth.None));
            end if;
          end for;
        end for;
        connect(cell.anPositive.gas, anRouter.negative2.gas) annotation (Line(
            points={{-4,10},{-4,20},{-40,20},{-40,4}},
            color={240,0,0},
            thickness=0.5,
            smooth=Smooth.None));
        if cell.inclLiq then
          connect(cell.anPositive.liquid, anRouter.negative2.liquid) annotation (Line(
            points={{-4,10},{-4,20},{-40,20},{-40,4}},
            color={240,0,0},
            thickness=0.5,
            smooth=Smooth.None));
        end if;
        connect(cell.anNegative.gas, anRouter.negative1.gas) annotation (Line(
            points={{-4,-10},{-4,-20},{-40,-20},{-40,-4}},
            color={240,0,0},
            thickness=0.5,
            smooth=Smooth.None));
        if cell.inclLiq then
          connect(cell.anNegative.liquid, anRouter.negative1.liquid) annotation (Line(
            points={{-4,-10},{-4,-20},{-40,-20},{-40,-4}},
            color={240,0,0},
            thickness=0.5,
            smooth=Smooth.None));
        end if;
        connect(caSink.boundary.gas, caRouter.negative2.gas) annotation (Line(
            points={{56,20},{56,4}},
            color={0,0,240},
            thickness=0.5,
            smooth=Smooth.None));
        for j in 1:cell.caFP.n_x loop
          for k in 1:cell.n_z loop
            if caSink[j,k].liquid.inclH2O then
              connect(caSink[j,k].boundary.liquid, caRouter[j,k].negative2.liquid) annotation (Line(
            points={{56,20},{56,4}},
            color={0,0,240},
            thickness=0.5,
            smooth=Smooth.None));
            end if;
          end for;
        end for;
        connect(caSource.boundary.gas, caRouter.negative1.gas) annotation (Line(
            points={{56,-20},{56,-4}},
            color={0,0,240},
            thickness=0.5,
            smooth=Smooth.None));
        for j in 1:cell.caFP.n_x loop
          for k in 1:cell.n_z loop
            if caSource[j,k].liquid.inclH2O then
              connect(caSource[j,k].boundary.liquid, caRouter[j,k].negative1.liquid) annotation (Line(
            points={{56,-20},{56,-4}},
            color={0,0,240},
            thickness=0.5,
            smooth=Smooth.None));
            end if;
          end for;
        end for;
        connect(caRouter.positive2.gas, cell.caPositive.gas) annotation (Line(
            points={{40,4},{40,20},{4,20},{4,10}},
            color={0,0,240},
            thickness=0.5,
            smooth=Smooth.None));
        if cell.inclLiq then
          connect(caRouter.positive2.liquid, cell.caPositive.liquid) annotation (Line(
            points={{40,4},{40,20},{4,20},{4,10}},
            color={0,0,240},
            thickness=0.5,
            smooth=Smooth.None));
        end if;
        connect(caRouter.positive1.gas, cell.caNegative.gas) annotation (Line(
            points={{40,-4},{40,-20},{4,-20},{4,-10}},
            color={0,0,240},
            thickness=0.5,
            smooth=Smooth.None));
        if cell.inclLiq then
          connect(caRouter.positive1.liquid, cell.caNegative.liquid) annotation (Line(
            points={{40,-4},{40,-20},{4,-20},{4,-10}},
            color={0,0,240},
            thickness=0.5,
            smooth=Smooth.None));
        end if;
        for j in 1:cell.n_y loop
          for k in 1:cell.n_z loop
            connect(anAdapt[j, k].pin, load.n);
            connect(caAdapt[j, k].pin, load.p);
          end for;
        end for;
        connect(load.n, ground.p) annotation (Line(
            points={{-10,-50},{-10,-60}},
            color={0,0,255},
            smooth=Smooth.None));
        annotation (
          Documentation(info="<html>

    <p>Please see <a href=\"FCSys.Assemblies.Cells.Examples.TestConditions\">TestConditions</a> regarding

    how the properties of the environment are used.</p>

    <p>To run the cell with pure O<sub>2</sub> in the cathode (no N<sub>2</sub>), set <code>environment.psi_O2_dry</code> to 100%.</p>

    <p>Assumptions:</p>
    <ol>
    <li>The outer surface of each end plate has uniform temperature in the yz plane.</li>
    <li>No heat is conducted from the rest of the cell hardware.</li>
    <li>Electronic current is collected independently at each yz segment through distributed adapters; all anode adapters share the load negative pin and all cathode adapters share the load positive pin.</li>
    <li>There is no shear force on the fluid at either outlet.</li>
    <li>The pressure of each gas species is uniform over each inlet.</li>
    <li>The volumetric flow rates of the gas species are equal at each outlet, where the volumetric flow rate

    is approximated using the current at the outlet and the density of the gas within the last segment of the cell.</li>
    <li>The outlet pressure is applied to the gas mixture by Dalton's law (additivity of pressure).</li>
    <li>At the outlet, the liquid has the same pressure as the gas (Amagat's law).</li>
    <li>There is no thermal conduction across either outlet.</li>
    </ol>
    </html>"),
          Commands(file=
                "Resources/Scripts/Dymola/Assemblies.Cells.Examples.TestStand.mos"
              "Assemblies.Cells.Examples.TestStand.mos", file=
                "Resources/Scripts/Dymola/Assemblies.Cells.Examples.TestStand-states.mos"
              "Assemblies.Cells.Examples.TestStand-states.mos"),
          experiment(StopTime=36180, __Dymola_Algorithm="Dassl"),
          __OpenModelica_commandLineOptions="--generateDynamicJacobian=symbolic",
          __OpenModelica_simulationFlags(s="ida", jacobian="coloredSymbolical"),
          Diagram(coordinateSystem(preserveAspectRatio=false, extent={{-80,-80},
                  {80,60}}), graphics));
      end TestStandDistributed;


      model TestStandDistributedFixedFlow
        "Distributed electrical collection with fixed flow rate"
        extends TestStandDistributed(testConditions(I_an=anFlowSet.y, I_ca=caFlowSet.y));
        Modelica.Blocks.Sources.Constant anFlowSet(
          k=120*U.A+0.1*U.mA) "Specify the equivalent current of the anode supplies"
          annotation (Placement(transformation(extent={{-60,-60},{-40,-40}})));
        Modelica.Blocks.Sources.Constant caFlowSet(
          k=160*U.A+0.1*U.mA) "Specify the equivalent current of the cathode supplies"
          annotation (Placement(transformation(extent={{40,-60},{60,-40}})));
        annotation (experiment(StopTime=36120));
      end TestStandDistributedFixedFlow;

      model TestStandDistributedFixedFlowSegmented
        "Distributed electrical collection with multiple fixed-flow segments"
        parameter Integer n_y=2 "Number of segments in the y direction"
          annotation (Dialog(group="Geometry", __Dymola_label=
                "<html><i>n</i><sub>y</sub></html>"));

        extends TestStandDistributedFixedFlow(
          cell(
            inclLiq=false,
            L_y=fill(8*U.cm/n_y, n_y),
            anGDL(epsilon=0.45),
            caGDL(epsilon=0.45)),
          testConditions(I_an=anFlowSet.y, I_ca=caFlowSet.y));

        annotation (
          experiment(StopTime=36120),
          Diagram(coordinateSystem(preserveAspectRatio=false, extent={{-80,-80},
                  {80,60}}), graphics));
      end TestStandDistributedFixedFlowSegmented;
end KulikovskyDistributed;
