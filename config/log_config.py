import os
from config.tracer_config import TracerConfig

# 日志等级
type LOG_LEVEL = str
DEBUG: LOG_LEVEL = "DEBUG"
INFO: LOG_LEVEL = "INFO"
WARN: LOG_LEVEL = "WARN"
ERROR: LOG_LEVEL = "ERROR"
FATAL: LOG_LEVEL = "FATAL"


class LogConfig(object):
    
    def __init__(self):
        self.level: LOG_LEVEL = INFO # 日志等级

        # 日志输出配置
        self.log_file: str = "logs/app.log"   # 日志输出路径
        self.rotation: bool = True
        self.compress: bool = False # 日志压缩
        self.rotation_interval: int = 1 # 轮动时间间隔, 单位:小时

        # 日志内容
        self.enable_caller: bool = True # 是否输出调用者信息
        self.caller_keep_level: int = 3 # 调用者信息保留的层级


        # TODO：链路追踪
        self.tracer_config: TracerConfig = TracerConfig()
        pass
    
    pass



_globalConfig = LogConfig()


def GetConfig() -> LogConfig:
    return _globalConfig
