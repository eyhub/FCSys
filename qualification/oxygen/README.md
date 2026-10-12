# Current oxygen-cell qualification

full-cell-baseline.json preserves the successful fresh ten-section native1 result
from 2026-10-12. environment.json declares the explicitly supported environment.
No physical Modelica files changed when the reusable runner was introduced.

One case is qualified: oxygenOrder=1, 50 sccm air, 25 sccm H2, 0.65 V, ambient
303.15 K, RH=1, 180 s. All 19 original whole-cell gates passed. This is numerical
verification, not empirical calibration, wet-cell qualification or a 300 W stack.

Warnings remain visible: 489 compiler warnings (initial values, deprecated Real
comparisons, two nitrogen signal connectors, aliases/state selection) and 177
startup pressure-minimum warnings for charged species. IDA recovered from internal
error/convergence test failures and completed; all final gates passed. No warning
was repaired by changing model physics or loosening numerical tolerances.

Review of the full runtime logs also found 72 linear-solver total-pivoting fallback
warnings at initialization (time 0) in the original run and both relocated runner
attempts. Earlier summaries counted only the 177 pressure warnings. The MAT files
are byte-identical. The runner records these 72 initialization fallbacks separately;
different wording, nonzero times or unexpected nonzero counts stop acceptance.
This is a documented solver limitation, not a repaired model or a warning-free run.

The original oxygen-20260929/ evidence and serialization manifests remain immutable.
The documentation-maintenance.json map permits exactly the current root README,
OXYGEN guide and source verifier to evolve; it carries baseline/current canonical
hashes and does not exempt physical models or old evidence from integrity checks.

Run output is deliberately excluded from Git. The reusable command writes full
provenance, actual source/tool paths and hashes, logs, executable, MAT, numerical
checks and artifacts manifest under build/. Preserve that directory when archiving
a study. Neither an expected hash nor a process exit alone establishes acceptance.
