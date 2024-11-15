from curses import ERR
from typing import List, Dict

from mylogger import Logger, NewLogger
from config import option as option, GetConfig, DEBUG, ERROR
# TODO
class myLogger(Logger):
    def __init__(self, options: List[option.Option]=[]):
        self.config = GetConfig()
        for option in options:
            option(self.config)
        self.logger = NewLogger(self.config)
        pass

    def Fatal(self, ctx: Dict[str, object], msg: str, **kwargs):
        return self.logger.Fatal(msg, **kwargs)

    def Error(self, ctx: Dict[str, object], msg: str, **kwargs):
        return self.logger.Error(msg, **kwargs)

    def Warn(self, ctx: Dict[str, object], msg: str, **kwargs):
        return self.logger.Warn(msg, **kwargs)

    def Info(self, ctx: Dict[str, object], msg: str, **kwargs):
        return self.logger.Info(msg, **kwargs) 

    def Debug(self, ctx: Dict[str, object], msg: str, **kwargs):
        return self.logger.Debug(msg, **kwargs)    
    pass


_myLogger = myLogger() # 默认配置
def InitWithOptions(opts: List[option.Option] = []) -> None:
    _myLogger = myLogger(opts)
    return
# 导出接口
def Fatal(ctx: Dict[str, object], msg: str, **kwargs):
    _myLogger.Fatal(ctx, msg, **kwargs)
    return

def Error(ctx: Dict[str, object], msg: str, **kwargs):
    _myLogger.Error(ctx, msg, **kwargs)
    return  

def Warn(ctx: Dict[str, object], msg: str, **kwargs):
    _myLogger.Warn(ctx, msg, **kwargs)
    return

def Info(ctx: Dict[str, object], msg: str, **kwargs):
    _myLogger.Info(ctx, msg, **kwargs)
    return  

def Debug(ctx: Dict[str, object], msg: str, **kwargs):
    _myLogger.Debug(ctx, msg, **kwargs)
    return  

#测试样例
if __name__ == "__main__":
    # not necessary to call this function
    InitWithOptions([
        option.WithCaller(enable=True, keep_level=2),
        option.WithLogLevel(level=ERROR),
    ])

    Fatal({}, "fatal test", 测试字段="sss", 测试=2) 
    Error({}, "error test", 测试字段="sss", 测试=2)
    Warn({}, "warn test", 测试字段="sss", 测试=2)
    Info({}, "info test", 测试字段="sss", 测试=2)
    Debug({}, "debug test", 测试字段="sss", 测试=2)