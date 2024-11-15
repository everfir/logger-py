from typing import Dict
from abc import ABC, abstractmethod

class Logger(ABC):
    @abstractmethod
    def Fatal(self, msg: str, **kwargs):
        pass

    @abstractmethod
    def Error(self, msg: str, **kwargs):
        pass

    @abstractmethod
    def Warn(self, msg: str, **kwargs):
        pass

    @abstractmethod
    def Info(self, msg: str, **kwargs):
        pass

    @abstractmethod
    def Debug(self, msg: str, **kwargs):
        pass


