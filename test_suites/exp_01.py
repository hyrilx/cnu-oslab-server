from os_daemon import OsDaemon
from test_util import TestResult,test_case

@test_case('echo test 01 with 1234 which should success')
def echo_test_01(osd: OsDaemon) -> TestResult:
    text = '1234'
    res = osd.exec(f'echo {text}', 5)
    if not res.time_spent:
        return TestResult(False, 'Timeout')
    if len(res.stdout) != 1 or res.stdout[0] != text:
        return TestResult(False, f'Output mismatch {res.stdout}')
    return TestResult(True)

@test_case('echo test 02 with 5678 which should timeout')
def echo_test_02(osd: OsDaemon) -> TestResult:
    text = '5678'
    res = osd.exec(f'echo {text}', 0)
    if not res.time_spent:
        return TestResult(False, 'Timeout')
    if len(res.stdout) != 1 or res.stdout[0] != text:
        return TestResult(False, f'Output mismatch {res.stdout}')

    return TestResult(True)


@test_case('echo test 03 with 2333 which should mismatch')
def echo_test_03(osd: OsDaemon) -> TestResult:
    text = '2333'
    res = osd.exec(f'echo {text}', 5)
    if not res.time_spent:
        return TestResult(False, 'Timeout')
    if len(res.stdout) != 1 or res.stdout[0] != 3444:
        return TestResult(False, f'Output mismatch {res.stdout}')

    return TestResult(True)


@test_case('echo test 01 with 7890 which should success')
def echo_test_04(osd: OsDaemon) -> TestResult:
    text = '7890'
    res = osd.exec(f'echo {text}', 5)
    if not res.time_spent:
        return TestResult(False, 'Timeout')
    if len(res.stdout) != 1 or res.stdout[0] != text:
        return TestResult(False, f'Output mismatch {res.stdout}')

    return TestResult(True)
