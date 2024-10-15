from dataclasses import dataclass
from pathlib import Path
from subprocess import Popen, PIPE
import fcntl, os
import time
from typing import Any, Mapping


@dataclass
class ExecResult:
    time_spent: float | None
    stdout: list[str]


@dataclass
class RecvResult:
    time_spent: float | None
    stdout: str

class OsDaemon(object):
    def __init__(self, exe: list[str], cwd:Path = Path.cwd(), timeout: float | None = 8.) -> None:
        self.process = Popen(exe, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=cwd)

        flags = fcntl.fcntl(self.process.stdout, fcntl.F_GETFL)
        fcntl.fcntl(self.process.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)

        result = self.exec(timeout=timeout)
        if not result.time_spent:
            raise RuntimeError('Daemon not responding')
        self.welcome = result.stdout

    def __del__(self) -> None:
        self._stop()

    def _send(self, data: str) -> None:
        self.process.stdin.write((data + os.linesep).encode('utf-8'))
        self.process.stdin.flush()

    def _recv(self, timeout: float | None = None) -> RecvResult:
        start_time = time.time()
        buffer = ''
        while True:
            elapsed_time: float = time.time() - start_time
            if timeout is not None and elapsed_time >= timeout:
                return RecvResult(None, buffer)

            chunk = self.process.stdout.read()
            if not chunk:
                continue

            chunk = chunk.decode()
            buffer += chunk
            if chunk.split(os.linesep)[-1].strip() == '$':
                return RecvResult(elapsed_time, buffer)

            time.sleep(.005)

    def _stop(self) -> None:
        self._send('\001x')

    def get_welcome(self) -> list[str]:
        return self.welcome

    def exec(self, data: str | None = None, timeout: float | None = None) -> ExecResult:
        if data:
            self._send(data)
        res = self._recv(timeout)

        return ExecResult(res.time_spent, [_line.strip() for _line in res.stdout.split(os.linesep)[1:-1]])
