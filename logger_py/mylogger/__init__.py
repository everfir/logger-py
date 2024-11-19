from logger_py.mylogger.abstract import Logger
from logger_py.config.log_config import LogConfig
from logger_py.mylogger.my_structlog import MyStructlogger



__all__ = ["Logger"]
__all__.extend(["MyStructlogger"])
__all__.extend(["NewLogger"])

def NewLogger(config: LogConfig) -> Logger:
    return MyStructlogger(config=config)