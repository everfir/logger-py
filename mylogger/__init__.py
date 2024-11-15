from mylogger.abstract import *
from config.log_config import LogConfig
from mylogger.my_structlog import MyStructlogger



__all__ = ["Logger"]
__all__.extend(["MyStructlogger"])
__all__.extend(["NewLogger"])


def NewLogger(config: LogConfig) -> Logger:
    return MyStructlogger(config=config)