"""Process and generated-model checks for the qualified full-cell recipe."""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid
import xml.etree.ElementTree as ET


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, value, *, new=False):
    with Path(path).open('x' if new else 'w', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def confined_new_output(root, path):
    path = Path(path).resolve()
    build = (root / 'build').resolve()
    if path == build or not path.is_relative_to(build):
        raise ValueError('Use a new directory strictly below this checkout/build')
    if path.exists():
        raise FileExistsError(path)
    return path


@contextmanager
def own_session(path, description):
    token = uuid.uuid4().hex
    payload = dict(description, token=token, controllerPid=os.getpid())
    write_json(path, payload, new=True)
    try:
        yield
    finally:
        # Never remove a lock replaced by another owner.
        if Path(path).exists() and json.loads(Path(path).read_text())['token'] == token:
            Path(path).unlink()


def run_process(command, directory, name, timeout, env):
    receipt_path = directory / (name + '-process.json')
    if receipt_path.exists():
        raise FileExistsError(receipt_path)
    receipt = {'command': command, 'cwd': str(directory), 'operation': name,
               'startedUtc': datetime.now(timezone.utc).isoformat(),
               'wallLimitSeconds': timeout, 'accepted': False,
               'timeout': False, 'exit_code': None, 'state': 'starting'}
    write_json(receipt_path, receipt, new=True)
    start = time.monotonic()
    process = None
    try:
        with (directory / (name + '-stdout.log')).open('xb') as stdout, (directory / (name + '-stderr.log')).open('xb') as stderr:
            process = subprocess.Popen(command, cwd=directory, env=env, stdout=stdout, stderr=stderr,
                                       creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP)
            receipt.update(pid=process.pid, state='running')
            write_json(receipt_path, receipt)
            print(json.dumps({'stage': name, 'pid': process.pid, 'boundSeconds': timeout}), flush=True)
            try:
                receipt['exit_code'] = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                receipt['timeout'] = True
                killed = subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                                        capture_output=True, text=True, timeout=15,
                                        creationflags=subprocess.CREATE_NO_WINDOW)
                receipt['ownedTermination'] = {'exit_code': killed.returncode, 'stdout': killed.stdout, 'stderr': killed.stderr}
                receipt['exit_code'] = process.wait(timeout=15)
    except BaseException as error:
        receipt['exception'] = str(error)
        # A controller interruption must not leave its owned process tree running.
        if process is not None and process.poll() is None:
            subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                           capture_output=True, timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
            process.wait(timeout=15)
        raise
    finally:
        receipt.update(elapsedSeconds=time.monotonic()-start, state='terminal')
        write_json(receipt_path, receipt)
    if receipt['timeout'] or receipt['exit_code'] != 0:
        raise RuntimeError(f'{name} failed; see {receipt_path}')
    return receipt


def diagnostics(stdout):
    lines = [line for line in stdout.splitlines() if 'Warning:' in line]
    if re.search(r'\bError:', stdout):
        raise ValueError('Compiler reported an error despite process completion')
    return lines


