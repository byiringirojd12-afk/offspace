import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const outputDirectory = path.join(root, 'src-tauri', 'binaries');
const outputExecutable = path.join(outputDirectory, 'offspace-backend.exe');

if (process.platform !== 'win32') {
  throw new Error('The OFFSPACE Windows backend sidecar must be built on Windows.');
}

function probePython(executable, prefixArguments = []) {
  const result = spawnSync(
    executable,
    [...prefixArguments, '-c', 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'],
    { cwd: root, encoding: 'utf8', windowsHide: true },
  );
  return result.status === 0 && result.stdout.trim() === '3.12';
}

let python = process.env.OFFSPACE_PYTHON;
let pythonArguments = [];
if (python) {
  if (!probePython(python)) {
    throw new Error('OFFSPACE_PYTHON must point to a working Python 3.12 interpreter.');
  }
} else if (probePython('py', ['-3.12'])) {
  python = 'py';
  pythonArguments = ['-3.12'];
} else {
  throw new Error(
    'Python 3.12 was not found. Set OFFSPACE_PYTHON to a Python 3.12 executable.',
  );
}

const packagingCheck = spawnSync(
  python,
  [...pythonArguments, '-c', 'import PyInstaller'],
  { cwd: root, encoding: 'utf8', windowsHide: true },
);
if (packagingCheck.status !== 0) {
  throw new Error(
    'PyInstaller is missing from the Python 3.12 environment. Install requirements.txt and requirements-packaging.txt there.',
  );
}

fs.mkdirSync(outputDirectory, { recursive: true });
const workDirectory = path.join(os.tmpdir(), 'offspace-pyinstaller-work');
const specDirectory = path.join(os.tmpdir(), 'offspace-pyinstaller-spec');
const build = spawnSync(
  python,
  [
    ...pythonArguments,
    '-m',
    'PyInstaller',
    '--clean',
    '--noconfirm',
    '--onefile',
    '--name',
    'offspace-backend',
    '--paths',
    root,
    '--collect-all',
    'uvicorn',
    '--collect-submodules',
    'sqlalchemy.dialects.sqlite',
    '--distpath',
    outputDirectory,
    '--workpath',
    workDirectory,
    '--specpath',
    specDirectory,
    path.join(root, 'scripts', 'backend_entry.py'),
  ],
  { cwd: root, stdio: 'inherit', windowsHide: true },
);

if (build.status !== 0 || !fs.existsSync(outputExecutable)) {
  throw new Error('PyInstaller did not produce the OFFSPACE backend executable.');
}

console.log(`Built backend sidecar: ${outputExecutable}`);
