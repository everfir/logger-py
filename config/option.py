from config.log_config import LogConfig, GetConfig
from config.log_config import LOG_LEVEL
from typing import Callable

type Option = Callable[[LogConfig], None]

def WithLogLevel(level: LOG_LEVEL) -> Option: 
    return lambda config: setattr(config, "level", level)

def WithLogFile(file: str) -> Option:
    return lambda config: setattr(config, "log_file", file)

def WithLogFileFormat(format: str) -> Option:
    return lambda config: setattr(config, "log_file_name_format", format)

def WithLogRotation(rotation: bool) -> Option:
    return lambda config: setattr(config, "rotation", rotation)

def WithLogRotationInterval(interval: int) -> Option:
    return lambda config: setattr(config, "rotation_interval", interval)

def WithCaller(enable: bool, keep_level: int = 3) -> Option:
    def handler(config: LogConfig) -> None:
        config.enable_caller = enable
        config.caller_keep_level = keep_level
    return handler


