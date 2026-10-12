# Provenance

Measured: raw compiler/build/runtime logs, three new MAT outputs, actual 0..0.1 s horizons and component variables. The copied FCSys and OxygenLocal sources are byte-identical to the qualified oxygen-variable-binding-20260929T170713Z parent; results/source-identity.json records every input pair. The only source addition is harness/OxygenControls.mo. The complete flat audit, releases and atomic claims precede their dependent stages.

Derived: scripts/verify.py independently checks the rate law, stoichiometry, equilibrium-potential change and amplitude scaling using actual MAT variables and unit scales. scripts/analyze.py rehashes the two accepted coupled MATs, evaluates conditional eta/T freezes and creates the figure and aggregate results. Figure inspected visually: axes, units, series and analytic-versus-measured labels readable. Conditional replays are not new transport solutions.

Inferred within the controlled scope: adjusting constant I0 amplitude alone cannot change the explicit oxygen order at fixed eta/T. Coupled local-overpotential feedback partly compensates the candidate law. Neither inference selects a universally valid oxygen exponent or experimentally calibrated parameters.

Known exact source paths were opened directly. The new wrapper is outside retained graph coverage; no Graphify rebuild, external indexing, Jev invocation or external message occurred. No new production files were read or changed in this bundle; hashes.txt therefore records this fact and source-identity.json/release files pin the retained run-local inputs. The prior coupled bundle remains immutable and its startup warnings remain part of its evidence.

No failed native stages or acceptance-gate relaxations occurred. One initial source lookup used nonexistent scripts/verify.py in the retained coupled bundle; bounded file discovery located verify_cell.py, which was read before analysis. This lookup had no execution or scientific effect.
