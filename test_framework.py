import importlib.util
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Generator

from os_daemon import OsDaemon
from test_util import is_test_case, TestCase, TestResult

@dataclass
class TestInfo:
    test_brief: str
    test_result:TestResult

def load_module(module_path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location('test_suite', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class TestFramework(object):
    def __init__(self, suite_root: Path, suite_id: int, os_daemon_exe: list[str], os_daemon_cwd:Path) -> None:
        path = suite_root / f'exp_{suite_id:02d}.py'
        if not path.exists():
            raise RuntimeError()

        self.module = load_module(path)
        self.os_daemon_exe = os_daemon_exe
        self.os_daemon_cwd = os_daemon_cwd
        self.pass_count = 0


    def __len__(self) -> int:
        return sum(1
                   for obj
                   in vars(self.module).values()
                   if is_test_case(obj))

    def get_test_suite(self) -> Generator[TestCase,None,None]:
        yield from (TestCase(obj, obj.test_case_brief)
                    for obj
                    in vars(self.module).values()
                    if is_test_case(obj))

    def run(self)->Generator[TestInfo,None,None]:
        self.pass_count = 0
        for case in self.get_test_suite():
            osd = OsDaemon(exe = self.os_daemon_exe,cwd = self.os_daemon_cwd)
            result = case.func(osd)
            if result.is_succeed:
                self.pass_count += 1
            yield TestInfo(case.brief,result)

    def check(self) -> bool:
        try:
            _ = OsDaemon(exe=self.os_daemon_exe, cwd=self.os_daemon_cwd)
        except RuntimeError:
            return False

        return True

    def get_pass_count(self) -> int:
        return self.pass_count

