import inspect  # 用于获取调用栈信息
import logging  # Python标准日志库
import os  # 用于文件和目录操作

from logger_py.mylogger import Logger  # 导入基础日志接口
from logger_py.config.log_config import LogConfig  # 导入日志配置类
from opentelemetry import trace
from opentelemetry.context import Context

import structlog  # 结构化日志库
from logging.handlers import TimedRotatingFileHandler  # 用于实现日志文件按时间滚动


def process_ctx_fields(logger, method_name, event_dict):
    """处理 ctx 字段的处理器"""
    if "ctx" not in event_dict:
        return event_dict

    ctx = event_dict["ctx"]
    del event_dict["ctx"]

    span = trace.get_current_span(Context(ctx))
    if not span:
        return event_dict

    span_context = span.get_span_context()
    if not span_context.is_valid:
        return event_dict

    event_dict["span_id"] = span_context.span_id
    event_dict["trace_id"] = span_context.trace_id

    # 处理所有以 x-everfir- 开头的字段
    for key, value in ctx.items():
        if key.startswith("x-everfir-"):
            # 移除 x-everfir- 前缀
            new_key = key.replace("x-everfir-", "")
            
            if isinstance(value, str):
                # 如果是字符串，直接添加到 event_dict
                event_dict[new_key] = value
            else:
                # 如果是结构体，尝试获取其实际值
                try:
                    # 尝试将对象转换为字典
                    if hasattr(value, "dict"):
                        value_dict = value.dict()
                    elif hasattr(value, "__dict__"):
                        value_dict = value.__dict__
                    else:
                        continue
                        
                    # 将字典中的所有值添加到 event_dict
                    for attr_name, attr_value in value_dict.items():
                        if not attr_name.startswith("_"):
                            event_dict[f"{attr_name}"] = attr_value
                except Exception:
                    continue

    return event_dict


class MyStructlogger(Logger):
    """
    结构化日志记录器类，继承自基础Logger类
    实现了结构化日志输出，支持控制台和文件两种输出方式
    """

    def __init__(self, config: LogConfig):
        """
        初始化日志记录器
        Args:
            config: LogConfig对象，包含日志配置信息
        """
        # 创建日志处理器列表
        log_handlers = []

        # 配置控制台日志处理器
        console_handler = logging.StreamHandler()  # 创建控制台输出处理器
        console_handler.setFormatter(
            logging.Formatter("%(message)s")
        )  # 设置日志格式为纯消息
        log_handlers.append(console_handler)

        # 如果配置了日志文件，则配置文件日志处理器
        if config.log_file:
            # 确保日志目录存在
            log_dir = os.path.dirname(config.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # 配置按时间滚动的文件处理器
            file_handler = TimedRotatingFileHandler(
                config.log_file,  # 日志文件路径
                when="H",  # 按小时滚动
                interval=1,  # 每1小时滚动一次
                backupCount=168,  # 保留最近168个文件（7天）
                encoding="utf-8",  # 使用UTF-8编码
            )
            # 自定义日志文件滚动后缀格式：年-月-日-时
            file_handler.suffix = "%Y-%m-%d-%H"
            file_handler.setFormatter(logging.Formatter("%(message)s"))
            log_handlers.append(file_handler)

        # 配置基础日志系统
        logging.basicConfig(
            level=logging._nameToLevel[config.level],  # 设置日志级别
            handlers=log_handlers,  # 设置处理器
            force=True,  # 强制重新配置，确保配置生效
        )

        # 配置结构化日志处理器链
        processors = [
            structlog.stdlib.filter_by_level,  # 根据级别过滤日志
            process_ctx_fields,  # 处理 ctx 中的字段
            structlog.processors.add_log_level,  # 添加日志级别字段
            structlog.processors.TimeStamper(fmt="iso"),  # 添加ISO格式时间戳
            structlog.processors.StackInfoRenderer(),  # 添加堆栈信息
        ]

        # 如果启用了调用者信息，添加调用者处理器
        if config.enable_caller:
            processors.append(callerProcessor(config.caller_keep_level))

        # 添加其他必要的处理器
        processors.extend(
            [
                structlog.processors.format_exc_info,  # 格式化异常信息
                structlog.stdlib.PositionalArgumentsFormatter(),  # 处理位置参数
                structlog.processors.UnicodeDecoder(),  # 确保正确的字符编码
                structlog.processors.JSONRenderer(
                    ensure_ascii=False
                ),  # JSON格式化，支持中文
            ]
        )

        # 配置structlog
        structlog.configure(
            processors=processors,  # 设置处理器链
            context_class=dict,  # 使用字典作为上下文类
            logger_factory=structlog.stdlib.LoggerFactory(),  # 使用标准日志工厂
            wrapper_class=structlog.stdlib.BoundLogger,  # 使用绑定日志器
            cache_logger_on_first_use=True,  # 缓存日志器以提高性能
        )

        # 获取配置好的日志器实例
        self.logger = structlog.get_logger()

    # 实现各个日志级别的方法
    def fatal(self, msg: str, **kwargs):
        """
        记录致命级别日志，自动添加堆栈信息
        """
        self.logger.critical(msg, **kwargs, stack_info=True)

    def error(self, msg: str, **kwargs):
        """
        记录错误级别日志
        """
        self.logger.error(msg, **kwargs)

    def warn(self, msg: str, **kwargs):
        """
        记录警告级别日志
        """
        self.logger.warn(msg, **kwargs)

    def info(self, msg: str, **kwargs):
        """
        记录信息级别日志
        """
        self.logger.info(msg, **kwargs)

    def debug(self, msg: str, **kwargs):
        """
        记录调试级别日志
        """
        self.logger.debug(msg, **kwargs)


class callerProcessor:
    """
    调用者信息处理器
    用于在日志中添加调用位置信息（文件名:行号）
    """

    def __init__(self, level: int):
        """
        初始化处理器
        Args:
            level: 保留的路径层级数
        """
        self.level = level  # 设置保留的路径级别

    def __call__(self, logger, name, event_dict) -> dict:
        """
        处理器调用方法，添加调用者信息到日志事件字典
        """
        event_dict["caller"] = self.get_caller()
        return event_dict

    def get_caller(self):
        """
        获取调用者信息
        Returns:
            str: 格式化的调用者信息（文件名:行号）
        """
        # 获取当前调用栈帧
        frame = inspect.currentframe()
        if frame is None:
            return "unknown"

        # 跳过库内部的调用栈
        while frame and (
            "logger_py" in frame.f_code.co_filename
            or "structlog" in frame.f_code.co_filename
            or "logging" in frame.f_code.co_filename
        ):
            frame = frame.f_back

        if frame is None:
            return "unknown"

        # 获取文件名和行号
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno

        # 如果设置了路径保留级别，处理文件路径
        if self.level > 0:
            path_parts = filename.split("/")  # 分割路径
            if self.level < len(path_parts):
                filename = "/".join(path_parts[-self.level :])  # 只保留指定层级的路径

        return f"{filename}:{lineno}"  # 返回"文件名:行号"格式的调用者信息
