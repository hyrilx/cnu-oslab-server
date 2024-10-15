import dataclasses
import os
import threading
from enum import Enum
from pathlib import Path
from threading import Thread
from typing import Dict

import config
import os_helper
from test_framework import TestFramework


class WorkerStatus(Enum):
    submitted = 0
    compiling = 1
    testing = 2
    test_complete = 3
    compile_failed = 4
    run_failed = 5


@dataclasses.dataclass
class WorkerContext(object):
    worker: Thread
    test_framework: TestFramework | None
    path: Path
    user_id: str
    exp_id: int
    status: WorkerStatus
    report: list[str]


worker_map: Dict[str, WorkerContext] = {}

def fill_report(submit_id: str) -> None:
    """
    [EvaluationReport]
      SubmitId: abcdefgh
      Student: 1211001011
      Experiment: 01
      Title: 标题标题
      Details:
        [TestPoint_01] this is brief: PASSED
        [TestPoint_02] this is brief: PASSED
        [TestPoint_03] this is brief: FAILED
          Message: This is provided by scripts.
        [TestPoint_04] this is brief: PASSED
      Summary: 75% PASSED
    """
    worker_context = worker_map[submit_id]

    worker_context.report.append(f'[EvaluationReport]' + os.linesep)
    worker_context.report.append(f'  SubmitId: {submit_id}' + os.linesep)
    worker_context.report.append(f'  Student: {worker_context.user_id}' + os.linesep)
    worker_context.report.append(f'  Experiment: {worker_context.exp_id}' + os.linesep)
    worker_context.report.append(f'  Title: {worker_context.test_framework.get_title()}' + os.linesep)
    worker_context.report.append(f'  Details:' + os.linesep)
    for index, eval_ in enumerate(worker_context.test_framework.run()):
        worker_context.report.append(
            f'    [EvalPoint_{index:02d}] {eval_.brief}: {"PASSED" if eval_.result.is_succeed else "FAILED"}'
            + os.linesep)
        if not eval_.result.is_succeed and eval_.result.error_message:
            worker_context.report.append(
                f'      Message: {eval_.result.error_message}' + os.linesep)
    worker_context.report.append(
        f'  Summary: {worker_context.test_framework.get_pass_count() / len(worker_context.test_framework) * 100}% PASSED' + os.linesep)

def worker_thread(submit_id:str):
    worker_context = worker_map[submit_id]

    worker_context.status = WorkerStatus.compiling
    worker_context.report.append('[COMPILING...]'+ os.linesep)

    if not os_helper.build(worker_context.path):
        worker_context.status = WorkerStatus.compile_failed
        worker_context.report.append('[COMPILE FAILED]'+ os.linesep)
        return


    exe: list[str] = ['python3', 'main.py', 'local', '-s', worker_context.path, 'run']
    worker_context.test_framework = TestFramework(suite_root=Path.cwd() / 'eval_suites',
                                                  suite_id=worker_context.exp_id,
                                                  os_daemon_exe=exe,
                                                  os_daemon_cwd=Path(config.DAEMON_PATH))

    if not worker_context.test_framework.check():
        worker_context.status = WorkerStatus.run_failed
        worker_context.report.append('[RUN FAILED]'+ os.linesep)

    worker_context.status = WorkerStatus.testing
    worker_context.report.append('[TESTING...]' + os.linesep)

    fill_report(submit_id)

    worker_context.status = WorkerStatus.test_complete
    worker_context.report.append('[TEST COMPLETE]'+ os.linesep)


def start_worker(submit_id:str, source_path:Path, user_id:str,exp_id:int) -> None:
    worker_map[submit_id] = WorkerContext(worker=threading.Thread(target=worker_thread, args=(submit_id,)),
                                          test_framework=None,
                                          path=source_path,
                                          user_id=user_id,
                                          exp_id=exp_id,
                                          status=WorkerStatus.submitted,
                                          report=[])
    worker_map[submit_id].worker.start()

def generate_report(submit_id:str):
    worker = worker_map[submit_id]
    index = 0
    while worker.status != WorkerStatus.test_complete or index < len(worker.report):
        if index < len(worker.report):
            yield worker.report[index]
            index += 1
        else:
            import time
            time.sleep(0.005)