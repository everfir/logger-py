from typing import List, Tuple, Optional

from logger_py.mytracer.tracer import Tracer
from logger_py.mylogger import Logger, NewLogger
from logger_py.config.log_config import LogConfig
from logger_py.config import option as option, GetConfig, ERROR

from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.trace.span import Span


class myLogger(Logger):
    def __init__(self, options: List[option.Option] = []):
        self.config: LogConfig = GetConfig()
        for option in options:
            option(self.config)

        self.logger = NewLogger(self.config)
        self.tracer = Tracer(self.config.tracer_config)
        pass

    def init(self) -> Optional[Exception]:
        return self.tracer.init()

    def fatal(self, ctx: dict, msg: str, **kwargs):
        kwargs["ctx"] = ctx
        return self.logger.fatal(msg, **kwargs)

    def error(self, ctx: dict, msg: str, **kwargs):
        kwargs["ctx"] = ctx
        return self.logger.error(msg, **kwargs)

    def warn(self, ctx: dict, msg: str, **kwargs):
        kwargs["ctx"] = ctx
        return self.logger.warn(msg, **kwargs)

    def info(self, ctx: dict, msg: str, **kwargs):
        kwargs["ctx"] = ctx
        return self.logger.info(msg, **kwargs)

    def debug(self, ctx: dict, msg: str, **kwargs):
        kwargs["ctx"] = ctx
        return self.logger.debug(msg, **kwargs)

    pass


def Init(opts: List[option.Option] = []) -> None:
    global _myLogger

    _myLogger = myLogger(opts)
    _myLogger.init()
    pass


# 导出接口
def Fatal(ctx: dict, msg: str, **kwargs):
    _myLogger.fatal(ctx=ctx, msg=msg, **kwargs)
    return


def Error(ctx: dict, msg: str, **kwargs):
    _myLogger.error(ctx=ctx, msg=msg, **kwargs)
    return


def Warn(ctx: dict, msg: str, **kwargs):
    _myLogger.warn(ctx=ctx, msg=msg, **kwargs)
    return


def Info(ctx: dict, msg: str, **kwargs):
    _myLogger.info(ctx=ctx, msg=msg, **kwargs)
    return


def Debug(ctx: dict, msg: str, **kwargs):
    _myLogger.debug(ctx=ctx, msg=msg, **kwargs)
    return


def StartSpan(ctx: dict, name: str) -> Tuple[dict, Span]:
    return _myLogger.tracer.start_span(ctx=ctx, name=name)


def Inject(ctx: dict, carrier: dict) -> None:
    return _myLogger.tracer.inject(ctx=ctx, carrier=carrier)


def Extract(ctx: dict, carrier: dict) -> Optional[dict]:
    return _myLogger.tracer.extract(ctx=ctx, carrier=carrier)


def WrapHeader(ctx: dict, header: dict) -> dict:
    if not ctx:
        return header

    Inject(ctx=ctx, carrier=header)
    return header


_myLogger = myLogger()  # 默认配置
if e := _myLogger.init():
    Error({}, msg="logger-py init error", error=e)
    raise e

# 测试样例
if __name__ == "__main__":
    # not necessary to call this function
    Init(
        [
            option.WithCaller(enable=True, keep_level=2),
            option.WithLogLevel(level=ERROR),
        ]
    )

    # Fatal({}, "fatal test", 测试字段="sss", 测试=2)
    Error({}, "error test", 测试字段="sss", 测试=2)
    Warn({}, "warn test", 测试字段="sss", 测试=2)
    Info({}, "info test", 测试字段="sss", 测试=2)
    Debug({}, "debug test", 测试字段="sss", 测试=2)
