# Nested array binding reproducer

Standalone numerical compiler diagnostic on pinned OpenModelica1.27.0; no FCSys physics or physical validation. Six positive decaying states feed three mathematically identical q=p^order formulations with distinct decay rates. Over0-1s and502 saved samples, the nested array-comprehension modifier keeps q=2 despite p falling to0.735759. Explicit array-literal modifiers and explicit equations track their changing states with zero recorded discrepancy.

Generated metadata assigns nested q only in initialization; literal q has regular assignments, and the explicit-equation form resolves through aliases to its live equation. This isolates a state-dependent nested-comprehension binding failure in this fixture and supports testing explicit scalar bindings in the actual cell. Different decay rates were chosen to prevent common-expression merging; no broad claim about every array comprehension or compiler version is established.

Check0.843s, translation0.991s, stock build4.918s; native successful, exact horizon verified. Raw stage commands/logs/release hashes are retained. Source/flat audit covered the complete printed44-line flat; its original prose line count mistakenly said52, corrected separately in results/audit-count-correction.json without rewriting the released audit.

See results/verification.json and harness/BindingProbe.mo. Actual-cell acceptance belongs to ../oxygen-explicit-binding-20260929T172830Z/README.md.
