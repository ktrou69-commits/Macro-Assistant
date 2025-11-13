#!/usr/bin/env python3
"""
simple_executor_enhanced.py
Улучшенный исполнитель .atlas макросов с продвинутым Computer Vision
Основан на архитектуре src/core/macro_sequence.py
"""

import re
import time
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class ExecutionResult:
    """Результат выполнения команды"""
    success: bool
    message: str
    execution_time: float = 0.0

class SimpleExecutorEnhanced:
    """
    Улучшенный исполнитель .atlas макросов
    Включает продвинутый Computer Vision из macro_sequence.py
    """
    
    def __init__(self):
        # Ленивая загрузка библиотек
        self.pyautogui = None
        self.cv2 = None
        self.numpy = None
        
        # Настройки Computer Vision
        self.default_threshold = 0.8  # Повышенный порог для точности
        self.retry_timeout = 10.0     # Время повторных попыток
        self.display_scale = None     # Масштаб дисплея (Retina)
        
        print("⚡ Enhanced SimpleExecutor инициализирован")
    
    def _lazy_import_pyautogui(self):
        """Ленивая загрузка PyAutoGUI"""
        if self.pyautogui is None:
            try:
                import pyautogui
                self.pyautogui = pyautogui
                # Настройки безопасности
                self.pyautogui.FAILSAFE = True
                self.pyautogui.PAUSE = 0.05
                print("📦 PyAutoGUI загружен")
            except ImportError:
                raise ImportError("PyAutoGUI не установлен. Установите: pip install pyautogui")
    
    def _lazy_import_opencv(self):
        """Ленивая загрузка OpenCV"""
        if self.cv2 is None:
            try:
                import cv2
                self.cv2 = cv2
                print("📦 OpenCV загружен")
            except ImportError:
                raise ImportError("OpenCV не установлен. Установите: pip install opencv-python")
    
    def _lazy_import_numpy(self):
        """Ленивая загрузка NumPy"""
        if self.numpy is None:
            try:
                import numpy
                self.numpy = numpy
                print("📦 NumPy загружен")
            except ImportError:
                raise ImportError("NumPy не установлен. Установите: pip install numpy")
    
    def _get_display_scale(self) -> float:
        """Определение масштаба дисплея (Retina)"""
        if self.display_scale is not None:
            return self.display_scale
        
        try:
            self._lazy_import_pyautogui()
            
            screen_size = self.pyautogui.size()
            screenshot = self.pyautogui.screenshot()
            
            # Если физическое разрешение больше логического - это Retina
            if screenshot.width != screen_size.width:
                self.display_scale = screenshot.width / screen_size.width
                print(f"🖥️ Retina Display обнаружен (scale: {self.display_scale}x)")
            else:
                self.display_scale = 1.0
            
            return self.display_scale
        except Exception:
            self.display_scale = 1.0
            return 1.0
    
    def execute_atlas_file(self, file_path: str) -> ExecutionResult:
        """
        Выполнение .atlas файла
        """
        start_time = time.time()
        
        try:
            atlas_path = Path(file_path)
            if not atlas_path.exists():
                return ExecutionResult(
                    False, 
                    f"Файл не найден: {file_path}",
                    time.time() - start_time
                )
            
            print(f"🚀 Выполнение макроса: {atlas_path.name}")
            
            # Читаем и парсим файл
            commands = self._parse_atlas_file(atlas_path)
            print(f"📋 Найдено команд: {len(commands)}")
            
            # Выполняем команды
            for i, command in enumerate(commands, 1):
                print(f"🔧 Команда {i}/{len(commands)}: {command}")
                
                result = self._execute_command(command)
                if not result.success:
                    return ExecutionResult(
                        False,
                        f"Ошибка на команде {i}: {result.message}",
                        time.time() - start_time
                    )
            
            execution_time = time.time() - start_time
            print(f"✅ Выполнено: Макрос выполнен успешно ({len(commands)} команд)")
            print(f"⚡ Время: {execution_time:.3f}с")
            
            return ExecutionResult(
                True,
                f"Макрос выполнен успешно ({len(commands)} команд)",
                execution_time
            )
        
        except Exception as e:
            return ExecutionResult(
                False,
                f"Критическая ошибка: {e}",
                time.time() - start_time
            )
    
    def _parse_atlas_file(self, file_path: Path) -> list:
        """Парсинг .atlas файла"""
        commands = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Пропускаем комментарии и пустые строки
                if not line or line.startswith('#'):
                    continue
                
                commands.append(line)
        
        return commands
    
    def _execute_command(self, command: str) -> ExecutionResult:
        """Выполнение одной команды"""
        try:
            command = command.strip()
            
            if not command:
                return ExecutionResult(True, "Пустая команда")
            
            # Парсим команду
            parts = command.split(' ', 1)
            action = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            # Маршрутизация команд
            if action == 'open':
                return self._execute_open(args)
            elif action == 'click':
                return self._execute_click(args)
            elif action == 'type':
                return self._execute_type(args.strip('"'))
            elif action == 'wait':
                return self._execute_wait(args)
            elif action == 'press':
                return self._execute_press(args)
            elif action == 'hotkey':
                return self._execute_hotkey(args)
            elif action == 'scroll':
                return self._execute_scroll(args)
            else:
                return ExecutionResult(False, f"Неизвестная команда: {action}")
        
        except Exception as e:
            return ExecutionResult(False, f"Ошибка выполнения команды '{command}': {e}")
    
    def _execute_open(self, app_name: str) -> ExecutionResult:
        """Открытие приложения"""
        try:
            # Маппинг имен приложений
            app_mapping = {
                'ChromeApp': 'Google Chrome',
                'Chrome': 'Google Chrome',
                'Calculator': 'Calculator',
                'Finder': 'Finder',
                'Safari': 'Safari',
                'TextEdit': 'TextEdit'
            }
            
            actual_app_name = app_mapping.get(app_name, app_name)
            
            # Используем системную команду open на macOS
            subprocess.run(['open', '-a', actual_app_name], check=True)
            
            print(f"✅ Приложение открыто: {actual_app_name}")
            return ExecutionResult(True, f"Приложение {actual_app_name} открыто")
        
        except subprocess.CalledProcessError as e:
            return ExecutionResult(False, f"Не удалось открыть {app_name}: {e}")
        except Exception as e:
            return ExecutionResult(False, f"Ошибка открытия приложения: {e}")
    
    def _execute_click(self, target: str) -> ExecutionResult:
        """Выполнение клика"""
        try:
            # Проверяем координаты: click (x, y)
            coord_match = re.match(r'\(\s*(\d+)\s*,\s*(\d+)\s*\)', target)
            if coord_match:
                x, y = map(int, coord_match.groups())
                return self._click_coordinates(x, y)
            else:
                # Клик по шаблону с улучшенным CV
                return self._click_template_enhanced(target)
        
        except Exception as e:
            return ExecutionResult(False, f"Ошибка клика: {e}")
    
    def _click_coordinates(self, x: int, y: int) -> ExecutionResult:
        """Клик по координатам"""
        try:
            self._lazy_import_pyautogui()
            
            self.pyautogui.click(x, y)
            print(f"🖱️ Клик по координатам ({x}, {y})")
            return ExecutionResult(True, f"Клик по координатам ({x}, {y})")
        
        except Exception as e:
            return ExecutionResult(False, f"Ошибка клика по координатам: {e}")
    
    def _click_template_enhanced(self, template_name: str) -> ExecutionResult:
        """Улучшенный клик по шаблону с продвинутым Computer Vision"""
        try:
            # Ищем шаблон
            template_path = self._find_template_file(template_name)
            
            if not template_path:
                print(f"⚠️ Шаблон не найден: {template_name}")
                return ExecutionResult(False, f"Шаблон не найден: {template_name}")
            
            # Используем улучшенный поиск с повторными попытками
            found, coords, score = self._find_template_with_retry(template_path)
            
            if found:
                x, y = coords
                self._lazy_import_pyautogui()
                self.pyautogui.click(x, y)
                print(f"✅ Шаблон найден с уверенностью {score:.3f}")
                print(f"🖱️ Клик по шаблону {template_name} в ({x}, {y})")
                return ExecutionResult(True, f"Клик по шаблону {template_name}")
            else:
                print(f"⚠️ Низкая уверенность поиска: {score:.3f}")
                print(f"⚠️ Шаблон не найден на экране: {template_name}")
                return ExecutionResult(False, f"Шаблон не найден на экране: {template_name}")
        
        except Exception as e:
            return ExecutionResult(False, f"Ошибка поиска шаблона: {e}")
    
    def _find_template_file(self, template_name: str) -> Optional[Path]:
        """Поиск файла шаблона"""
        # Возможные имена файлов
        possible_names = [
            f"{template_name}.png",
            f"{template_name}-btn.png",
            f"{template_name}_btn.png"
        ]
        
        # Возможные папки
        possible_dirs = [
            Path("templates"),
            Path("templates/Chrome/ChromeBasicGuiButtons"),
            Path("templates/Chrome/TikTok"),
            Path("templates/Chrome/YouTube")
        ]
        
        # Ищем файл
        for directory in possible_dirs:
            if directory.exists():
                for name in possible_names:
                    template_path = directory / name
                    if template_path.exists():
                        return template_path
        
        return None
    
    def _find_template_with_retry(self, template_path: Path) -> Tuple[bool, Optional[Tuple[int, int]], float]:
        """Улучшенный поиск шаблона с повторными попытками"""
        print(f"🔍 Поиск шаблона (макс. {self.retry_timeout}с, threshold: {self.default_threshold})...")
        start_time = time.time()
        
        last_score = 0.0
        
        while time.time() - start_time < self.retry_timeout:
            found, coords, score = self._find_template_advanced(template_path)
            last_score = score
            
            if found:
                return True, coords, score
            
            time.sleep(0.5)  # Пауза между попытками
        
        return False, None, last_score
    
    def _find_template_advanced(self, template_path: Path) -> Tuple[bool, Optional[Tuple[int, int]], float]:
        """Продвинутый поиск шаблона с обработкой Retina дисплеев"""
        try:
            self._lazy_import_opencv()
            self._lazy_import_numpy()
            self._lazy_import_pyautogui()
            
            # Загружаем шаблон
            template = self.cv2.imread(str(template_path), self.cv2.IMREAD_GRAYSCALE)
            if template is None:
                return False, None, 0.0
            
            # Захват экрана
            screenshot = self.pyautogui.screenshot()
            
            # Конвертируем в OpenCV формат
            frame = self.numpy.array(screenshot)
            frame = self.cv2.cvtColor(frame, self.cv2.COLOR_RGB2BGR)
            gray = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2GRAY)
            
            # Template matching
            res = self.cv2.matchTemplate(gray, template, self.cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = self.cv2.minMaxLoc(res)
            
            if max_val >= self.default_threshold:
                h, w = template.shape
                
                # Вычисляем центр в физическом разрешении
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                
                # Корректируем координаты для pyautogui.click() (логическое разрешение)
                display_scale = self._get_display_scale()
                center_x = int(center_x / display_scale)
                center_y = int(center_y / display_scale)
                
                return True, (center_x, center_y), max_val
            
            return False, None, max_val
        
        except Exception as e:
            print(f"❌ Ошибка продвинутого поиска: {e}")
            return False, None, 0.0
    
    def _execute_type(self, text: str) -> ExecutionResult:
        """Ввод текста"""
        try:
            self._lazy_import_pyautogui()
            
            self.pyautogui.typewrite(text)
            print(f"⌨️ Введен текст: {text}")
            return ExecutionResult(True, f"Введен текст: {text}")
        
        except Exception as e:
            return ExecutionResult(False, f"Ошибка ввода текста: {e}")
    
    def _execute_wait(self, duration: str) -> ExecutionResult:
        """Ожидание"""
        try:
            # Парсим длительность
            if duration.endswith('s'):
                seconds = float(duration[:-1])
            elif duration.endswith('ms'):
                seconds = float(duration[:-2]) / 1000
            else:
                seconds = float(duration)
            
            print(f"⏳ Ожидание {seconds}с...")
            time.sleep(seconds)
            return ExecutionResult(True, f"Ожидание {seconds}с")
        
        except Exception as e:
            return ExecutionResult(False, f"Ошибка ожидания: {e}")
    
    def _execute_press(self, key: str) -> ExecutionResult:
        """Нажатие клавиши"""
        try:
            self._lazy_import_pyautogui()
            
            self.pyautogui.press(key)
            print(f"⌨️ Нажата клавиша: {key}")
            return ExecutionResult(True, f"Нажата клавиша: {key}")
        
        except Exception as e:
            return ExecutionResult(False, f"Ошибка нажатия клавиши: {e}")
    
    def _execute_hotkey(self, hotkey: str) -> ExecutionResult:
        """Горячие клавиши"""
        try:
            self._lazy_import_pyautogui()
            
            keys = hotkey.split('+')
            self.pyautogui.hotkey(*keys)
            print(f"⌨️ Горячие клавиши: {hotkey}")
            return ExecutionResult(True, f"Горячие клавиши: {hotkey}")
        
        except Exception as e:
            return ExecutionResult(False, f"Ошибка горячих клавиш: {e}")
    
    def _execute_scroll(self, scroll_params: str) -> ExecutionResult:
        """Прокрутка"""
        try:
            self._lazy_import_pyautogui()
            
            parts = scroll_params.split()
            direction = parts[0] if parts else 'down'
            amount = int(parts[1]) if len(parts) > 1 else 3
            
            if direction in ['up', 'down']:
                scroll_amount = amount if direction == 'down' else -amount
                self.pyautogui.scroll(scroll_amount)
            elif direction in ['left', 'right']:
                # Горизонтальная прокрутка (не все системы поддерживают)
                self.pyautogui.hscroll(amount if direction == 'right' else -amount)
            
            print(f"📜 Прокрутка: {direction} {amount}")
            return ExecutionResult(True, f"Прокрутка {direction}")
        
        except Exception as e:
            return ExecutionResult(False, f"Ошибка прокрутки: {e}")


# Пример использования
if __name__ == "__main__":
    executor = SimpleExecutorEnhanced()
    
    # Тестируем на созданных макросах
    macros_dir = Path("data/generated_macros")
    
    if macros_dir.exists():
        atlas_files = list(macros_dir.glob("*.atlas"))
        
        if atlas_files:
            print(f"Найдено {len(atlas_files)} макросов")
            
            # Тестируем первый макрос
            test_file = atlas_files[0]
            print(f"Тестируем: {test_file.name}")
            
            result = executor.execute_atlas_file(str(test_file))
            print(f"Результат: {result}")
        else:
            print("Макросы не найдены")
    else:
        print("Папка с макросами не найдена")
