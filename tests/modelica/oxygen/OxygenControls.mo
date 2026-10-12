within;
package OxygenControls
 model Matrix
  parameter Real I0_scale(min=0.1)=1 "Prespecified amplitude sensitivity, not a fitted calibration";
  extends OxygenLocal.Matrix(
   native(each I0_set=I0_scale*0.00506*FCSys.Units.mA),
   disabled(each I0_set=I0_scale*0.00506*FCSys.Units.mA),
   candidate(each I0_set=I0_scale*0.00506*FCSys.Units.mA));
 end Matrix;
end OxygenControls;
