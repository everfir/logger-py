import config.option as option
from config.log_config import *




__all__ = ["option"]

__all__.extend(["GetConfig"])   # 日志配置获取
__all__.extend(["DEBUG", "INFO", "WARN", "ERROR", "FATAL"]) # 日志等级


a = None
if not a:
    a = 1
print(a)