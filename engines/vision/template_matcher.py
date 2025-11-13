#!/usr/bin/env python3
"""
👁️ Template Matcher - Поиск шаблонов на экране
Использует OpenCV для поиска изображений
"""

import time
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass

@dataclass
class MatchResult:
    """Результат поиска шаблона"""
    found: bool
    confidence: float
    center_x: int
    center_y: int
    top_left_x: int
    top_left_y: int
    width: int
    height: int
    template_path: str

class TemplateMatcher:
    """
    Класс для поиска шаблонов на экране
    """
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Инициализация Template Matcher
        
        Args:
            templates_dir: Путь к директории с шаблонами
        """
        self.templates_dir = Path(templates_dir)
        
        # Ленивая загрузка OpenCV и PIL
        self.cv2 = None
        self.np = None
        self.PIL_Image = None
        self.pyautogui = None
        
        # Кэш шаблонов
        self.template_cache = {}
        
        # Настройки поиска
        self.default_confidence = 0.8
        self.retina_scale = 1.0
        
        # Настройка логгера
        try:
            from core.logger import get_logger
            self.logger = get_logger("template_matcher")
        except ImportError:
            import logging
            self.logger = logging.getLogger("template_matcher")
        
        # Определяем масштаб Retina дисплея
        self._detect_retina_scale()
        
        self.logger.info("👁️ TemplateMatcher инициализирован")
    
    def _lazy_import_cv2(self):
        """Ленивый импорт OpenCV"""
        if self.cv2 is None:
            try:
                import cv2
                import numpy as np
                self.cv2 = cv2
                self.np = np
                self.logger.debug("📦 OpenCV загружен")
            except ImportError:
                raise ImportError("OpenCV не установлен. Установите: pip install opencv-python")
    
    def _lazy_import_pil(self):
        """Ленивый импорт PIL"""
        if self.PIL_Image is None:
            try:
                from PIL import Image
                self.PIL_Image = Image
                self.logger.debug("📦 PIL загружен")
            except ImportError:
                raise ImportError("PIL не установлен. Установите: pip install Pillow")
    
    def _lazy_import_pyautogui(self):
        """Ленивый импорт PyAutoGUI"""
        if self.pyautogui is None:
            try:
                import pyautogui
                self.pyautogui = pyautogui
                # Отключаем fail-safe для автоматизации
                self.pyautogui.FAILSAFE = False
                self.logger.debug("📦 PyAutoGUI загружен")
            except ImportError:
                raise ImportError("PyAutoGUI не установлен. Установите: pip install pyautogui")
    
    def _detect_retina_scale(self):
        """Определение масштаба Retina дисплея"""
        try:
            self._lazy_import_pyautogui()
            
            # Получаем логическое и физическое разрешение
            screen_size = self.pyautogui.size()
            screenshot = self.pyautogui.screenshot()
            
            if screenshot.width != screen_size.width:
                self.retina_scale = screenshot.width / screen_size.width
                self.logger.info(f"🖥️ Retina дисплей обнаружен (масштаб: {self.retina_scale}x)")
            else:
                self.retina_scale = 1.0
                self.logger.debug("🖥️ Обычный дисплей")
        
        except Exception as e:
            self.logger.warning(f"⚠️ Не удалось определить масштаб дисплея: {e}")
            self.retina_scale = 1.0
    
    def find_template(self, template_name: str, confidence: Optional[float] = None, 
                     timeout: float = 5.0) -> MatchResult:
        """
        Поиск шаблона на экране
        
        Args:
            template_name: Имя шаблона (без расширения)
            confidence: Минимальная уверенность (0.0-1.0)
            timeout: Таймаут поиска в секундах
            
        Returns:
            Результат поиска
        """
        if confidence is None:
            confidence = self.default_confidence
        
        self.logger.debug(f"🔍 Поиск шаблона: {template_name}")
        
        # Загружаем шаблон
        template_path = self._get_template_path(template_name)
        if not template_path:
            return MatchResult(
                found=False, confidence=0.0, center_x=0, center_y=0,
                top_left_x=0, top_left_y=0, width=0, height=0,
                template_path=""
            )
        
        # Загружаем шаблон в память
        template_image = self._load_template(template_path)
        if template_image is None:
            return MatchResult(
                found=False, confidence=0.0, center_x=0, center_y=0,
                top_left_x=0, top_left_y=0, width=0, height=0,
                template_path=str(template_path)
            )
        
        # Поиск с таймаутом
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Делаем скриншот
            screenshot = self._take_screenshot()
            if screenshot is None:
                continue
            
            # Ищем шаблон
            result = self._match_template(screenshot, template_image, confidence)
            
            if result.found:
                self.logger.debug(f"✅ Шаблон найден: {template_name} ({result.confidence:.3f})")
                result.template_path = str(template_path)
                return result
            
            # Небольшая пауза перед следующей попыткой
            time.sleep(0.1)
        
        self.logger.debug(f"❌ Шаблон не найден: {template_name}")
        return MatchResult(
            found=False, confidence=0.0, center_x=0, center_y=0,
            top_left_x=0, top_left_y=0, width=0, height=0,
            template_path=str(template_path)
        )
    
    def _get_template_path(self, template_name: str) -> Optional[Path]:
        """Получение пути к шаблону"""
        # Проверяем различные варианты имени
        possible_names = [
            f"{template_name}.png",
            f"{template_name}.jpg",
            f"{template_name}.jpeg"
        ]
        
        # Ищем в основной директории
        for name in possible_names:
            template_path = self.templates_dir / name
            if template_path.exists():
                return template_path
        
        # Ищем рекурсивно
        for ext in ['.png', '.jpg', '.jpeg']:
            for template_path in self.templates_dir.rglob(f"*{template_name}*{ext}"):
                return template_path
        
        self.logger.warning(f"⚠️ Шаблон не найден: {template_name}")
        return None
    
    def _load_template(self, template_path: Path) -> Optional[Any]:
        """Загрузка шаблона в память"""
        try:
            self._lazy_import_cv2()
            
            # Проверяем кэш
            cache_key = str(template_path)
            if cache_key in self.template_cache:
                return self.template_cache[cache_key]
            
            # Загружаем изображение
            template = self.cv2.imread(str(template_path))
            if template is None:
                self.logger.error(f"❌ Не удалось загрузить шаблон: {template_path}")
                return None
            
            # Масштабируем для Retina дисплеев
            if self.retina_scale != 1.0:
                new_width = int(template.shape[1] * self.retina_scale)
                new_height = int(template.shape[0] * self.retina_scale)
                template = self.cv2.resize(template, (new_width, new_height))
            
            # Сохраняем в кэш
            self.template_cache[cache_key] = template
            
            return template
        
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки шаблона {template_path}: {e}")
            return None
    
    def _take_screenshot(self) -> Optional[Any]:
        """Создание скриншота экрана"""
        try:
            self._lazy_import_pyautogui()
            self._lazy_import_cv2()
            
            # Делаем скриншот
            screenshot_pil = self.pyautogui.screenshot()
            
            # Конвертируем PIL -> OpenCV
            screenshot_np = self.np.array(screenshot_pil)
            screenshot_cv = self.cv2.cvtColor(screenshot_np, self.cv2.COLOR_RGB2BGR)
            
            return screenshot_cv
        
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания скриншота: {e}")
            return None
    
    def _match_template(self, screenshot: Any, template: Any, confidence: float) -> MatchResult:
        """Поиск шаблона на скриншоте"""
        try:
            self._lazy_import_cv2()
            
            # Выполняем template matching
            result = self.cv2.matchTemplate(screenshot, template, self.cv2.TM_CCOEFF_NORMED)
            
            # Находим лучшее совпадение
            min_val, max_val, min_loc, max_loc = self.cv2.minMaxLoc(result)
            
            # Проверяем уверенность
            if max_val >= confidence:
                # Вычисляем координаты
                template_height, template_width = template.shape[:2]
                
                top_left_x, top_left_y = max_loc
                center_x = top_left_x + template_width // 2
                center_y = top_left_y + template_height // 2
                
                # Корректируем координаты для Retina дисплеев
                if self.retina_scale != 1.0:
                    center_x = int(center_x / self.retina_scale)
                    center_y = int(center_y / self.retina_scale)
                    top_left_x = int(top_left_x / self.retina_scale)
                    top_left_y = int(top_left_y / self.retina_scale)
                    template_width = int(template_width / self.retina_scale)
                    template_height = int(template_height / self.retina_scale)
                
                return MatchResult(
                    found=True,
                    confidence=max_val,
                    center_x=center_x,
                    center_y=center_y,
                    top_left_x=top_left_x,
                    top_left_y=top_left_y,
                    width=template_width,
                    height=template_height,
                    template_path=""
                )
            else:
                return MatchResult(
                    found=False, confidence=max_val, center_x=0, center_y=0,
                    top_left_x=0, top_left_y=0, width=0, height=0,
                    template_path=""
                )
        
        except Exception as e:
            self.logger.error(f"❌ Ошибка поиска шаблона: {e}")
            return MatchResult(
                found=False, confidence=0.0, center_x=0, center_y=0,
                top_left_x=0, top_left_y=0, width=0, height=0,
                template_path=""
            )
    
    def click_template(self, template_name: str, confidence: Optional[float] = None,
                      timeout: float = 5.0) -> bool:
        """
        Поиск и клик по шаблону
        
        Args:
            template_name: Имя шаблона
            confidence: Минимальная уверенность
            timeout: Таймаут поиска
            
        Returns:
            True если клик выполнен успешно
        """
        result = self.find_template(template_name, confidence, timeout)
        
        if result.found:
            try:
                self._lazy_import_pyautogui()
                self.pyautogui.click(result.center_x, result.center_y)
                self.logger.info(f"🖱️ Клик по шаблону {template_name} ({result.center_x}, {result.center_y})")
                return True
            except Exception as e:
                self.logger.error(f"❌ Ошибка клика по шаблону: {e}")
                return False
        else:
            self.logger.warning(f"⚠️ Не удалось найти шаблон для клика: {template_name}")
            return False
    
    def wait_for_template(self, template_name: str, confidence: Optional[float] = None,
                         timeout: float = 10.0) -> bool:
        """
        Ожидание появления шаблона
        
        Args:
            template_name: Имя шаблона
            confidence: Минимальная уверенность
            timeout: Таймаут ожидания
            
        Returns:
            True если шаблон появился
        """
        result = self.find_template(template_name, confidence, timeout)
        return result.found
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Получение информации о шаблоне"""
        template_path = self._get_template_path(template_name)
        
        if not template_path:
            return {"exists": False}
        
        try:
            self._lazy_import_pil()
            
            with self.PIL_Image.open(template_path) as img:
                return {
                    "exists": True,
                    "path": str(template_path),
                    "size": img.size,
                    "format": img.format,
                    "mode": img.mode
                }
        except Exception as e:
            return {"exists": False, "error": str(e)}

# Пример использования
if __name__ == "__main__":
    matcher = TemplateMatcher()
    
    print("🧪 Тестирование TemplateMatcher")
    print("=" * 50)
    
    # Тест поиска шаблона (если есть)
    test_template = "ChromeNewTab"
    
    print(f"🔍 Поиск шаблона: {test_template}")
    result = matcher.find_template(test_template, timeout=1.0)
    
    if result.found:
        print(f"✅ Шаблон найден!")
        print(f"   📍 Координаты: ({result.center_x}, {result.center_y})")
        print(f"   🎯 Уверенность: {result.confidence:.3f}")
    else:
        print(f"❌ Шаблон не найден")
    
    # Информация о шаблоне
    info = matcher.get_template_info(test_template)
    print(f"📋 Информация о шаблоне: {info}")
    
    print("\n👁️ TemplateMatcher готов к работе!")
