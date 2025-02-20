import threading
import typing
from typing import Any, Callable, get_type_hints, List
import inspect
from functools import wraps
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
class Global_Variable_Manager():
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_global_variable"):
            self._global_variable = {}

    def get(self,variable_name:str):
        return self._global_variable.get(variable_name,None)

    def add(self,variable_name:str,variable_value:Any):
        self._global_variable[variable_name] = variable_value

    def delete(self,variable_name:str):
        self._global_variable.pop(variable_name)


class Type_Check_Wrapper:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def is_check_signature_type(self):
        try:

            func_signature = inspect.signature(self.func)
            bound_args = func_signature.bind(*self.args, **self.kwargs)
            bound_args.apply_defaults()
            annotations = self.func.__annotations__

            parameters = list(func_signature.parameters.keys())
            if 'self' in parameters:
                parameters.remove('self')

            if "cls" in parameters:
                parameters.remove("cls")

            for param_name in parameters:
                if param_name in annotations:
                    expected_type = annotations[param_name]
                    actual_value = bound_args.arguments[param_name]
                    if not self._check_type(actual_value, expected_type):
                        raise TypeError(f"Argument '{param_name}' must be of type {expected_type}, "
                                        f"receive an unexpected argument: {actual_value}.")

            result = self.func(*self.args, **self.kwargs)
            print(f"result = {result}")
            # print("Type check passed.")
            return result

        except Exception as e:
            print(f"Type check failed: {e}")
            return e

    def _check_type(self, value, expected_type):
        if isinstance(expected_type, typing._GenericAlias):
            origin_type = typing.get_origin(expected_type)
            args_types = typing.get_args(expected_type)
            if not isinstance(value, origin_type):
                return False
            if args_types:
                return all(self._check_type(v, args_types[0]) for v in value)
        else:
            return isinstance(value, expected_type)


def check_signature_type(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if any(hasattr(arg, 'is_check_signature_type') for arg in args):
            return Type_Check_Wrapper(func, *args, **kwargs)
        return func(*args, **kwargs)
    return wrapper

@check_signature_type
def test_func(name:str, item:List[int]) -> str:
    print(name)
    print(item)
    return name



if __name__ == '__main__':
    print(PROJECT_ROOT)