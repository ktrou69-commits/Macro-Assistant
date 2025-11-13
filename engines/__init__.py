"""
🚀 Engines - Движки выполнения для Macro-Assistant
Парсинг, выполнение и автоматизация
"""

__version__ = "1.0.0"

from .dsl.atlas_parser import AtlasParser
from .dsl.atlas_executor import AtlasExecutor
from .vision.template_matcher import TemplateMatcher

__all__ = [
    "AtlasParser",
    "AtlasExecutor", 
    "TemplateMatcher"
]
