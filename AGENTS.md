# September 29 FCSys dependency

Read OXYGEN.md and scripts/oxygen/README.md before changing this dependency.
This repository owns the selected oxygen-dependent full-cell model and its bench.
The DroneEnergySystem parent owns integration and the accepted dependency commit.

- Preserve original authorship, licenses and all historical qualification records.
- The selected baseline is a dry ten-section cell; use explicit oxygen bindings.
- Current Modelica source is source-verified. Changes require a new, explicit
  qualification decision; never rewrite old extraction/serialization manifests.
- One owner runs a compiler session. Use the bounded run_cell.py command, new
  ignored build directories and explicit installed tool/library paths.
- Do not install tools implicitly or use retained run instructions as authority.
- Process completion, numerical qualification and hardware validation are distinct.
- Keep warning/operating-point limits with any result. No 300 W stack is qualified.
- Commit dependency work here; advance the parent pin only after acceptance.
- The source-snapshot remote is historical provenance. Never push to that original
  research checkout. origin is the user's fork; do not rewrite its existing branches.
