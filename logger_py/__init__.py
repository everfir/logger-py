import logger_py.config as config

# logger
__all__ = [
    "Init", 
    "Fatal", 
    "Error", 
    "Warn", 
    "Info", 
    "Debug", 
    "StartSpan", 
    "Inject"
]

__all__.extend(config.__all__)