def accept_translation(directory, libraries):
    stdout = (directory / 'translate-stdout.log').read_text()
    if (directory / 'translate-stderr.log').read_text():
        raise ValueError('Unexpected translation stderr; inspect it before acceptance')
    warnings = diagnostics(stdout)
    if stdout.split('BEGIN_LIBRARIES')[0].splitlines().count('true') != 5:
        raise ValueError('All five model/library loads must return true')
    block = stdout.split('BEGIN_STAGE=translate')[1].split('END_STAGE=translate')[0].strip()
    if block.splitlines()[0] != 'true':
        raise ValueError('translateModel did not return true')
    for entry in libraries:
        block = stdout.split('BEGIN_VERSION_' + entry['name'] + '\n')[1].split('END_VERSION_' + entry['name'])[0]
        if re.findall(r'^"(.*)"$', block, re.M) != [entry['version'], entry['sourceFile'], '']:
            raise ValueError('Unexpected library resolution: ' + entry['name'])
    tree = ET.parse(directory / 'OxygenCoupled.Cell_init.xml').getroot()
    settings = tree.find('DefaultExperiment').attrib
    for key, value in [('startTime', 0), ('stopTime', 180), ('stepSize', .36), ('tolerance', 1e-6)]:
        if abs(float(settings[key])-value) > 1e-12:
            raise ValueError('Unexpected setting: ' + key)
    variables = {v.attrib['name']: v for v in tree.find('ModelVariables')}
    if float(variables['oxygenOrder'].find('Real').attrib['start']) != 1:
        raise ValueError('Expected oxygenOrder=1')
    grid = {}
    expected = {(1, j, 1) for j in range(1, 11)}
    for layer in ['anFP', 'anGDL', 'anCL', 'PEM', 'caCL', 'caGDL', 'caFP']:
        pattern = re.compile(r'cell\.' + layer + r'\.subregions\[(\d+),(\d+),(\d+)\]')
        indices = {tuple(map(int, match.groups())) for name in variables if (match := pattern.match(name))}
        if indices != expected:
            raise ValueError('Unexpected grid in ' + layer)
        grid[layer] = sorted(indices)
    state_count = int(tree.attrib['numberOfContinuousStates'])
    if state_count != 446:
        raise ValueError(f'Unexpected state count: {state_count}; review model/tool changes')
    info = json.loads((directory / 'OxygenCoupled.Cell_info.json').read_text())
    bindings = []
    for j in range(1, 11):
        q = f"cell.caCL.subregions[1,{j},1].graphite.'e-Transfer'.qO2"
        pressure = f'cell.caCL.subregions[1,{j},1].gas.O2.p'
        equations = [e for e in info['equations'] if q in e.get('defines', []) and e.get('section') == 'regular']
        if not any(pressure in e.get('uses', []) and 'oxygenOrder' in e.get('uses', []) for e in equations):
            raise ValueError('Missing regular live oxygen binding: ' + q)
        bindings.append({'section': j, 'equations': equations})
    result = {'status': 'PASS', 'settings': settings, 'continuousStates': state_count,
              'grid': grid, 'bindings': bindings, 'warnings': warnings}
    write_json(directory / 'translation-audit.json', result, new=True)
    return result


def accept_runtime(directory):
    stdout = (directory / 'simulate-stdout.log').read_text()
    stderr = (directory / 'simulate-stderr.log').read_text()
    if stderr or 'The simulation finished successfully.' not in stdout or 'solver: ida' not in stdout:
        raise ValueError('Runtime did not complete with the qualified IDA recipe')
    if re.search(r'LOG_(ERROR|ASSERT)\s*\|\s*error|\bfatal\b', stdout, re.I):
        raise ValueError('Runtime reported an error')
    blocks = re.findall(r'LOG_ASSERT\s*\| warning \|.*?(?=\nLOG_|\Z)', stdout, re.S)
    allowed_species = {"'e-'", "'H+'", "'C+'", "'SO3-'"}
    for block in blocks:
        species = re.search(r'\.([^.]+)\.p >=', block)
        if not (species and species.group(1) in allowed_species and 'time 0.000000' in block and 'min constraint' in block):
            raise ValueError('Unreviewed runtime assertion warning; inspect logs')
    other = [line for line in stdout.splitlines() if 'warning' in line.lower() and 'LOG_ASSERT' not in line]
    # Reviewed in the original complete-cell run and both relocated attempts:
    # 72 initialization fallbacks; all three MATs have the same SHA-256.
    fallback = re.compile(r'^LOG_STDOUT\s*\| warning \| The default linear solver fails, the fallback solver with total pivoting is started at time 0\.000000\. That might raise performance issues, for more information use -lv LOG_LS\.$')
    unreviewed = [line for line in other if not fallback.fullmatch(line)]
    if unreviewed:
        raise ValueError('Unreviewed runtime warning: ' + unreviewed[0])
    if len(other) not in (0, 72):
        raise ValueError('Unexpected count of initialization linear-solver fallbacks')
    return {'solver': 'ida', 'startupPressureWarnings': len(blocks),
            'initializationLinearSolverFallbacks': len(other),
            'linearSolverFallbackWarnings': other,
            'warningBlocks': blocks, 'scope': 'process completion; numerical acceptance is separate'}
