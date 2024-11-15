import inspect
import logging
import structlog    


from mylogger import Logger
from config.log_config import LogConfig
from logging.handlers import TimedRotatingFileHandler  # 导入时间滚动处理器


class MyStructlogger(Logger):
    def __init__(self, config: LogConfig): 
        processors = [
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt='iso'),  # 添加时间戳
            structlog.processors.StackInfoRenderer(),  # 添加堆栈信息
        ]

        if config.enable_caller:
            processors.append(callerProcessor(config.caller_keep_level))
        processors.append(structlog.processors.JSONRenderer(ensure_ascii=False)) # 以json格式输出


        # 配置 structlog
        structlog.configure(
            processors=processors,  # 动态填充的处理器列表
        )
        
        # 配置日志处理器，支持按小时滚动
        log_handler = TimedRotatingFileHandler(
            'app.log',  # 日志文件名
            when='h',  # 每小时滚动
            interval=1,  # 每小时滚动一次
            backupCount=168  # 默认保留最近 168 个备份
        )

        logging.basicConfig(
            level=logging._nameToLevel[config.level],   # 日志截断
            handlers=[log_handler] # 日志滚动
        )   
        self.logger = structlog.getLogger()
        pass

    def Fatal(self, msg: str, **kwargs):
        self.logger.critical(msg, **kwargs, stack_info=True)
        pass

    def Error(self, msg: str, **kwargs):
        self.logger.error(msg, **kwargs)    
        pass

    def Warn(self, msg: str, **kwargs):
        self.logger.warn(msg, **kwargs)
        pass

    def Info(self, msg: str, **kwargs):
        self.logger.info(msg, **kwargs)
        pass

    def Debug(self, msg: str, **kwargs):
        self.logger.debug(msg, **kwargs)   
        pass
    pass


class callerProcessor():
    def __init__(self, level: int):
        self.level = level # 设置保留的路径级别
        pass

    def __call__(self, logger, name, event_dict) -> dict:
        event_dict['caller'] = self.get_caller()
        return event_dict

    def get_caller(self):
        # 获取当前调用的堆栈信息
        frame = inspect.currentframe()  # 获取当前帧
        if frame is None:
            return "unknown"
        caller_frame = frame.f_back  # 获取上一个帧（调用者）
        if caller_frame is None:
            return "unknown"

        # 获取文件名和行号
        filename = caller_frame.f_code.co_filename  # 获取文件名
        lineno = caller_frame.f_lineno  # 获取行号

        if self.level > 0:
            # 处理保留的路径级别
            path_parts = filename.split('/')  # 根据路径分隔符分割文件路径
            if self.level < len(path_parts):
                filename = '/'.join(path_parts[-self.level:])  # 保留 N 级路径

        return f"{filename}:{lineno}"  # 返回格式化的调用者信息