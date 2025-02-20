'''
@File: exception_marker.py
@Description: ... ;
@Author: Jerry ;
@Date  : 24/1/25
Version: 1.0.0
Update Record:
-- 24/1/25: initialize version 1.0.0;
'''

import functools
import traceback
import logging
from datetime import datetime,timezone

class UTCFormatter(logging.Formatter):
    converter = datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created, tz=timezone.utc)
        if datefmt:
            time_string = dt.strftime(datefmt)
        else:
            time_string = self.default_msec_format % (dt.strftime(self.default_time_format), record.msecs)
        return time_string

formatter = UTCFormatter(fmt='%(asctime)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.basicConfig(level=logging.ERROR, handlers=[handler])


def exception_marker(is_raise=True, is_log=False, log_level=logging.ERROR,is_test=False):
    if log_level not in [logging.DEBUG,logging.INFO,logging.WARNING,logging.ERROR,logging.CRITICAL]:
        raise ValueError(f"Decorator:db_exception_marker:logLevel doesn't support 'log_level={log_level}'.")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if is_test:
                    print(f"test mode: func is being decorated.")
                return func(*args, **kwargs)
            except Exception as e:

                log_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')

                # exception info
                tb = traceback.format_exc()
                filename = traceback.extract_tb(e.__traceback__)[-1].filename
                line = traceback.extract_tb(e.__traceback__)[-1].lineno


                logging.log(log_level, f"Exception occurred at {log_time}\n"
                                            f"File: {filename}\n"
                                            f"Line: {line}\n"
                                            f"Message: {str(e)}\n"
                                            f"Traceback: {tb}")

                if is_raise:
                    raise

        return wrapper

    return decorator

class exception_marker_class:

    def __init__(self,attr_1, attr_2):
        self.attr_1 = attr_1
        self.attr_2 = attr_2
        '''
        self.is_raise = is_raise
        self.is_log = is_log
        self.log_level = log_level
        '''

    def __call__(self, func):
        #@functools.wraps(func)
        def wrapper(*args, **kwargs):
            # class_attribute = instance.__class__.class_var
            # print(f"Decorator accessed class variable: {class_attribute}")
            result = func(*args,**kwargs)
            return result
        return wrapper

# test
@exception_marker(is_raise=True,log_level=logging.ERROR)
def test_func():
    return 1 / 0  # raise exception



if __name__ == '__main__':
    test_func()