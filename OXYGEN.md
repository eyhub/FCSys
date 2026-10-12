# September 29 oxygen-dependent FCSys

Standalone dependency for the selected dry ten-section `OxygenCoupled.Cell`.
Develop on `oxygen-sep29`; DroneEnergySystem records an accepted commit separately.
Original research folders are historical provenance, not a second editable source.

## Run the complete cell

The supported command builds, simulates 180 seconds and applies all 19 numerical
gates. From this checkout, using the actual installed paths:

```powershell
python -B scripts/oxygen/run_cell.py --omc-home "C:/Program Files/OpenModelica1.27.0-64bit" --modelica-library "C:/Users/ZGR/AppData/Roaming/.openmodelica/libraries"
```

Tools/libraries must match [environment.json](qualification/oxygen/environment.json).
Nothing is installed automatically. NumPy 2.4.2 and SciPy 1.17.1 are required;
Python 3.14.3 on Windows x64 was qualified. See the [runner guide](scripts/oxygen/README.md).
No OMD, Thesis-cell folder or external reference MAT is needed for this case.
Do not use Python -O. Each invocation creates a new ignored build/cell-<timestamp>
directory. run.json becomes PASS only after fresh execution and verification.

## Selected model and result

- Full cell: OxygenCoupled.Cell extends DCell.PaperTen, with seven ten-section layers.
- CaGDL grid: 1 x 10 x 1; ten channelwise divisions, not DCell.Six.
- qO2=(local catalyst-layer pO2/pO2_ref)^oxygenOrder; oxygenOrder=1 and
  pO2_ref=0.14603527167717584 atm. Preserve ten explicit scalar pressure bindings:
  a nested-comprehension form froze values in the OpenModelica 1.27 diagnostic.
- Case: 50 sccm air, 25 sccm hydrogen, 0.65 V, 303.15 K ambient, RH=1, 180 s.
- IDA, coloredNumerical Jacobian, tolerance 1e-6; 446 continuous states.

The [baseline](qualification/oxygen/full-cell-baseline.json) passed all 19 gates
with 504 saved samples. Final current: 0.7780197059 A; power: 0.5057128088 W;
oxygen utilization: 28.6298%. This is a small single-cell geometry, not a qualified
300 W stack or integrated drone model.

Translation warnings include initialization defaults, deprecated Real equality,
nitrogen-pressure signal connector imbalance, aliases and state selection.
Startup pressure-minimum warnings affect electrons, protons, graphite C+ and
ionomer SO3-. Numerical acceptance does not resolve these warnings or establish
empirical/hardware validity. Read [qualification notes](qualification/oxygen/README.md).

## Source and compatibility

FCSys 0.2.6/ owns the library/resources. experimental/oxygen-paperten/ owns the
full-cell harness; tests/modelica/oxygen/ contains component/binding diagnostics.
scripts/oxygen/ owns runnable support. Original tests/oxygen/ verifiers remain
historical source; use the adapted scripts instead.

Load Modelica 3.2.3+maint.om, FCSys, KulikovskyDistributed, DCell, then OxygenCoupled.
The runner checks actual loaded paths and versions. Complex/ModelicaServices
4.1.0+maint.om were resolved. DronePlant's Modelica 4.1.0, the inherited wet TestStand,
empirical oxygen-law calibration and broad operating sweeps need separate work.

Source baseline: 3a58218e24d6e7302d0fbb6ff34c688c80cd451e, based on
19b9d322446843d5cba55073de0bcc0610767af7. The 41 selected files and five library
overlays retain their exact source bytes. Historical [EXTRACTION.json](qualification/oxygen-20260929/EXTRACTION.json)
and [SERIALIZATION.json](qualification/oxygen-20260929/SERIALIZATION.json) are immutable.
Root guidance and the source verifier evolve under the narrow
[documentation maintenance map](qualification/oxygen/documentation-maintenance.json),
which cannot authorize Modelica or historical-evidence changes.

`python -B scripts/verify_oxygen_extraction.py` checks source integrity without a
compiler. Optional --sources checks the original historical locations; normal
verification and the full-cell runner do not require them.

## Ownership and licensing

User fork: https://github.com/eyhub/FCSys.git; upstream: https://github.com/kdavies4/FCSys.git.
Keep this variant on its dedicated branch. source-snapshot is historical local
provenance: never push to that old research checkout. Commit/qualify dependency
changes here, then advance the parent pin explicitly. Do not follow branch tips silently.

Retain upstream Modelica License 2, original authorship and separate resource
licenses. New tooling does not claim authorship of the imported physical models.
