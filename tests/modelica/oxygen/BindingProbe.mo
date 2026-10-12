within;
package BindingProbe
 model Part
  Real q=1;
  Real y;
 equation
  y=2*q;
 end Part;
 model Slice
  parameter Real k=1;
  Real p(start=2,fixed=true);
  Part part;
 equation
  der(p)=-k*p;
 end Slice;
 model Matrix
  parameter Real order=1;
  Slice nested[1,2,1](each k=1,part(q={{{nested[i,j,k].p^order for k in 1:1} for j in 1:2} for i in 1:1}));
  Slice literal[1,2,1](each k=2,part(q={{{literal[1,1,1].p^order},{literal[1,2,1].p^order}}}));
  Real qLive[1,2,1];
  Slice explicitEquation[1,2,1](each k=3,part(q=qLive));
 equation
  for j in 1:2 loop
   qLive[1,j,1]=explicitEquation[1,j,1].p^order;
  end for;
  annotation(experiment(StartTime=0,StopTime=1,Interval=0.01,Tolerance=1e-8));
 end Matrix;
end BindingProbe;
