from .logger_tools import NiceLogger
from .logger_tools import BotLogger

from . import logger_tools
from . import thread_tools

__all__ = logger_tools.__all__ + thread_tools.__all__


__version__ = '0.0.1'
__author__ = 'amiwrpremium'

