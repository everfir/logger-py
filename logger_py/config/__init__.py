from logger_py.config.option import *
from logger_py.config.log_config import *




__all__.extend(["GetConfig"])   # 日志配置获取
__all__.extend(["DEBUG", "INFO", "WARN", "ERROR", "FATAL"]) # 日志等级
__all__.extend([
    "WithLogLevel", 
    "WithLogFile", 
    "WithLogRotation", 
    "WithLogRotationInterval", 
    "WithCaller", 
    "WithTracer"
]) # 日志配置选项
