import subprocess
from pathlib import Path

import config


def detect(source: Path) -> bool:
    exe = ['python3', 'main.py', 'local', '-s', str(source), 'detect']
    result = subprocess.run(
        exe,
        cwd=config.DAEMON_PATH,
        capture_output=True,
        text=True
    )
    return result.stdout and 'Kernel detected' in result.stdout


def build(source: Path) -> bool:
    exe = ['python3', 'main.py', 'local', '-s', str(source), 'build']
    subprocess.run(exe,
                   cwd=config.DAEMON_PATH,
                   capture_output=True,
                   text=True)

    return detect(source)
