# Run and verify the selected oxygen cell

The complete-cell command is:

```powershell
python -B scripts/oxygen/run_cell.py --omc-home "C:/Program Files/OpenModelica1.27.0-64bit" --modelica-library "C:/Users/ZGR/AppData/Roaming/.openmodelica/libraries"
```

Substitute your existing installation/library paths. Qualified environment:
Windows x64, OpenModelica 1.27.0, Modelica 3.2.3+maint.om, Complex/ModelicaServices
4.1.0+maint.om, Python 3.14.3, NumPy 2.4.2 and SciPy 1.17.1. Exact tool and library
entry hashes are in ../../qualification/oxygen/environment.json. requirements.txt
pins verifier packages for explicit environment setup; this command never installs.
Other tool builds require a reviewed requalification, not bypassing identity checks.

The command runs the selected full-cell native1 case only, with oxygenOrder=1.
It does not require old research folders, a fixture map or OMD. Default output is
a new timestamped directory under build/. Use --output-dir for an explicit new
path below this checkout/build. Existing directories are rejected. Clean source is
required by default; --allow-dirty records an explicitly exploratory run and exact
working-file hashes. Baseline Modelica integrity is still required in either mode.

Stages are bounded: translation 600 s, native compilation 300 s, simulation 180 s
wall time. The simulated horizon is 180 s with an explicit 0.36 s output interval;
IDA retains adaptive internal time steps. The runner checks five loads, actual
library paths, seven 1 x 10 x 1 layer grids, 446 states and ten regular qO2 equations
before compiling. It verifies the new MAT with the unchanged 19 full-cell gates.
There is no parameter sweep, calibration, stack sizing or system integration here.

Output: Run.mos, per-stage process JSON and stdout/stderr logs, translation-audit.json,
warnings.json, native1.mat, verification.json, run.json and a hashed artifacts.json.
Only run.json status PASS denotes completed numerical acceptance. Process accepted
means only the stage completed with its required checks. Failures retain evidence
and exit nonzero; use a new output directory for a new attempt. No automatic retries.

A compiler-wide lock in the user's temporary directory and a checkout-local
build/omc-owner.lock prevent concurrent runner ownership. Existing locks are never
guessed stale or removed. If a controller crashed, inspect its recorded PID/output
and confirm it and its owned children have ended before manually clearing its lock.
Timeout termination targets only the runner's own process tree. Do not use -O.

Known translation/startup warnings are retained. Unreviewed runtime warnings stop
acceptance. See ../../qualification/oxygen/README.md and ../../OXYGEN.md for scope.

Checks without simulation:

```powershell
python -B scripts/verify_oxygen_extraction.py
python -B tests/oxygen/test_local_entrypoints.py
python -B tests/oxygen/test_runner.py
```

## Lower-level preparation and retained-result verification

The commands below are separate preparation/replay tools. They do not themselves
launch a compiler; run_cell.py above is the demonstrated complete execution path.

## Prepare actual model loading

Run from the FCSys repository. Choose a new output directory for each attempt:

```powershell
python -B scripts/oxygen/prepare.py load --profile binding --output-dir build/qualification/binding
python -B scripts/oxygen/prepare.py load --profile controls --output-dir build/qualification/controls
python -B scripts/oxygen/prepare.py load --profile cell --output-dir build/qualification/cell
```

Each writes Load.mos, Translate.mos and preparation.json. Paths are resolved from
this repository, with FCSys before the ordered harness files. BindingProbe is
independent of FCSys. The recipe preserves the retained Modelica 3.2.3 request and
translation calls. preparation.json captures source hashes, commit and dirty status.

No compiler is invoked by these commands. Later execution must use the generated
directory as its working directory, the explicitly selected OpenModelica executable,
bounded stages and a single session owner. Review every load result, compiler error
and resolved library version before accepting translation. These scripts do not
enforce execution time limits or record process receipts; use run_cell.py above for
the qualified complete-cell execution. Generated scripts contain resolved absolute checkout paths and
must be regenerated after moving the checkout. Do not commit build outputs.

## Reference fixtures

[reference-fixtures.json](../../tests/oxygen/reference-fixtures.json) pins eight
native PaperTen trajectories and the component-calibration parent by SHA-256.
The files remain external; small endpoint records cannot replace their time-series
checks. On the current machine, make an explicit local map with:

```powershell
python -B scripts/oxygen/prepare.py fixtures --source-root C:/Thesis-cell --output build/qualification/fixtures.local.json
```

This reads and hashes all nine files and writes their locations; it copies no MATs.
On another machine, supply a JSON map with a `files` object mapping those fixture
IDs to local paths. Relative paths resolve against the map's directory. Each used
reference is checked against the repository's fixed hash, so relocating data does
not change its identity. Keep machine-specific maps under ignored build/.

## Verify a result explicitly

The entry points are verify_cell.py, verify_controls.py and verify_polarization.py.
Each requires `--case`, `--mat`, `--mat-sha256`, `--process-record`,
`--evidence-kind` and `--output`. Use `--fixtures` for component controls and
native-equivalence cases. `--help` lists the supported case names.

For example, after setting these paths/hash to an actual retained case:

```powershell
python -B scripts/oxygen/verify_cell.py --case native0 --mat $matPath --mat-sha256 $matSha256 --process-record $receiptPath --fixtures build/qualification/fixtures.local.json --evidence-kind retained-replay --output build/qualification/native0-verification.json
```

Use `retained-replay` for old result data; use `new-run` only with a newly executed
case and its actual process record. A process record must report accepted=true,
exit_code=0, timeout=false, and the matching artifact filename. If it provides a
stage or MAT hash, those must match too. Historical receipts do not all include a
MAT hash: the explicitly supplied hash is separately checked and this limitation
is recorded in verification_context. A passed numerical checker does not by itself
establish compiler provenance, process-record authenticity or empirical validation.

Outputs include input/receipt hashes, reference identities, verifier source hashes,
Git HEAD/dirty status, dependency versions and the declared evidence kind.
They must be new files within this repository's build/
directory; existing results and qualification evidence are never overwritten.
Do not use Python -O: the original assertion checks are required.

NumPy and SciPy must already be available. Development replay used NumPy 2.4.2 and
SciPy 1.17.1; no historical dependency-version equivalence is claimed and no package
was installed. The complete native1 run has since been qualified separately; these retained replays alone do not provide that qualification.

## Preparation checks

```powershell
python -B tests/oxygen/test_local_entrypoints.py
python -B scripts/verify_oxygen_extraction.py
```

The first checks input rejection, output preservation, fixture integrity and actual
load order. Its small fake byte strings test input boundaries only, never scientific
results. The second verifies the untouched committed source baseline. New entry-point
files are checked separately and are not retroactively covered by that baseline.

Development validation replayed five retained MATs: native0/native1, scale1 and
two polarization cases (gamma0 air20/0.75 V and gamma1 air20/0.65 V). Every existing
numeric field matched its retained verification record within relative 1e-10 /
absolute 1e-12; gates and structure matched exactly. This validates the I/O adaptation
for those cases, not fresh model execution or the complete polarization sweep.
