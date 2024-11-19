from typing import Dict
from abc import ABC, abstractmethod

class Logger(ABC):
    @abstractmethod
    def fatal(self, msg: str, **kwargs):
        pass

    @abstractmethod
    def error(self, msg: str, **kwargs):
        pass

    @abstractmethod
    def warn(self, msg: str, **kwargs):
        pass

    @abstractmethod
    def info(self, msg: str, **kwargs):
        pass

    @abstractmethod
    def debug(self, msg: str, **kwargs):
        pass


