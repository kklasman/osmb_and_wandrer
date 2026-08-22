import logging_functions
import functools
import datetime

def log_with_timestamp(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger = logging.getLogger(func.__name__)
        logger.info(f"[{timestamp}] Entering {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"[{timestamp}] Exiting {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"[{timestamp}] Exception in {func.__name__}: {e}")
            raise
    return wrapper

# @log_with_timestamp
# def example_function():
#     print("Hello, World!")
#
# example_function()