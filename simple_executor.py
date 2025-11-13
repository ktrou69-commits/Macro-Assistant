#!/usr/bin/env python3
"""
⚡ Simple Executor - Простой исполнитель .atlas макросов
Читает .atlas файлы и выполняет команды через CV + DOM + System
"""

import time
import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    """Результат выполнения команды"""
    success: bool
    message: str
    execution_time: float = 0.0

class SimpleExecutor:
    """
    Простой исполнитель .atlas макросов
    """
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Инициализация исполнителя
        
        Args:
            templates_dir: Путь к шаблонам для CV
        """
        self.templates_dir = Path(templates_dir)
        
        # Ленивая загрузка зависимостей
        self.pyautogui = None
        self.cv2 = None
        self.selenium_driver = None
        
        # Переменные выполнения
        self.variables = {}
        
        print("⚡ SimpleExecutor инициализирован")
    
    def _lazy_import_pyautogui(self):
        """Ленивый импорт PyAutoGUI"""
        if self.pyautogui is None:
            try:
                import pyautogui
                self.pyautogui = pyautogui
                # Отключаем fail-safe
                self.pyautogui.FAILSAFE = False
                print("📦 PyAutoGUI загружен")
            except ImportError:
                print("❌ PyAutoGUI не установлен. Установите: pip install pyautogui")
                raise
    
    def _lazy_import_cv2(self):
        """Ленивый импорт OpenCV"""
        if self.cv2 is None:
            try:
                import cv2
                import numpy as np
                self.cv2 = cv2
                self.np = np
                print("📦 OpenCV загружен")
            except ImportError:
                print("❌ OpenCV не установлен. Установите: pip install opencv-python")
                raise
    
    def execute_atlas_file(self, file_path: str) -> ExecutionResult:
        """
        Выполнение .atlas файла
        
        Args:
            file_path: Путь к .atlas файлу
            
        Returns:
            Результат выполнения
        """
        start_time = time.time()
        
        try:
            atlas_path = Path(file_path)
            
            if not atlas_path.exists():
                return ExecutionResult(
                    success=False,
                    message=f"Файл не найден: {file_path}",
                    execution_time=time.time() - start_time
                )
            
            print(f"🚀 Выполнение макроса: {atlas_path.name}")
            
            # Читаем файл
            with open(atlas_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсим и выполняем
            result = self.execute_atlas_content(content)
            result.execution_time = time.time() - start_time
            
            return result
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                message=f"Ошибка выполнения файла: {e}",
                execution_time=time.time() - start_time
            )
    
    def execute_atlas_content(self, content: str) -> ExecutionResult:
        """
        Выполнение .atlas кода
        
        Args:
            content: Содержимое .atlas файла
            
        Returns:
            Результат выполнения
        """
        try:
            # Парсим команды
            commands = self._parse_atlas_content(content)
            
            if not commands:
                return ExecutionResult(
                    success=False,
                    message="Нет команд для выполнения"
                )
            
            print(f"📋 Найдено команд: {len(commands)}")
            
            # Выполняем команды
            for i, command in enumerate(commands, 1):
                print(f"🔧 Команда {i}/{len(commands)}: {command}")
                
                result = self._execute_command(command)
                
                if not result.success:
                    return ExecutionResult(
                        success=False,
                        message=f"Ошибка на команде {i}: {result.message}"
                    )
            
            return ExecutionResult(
                success=True,
                message=f"Макрос выполнен успешно ({len(commands)} команд)"
            )
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                message=f"Ошибка выполнения: {e}"
            )
    
    def _parse_atlas_content(self, content: str) -> List[str]:
        """Парсинг .atlas содержимого в команды"""
        lines = content.split('\n')
        commands = []
        
        for line in lines:
            line = line.strip()
            
            # Пропускаем пустые строки и комментарии
            if not line or line.startswith('#'):
                continue
            
            commands.append(line)
        
        return commands
    
    def _execute_command(self, command: str) -> ExecutionResult:
        """Выполнение одной команды"""
        try:
            command = command.strip()
            
            # 1. Команды открытия приложений
            if command.startswith('open '):
                app_name = command[5:].strip()
                return self._execute_open(app_name)
            
            # 2. Команды кликов
            elif command.startswith('click '):
                target = command[6:].strip()
                return self._execute_click(target)
            
            # 3. Ввод текста
            elif command.startswith('type '):
                text_match = re.match(r'type\s+"([^"]*)"', command)
                if text_match:
                    text = text_match.group(1)
                    return self._execute_type(text)
                else:
                    return ExecutionResult(False, f"Неверный формат команды type: {command}")
            
            # 4. Ожидание
            elif command.startswith('wait '):
                duration = command[5:].strip()
                return self._execute_wait(duration)
            
            # 5. Нажатие клавиш
            elif command.startswith('press '):
                key = command[6:].strip()
                return self._execute_press(key)
            
            # 6. Горячие клавиши
            elif command.startswith('hotkey '):
                hotkey = command[7:].strip()
                return self._execute_hotkey(hotkey)
            
            # 7. Прокрутка
            elif command.startswith('scroll '):
                scroll_params = command[7:].strip()
                return self._execute_scroll(scroll_params)
            
            # 8. Циклы
            elif command.startswith('repeat '):
                # TODO: Реализовать циклы
                return ExecutionResult(True, f"Repeat команда пропущена (не реализована): {command}")
            
            elif command == 'end':
                return ExecutionResult(True, "End команда")
            
            # 9. Неизвестная команда
            else:
                return ExecutionResult(True, f"Неизвестная команда пропущена: {command}")
        
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
                # Клик по шаблону
                return self._click_template(target)
        
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
    
    def _click_template(self, template_name: str) -> ExecutionResult:
        """Клик по шаблону через улучшенный Computer Vision"""
        try:
            # Ищем шаблон с повторными попытками (как в macro_sequence.py)
            template_path = self._find_template(template_name)
            
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
    
    def _find_template(self, template_name: str) -> Optional[Path]:
        """Поиск файла шаблона"""
        # Возможные имена файлов
        possible_names = [
            f"{template_name}.png",
            f"{template_name}-btn.png",
            f"{template_name}_btn.png"
        ]
        
        # Ищем в директории шаблонов
        for name in possible_names:
            for template_file in self.templates_dir.rglob(name):
                return template_file
        
        # Ищем по частичному совпадению
        for template_file in self.templates_dir.rglob("*.png"):
            if template_name.lower() in template_file.stem.lower():
                return template_file
        
        return None
    
    def _find_template_on_screen(self, template_path: Path) -> Optional[tuple]:
        """Поиск шаблона на экране через OpenCV"""
        try:
            self._lazy_import_cv2()
            self._lazy_import_pyautogui()
            
            # Делаем скриншот
            screenshot = self.pyautogui.screenshot()
            screenshot_np = self.np.array(screenshot)
            screenshot_cv = self.cv2.cvtColor(screenshot_np, self.cv2.COLOR_RGB2BGR)
            
            # Загружаем шаблон
            template = self.cv2.imread(str(template_path))
            if template is None:
                print(f"❌ Не удалось загрузить шаблон: {template_path}")
                return None
            
            # Ищем шаблон
            result = self.cv2.matchTemplate(screenshot_cv, template, self.cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = self.cv2.minMaxLoc(result)
            
            # Проверяем уверенность
            if max_val >= 0.8:  # 80% уверенности
                # Вычисляем центр шаблона
                template_height, template_width = template.shape[:2]
                center_x = max_loc[0] + template_width // 2
                center_y = max_loc[1] + template_height // 2
                
                print(f"✅ Шаблон найден с уверенностью {max_val:.3f}")
                return (center_x, center_y)
            else:
                print(f"⚠️ Низкая уверенность поиска: {max_val:.3f}")
                return None
        
        except Exception as e:
            print(f"❌ Ошибка поиска шаблона: {e}")
            return None
    
    def _execute_type(self, text: str) -> ExecutionResult:
        """Ввод текста"""
        try:
            self._lazy_import_pyautogui()
            
            # Подстановка переменных
            text = self._substitute_variables(text)
            
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
        
        # Конвертируем в OpenCV формат
        import numpy as np
        frame = np.array(screenshot)
        frame = self.cv2.cvtColor(frame, self.cv2.COLOR_RGB2BGR)
        gray = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2GRAY)
        
        # Template matching
        res = self.cv2.matchTemplate(gray, template, self.cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = self.cv2.minMaxLoc(res)
        
        if max_val >= threshold:
            h, w = template.shape
            
            # Вычисляем центр
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            
            # Определяем масштаб дисплея (Retina)
            display_scale = self._get_display_scale()
            
            # Корректируем координаты для pyautogui.click()
            center_x = int(center_x / display_scale)
            center_y = int(center_y / display_scale)
            
            return True, (center_x, center_y), max_val
        
        return False, None, max_val
    
    except Exception as e:
        print(f"❌ Ошибка продвинутого поиска: {e}")
        return False, None, 0.0

def _get_display_scale(self):
    """Определение масштаба дисплея (Retina)"""
    try:
        self._lazy_import_pyautogui()
        
        screen_size = self.pyautogui.size()
        screenshot = self.pyautogui.screenshot()
        
        # Если физическое разрешение больше логического - это Retina
        if screenshot.width != screen_size.width:
            scale = screenshot.width / screen_size.width
            return scale
        
        return 1.0
    except:
        return 1.0

def _execute_type(self, text: str) -> ExecutionResult:
    """Ввод текста"""
    try:
        self._lazy_import_pyautogui()
        
        # Подстановка переменных
        text = self._substitute_variables(text)
        
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

def _substitute_variables(self, text: str) -> str:
    """Подстановка переменных в тексте"""
    # Простая подстановка переменных ${var}
    # В будущем можно расширить
    return text

# Пример использования
if __name__ == "__main__":
    executor = SimpleExecutor()
    
    # Тестируем на созданных макросах
    macros_dir = Path("data/generated_macros")
    
    if macros_dir.exists():
        atlas_files = list(macros_dir.glob("*.atlas"))
        
        if atlas_files:
            print("🧪 Тестирование SimpleExecutor")
            print("=" * 60)
            
            # Берем первый файл для теста
            test_file = atlas_files[0]
            print(f"\n🎯 Тестовый файл: {test_file.name}")
            
            result = executor.execute_atlas_file(str(test_file))
            
            if result.success:
                print(f"✅ Выполнение успешно: {result.message}")
                print(f"⚡ Время: {result.execution_time:.3f}с")
            else:
                print(f"❌ Ошибка выполнения: {result.message}")
        else:
            print("⚠️ Нет .atlas файлов для тестирования")
    else:
        print("⚠️ Директория с макросами не найдена")
    
    print("\n⚡ SimpleExecutor готов к работе!")
