"""
🚀 Macro-Assistant Core
Ядро системы автоматизации с AI модулями
"""

__version__ = "1.0.0"
__author__ = "Macro-Assistant Team"

from .config import Config
from .logger import get_logger
from .ai_router import AIRouter
from .context_manager import ContextManager

__all__ = [
    "Config",
    "get_logger", 
    "AIRouter",
    "ContextManager"
]
