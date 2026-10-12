# September 29 oxygen source assembly

This checkout contains the selected dry ten-section `OxygenCoupled.Cell` variant,
assembled on 2026-10-12 from retained research sources. Branch: `oxygen-sep29`.
Base commit: `19b9d322446843d5cba55073de0bcc0610767af7`.
This branch records the recovered oxygen source as a local baseline commit.
It is not runtime-qualified; the oxygen models have not been run from this checkout.

## Source layout

| Location | Purpose |
| --- | --- |
| FCSys 0.2.6/ | Inherited library/resources with five selected library replacements |
| experimental/oxygen-paperten/ | KulikovskyDistributed, DCell and OxygenCoupled whole-cell harness |
| tests/modelica/oxygen/ | OxygenLocal, OxygenControls and BindingProbe fixtures |
| tests/oxygen/ | Historical verifier sources and polarization case configuration |
| qualification/oxygen-20260929/ | Selected historical evidence and EXTRACTION.json |
| scripts/verify_oxygen_extraction.py | Source-integrity check; never launches a compiler |

The library replacements are Characteristics.mo, Chemistry.mo, Phases.mo,
Species.mo and Subregions.mo. Together they preserve inherited dry-cell,
transport, entropy and stable-asinh prerequisites plus the qO2 current multiplier.
The harness supplies ten explicit scalar local-pressure bindings; retain their
form until an intentional, tested change is made.

The intended load order, once a qualified local execution recipe is prepared, is:

1. Modelica 3.2.3+maint.om.
2. FCSys 0.2.6/package.mo.
3. experimental/oxygen-paperten/KulikovskyDistributed.mo.
4. experimental/oxygen-paperten/DCell.mo.
5. experimental/oxygen-paperten/OxygenCoupled.mo.

The whole-cell entry is `OxygenCoupled.Cell`. The selected defaults preserve
oxygenOrder=1 and pO2_ref=0.14603527167717584 atm. The library's qO2=1 default
alone does not enable the pressure-dependent wrapper. The September 4 wet-cell
candidate is not included.

## Current verification and limits

Run `python -B scripts/verify_oxygen_extraction.py` from this repository to check
the assembled source and inherited files. Add `--sources` to check the original
local research/fork files too. This command does not import NumPy/SciPy or Modelica.
It checks the recorded baseline; later intentional edits need a new provenance
record rather than silently replacing historical hashes. Imported files use exact
byte checks. Inherited text may use explicitly recorded CRLF-to-LF canonicalization;
binary resources always use exact checks.

The copied Python verifiers are historical source, not runnable standalone entry
points yet. They refer to Thesis-cell layouts and external trajectory fixtures.
No new runner, environment lock, installation or runtime profile has been added.
Prepare explicit repository-local paths and reference-data access before executing
them. Historical release/claim files are not current execution authority.

Retained coupled runs used OpenModelica 1.27.0 Windows 64-bit, MSL 3.2.3+maint.om,
IDA, coloredNumerical, tolerance 1e-6 and a 180-second simulated horizon. Recheck
all resolved dependencies when qualifying this checkout. The component controls
reported Euler despite requesting DASSL. No numerical result was reproduced during
assembly, and compatibility with DronePlant's MSL 4.1.0 is unresolved.

The historical candidate shifted matched-voltage current by up to 22.94% in the
tested comparison. Selection does not establish empirical calibration or preserve
the native polarization curve. Native wet TestStand compatibility needs separate
requalification after this five-file overlay; inherited openmodelica documents
and source manifests describe the base commit, not the oxygen working tree.

## Provenance and development ownership

[EXTRACTION.json](qualification/oxygen-20260929/EXTRACTION.json) records the 41-file
allowlist, source paths/hashes, all 970 inherited file identities, and documentation
adaptations. The initial clone normalized 276 line endings; those working files
were restored to the original snapshot bytes and verified before the overlay.
The extraction manifest is the immutable assembly-event record, including its
then-uncommitted status. [SERIALIZATION.json](qualification/oxygen-20260929/SERIALIZATION.json)
records the baseline Git blob identities and text-normalization rules. Explicit
.gitattributes entries preserve all 41 imported files and the provenance records
byte-for-byte. A clean local clone verifies the committed form separately.

This independent checkout is the authoritative development repository for the
selected FCSys variant. Original Thesis-cell sources and the old fork checkout remain untouched.
The sole remote, source-snapshot, is a local provenance locator; no publication
remote or upstream tracking branch has been selected. No remote was contacted.
The parent DroneEnergySystem repository has not registered this as a submodule.
Do not stage this directory as an ordinary embedded repository in the parent.

Retain upstream Modelica License 2, original authorship and separate resource
licenses. Existing source notices remain unchanged. New files record extraction
and integrity checks; they do not claim authorship of the imported physical models.

Next: prepare local load/verification entry points and fixture paths, then qualify
the isolated configuration before registering an accepted system dependency pin.
The source-baseline commit itself does not claim scientific qualification.
