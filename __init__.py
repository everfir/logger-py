from logger import *
import config


# logger
__all__ = ["Init", "Fatal", "Error", "Warn", "Info", "Debug", "StartSpan", "Inject"]
__all__.extend(config.__all__)