from dataclasses import dataclass
from typing import Callable, Any

from os_daemon import OsDaemon


@dataclass
class EvalResult:
    is_succeed: bool
    error_message: str | None = None

    def __post_init__(self) -> None:
        if self.is_succeed and self.error_message:
            raise ValueError("error_message cannot be set when is_succeed is True")
        elif not self.is_succeed and not self.error_message:
            raise ValueError("error_message cannot be set when is_succeed is True")


@dataclass
class EvalCase:
    func: Callable[[OsDaemon], EvalResult]
    brief: str


def eval_case(brief: str):
    def decorator(func: Callable[[OsDaemon], EvalResult]):
        def wrapper(*args, **kwargs):
            from typing import get_type_hints
            hints = get_type_hints(func)
            # 检查参数类型
            if 'osd' not in hints or hints['osd'] != OsDaemon:
                raise TypeError(f"Function {func.__name__} must have a parameter 'osd' of type OsDaemon")
            # 检查返回值类型
            if 'return' not in hints or hints['return'] != EvalResult:
                raise TypeError(f"Function {func.__name__} must return a value of type TestResult")

            return func(*args, **kwargs)

        wrapper.is_eval_case = True
        wrapper.test_eval_brief = brief
        return wrapper

    return decorator


def is_test_case(obj: Any) -> bool:
    return callable(obj) and hasattr(obj, 'is_eval_case') and obj.is_eval_case and hasattr(obj, 'test_eval_brief')
