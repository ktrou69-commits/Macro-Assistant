#!/usr/bin/env python3
"""
⚡ Atlas DSL Executor - Исполнитель .atlas команд
Выполняет команды через Vision, DOM и System
"""

import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass

from .atlas_parser import AtlasMacro, AtlasCommand, AtlasBlock, CommandType

@dataclass
class ExecutionResult:
    """Результат выполнения команды"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0

class AtlasExecutor:
    """
    Исполнитель Atlas DSL команд
    Поддерживает Vision, DOM и System автоматизацию
    """
    
    def __init__(self):
        """Инициализация исполнителя"""
        # Ленивая загрузка зависимостей
        self.pyautogui = None
        self.selenium_driver = None
        self.vision_engine = None
        
        # Переменные выполнения
        self.variables = {}
        self.execution_context = {}
        
        # Настройка логгера
        try:
            from core.logger import get_logger
            self.logger = get_logger("atlas_executor")
        except ImportError:
            import logging
            self.logger = logging.getLogger("atlas_executor")
        
        self.logger.info("⚡ AtlasExecutor инициализирован")
    
    def execute_macro(self, macro: AtlasMacro) -> ExecutionResult:
        """
        Выполнение полного макроса
        
        Args:
            macro: Макрос для выполнения
            
        Returns:
            Результат выполнения
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"🚀 Выполнение макроса: {macro.title}")
            
            # Инициализируем переменные
            self.variables.update(macro.variables)
            
            # Выполняем команды
            for i, command in enumerate(macro.commands):
                result = self._execute_command(command)
                
                if not result.success:
                    execution_time = time.time() - start_time
                    return ExecutionResult(
                        success=False,
                        message=f"Ошибка на команде {i+1}: {result.message}",
                        execution_time=execution_time
                    )
            
            execution_time = time.time() - start_time
            self.logger.info(f"✅ Макрос выполнен за {execution_time:.3f}с")
            
            return ExecutionResult(
                success=True,
                message="Макрос выполнен успешно",
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.exception(f"❌ Ошибка выполнения макроса: {e}")
            return ExecutionResult(
                success=False,
                message=str(e),
                execution_time=execution_time
            )
    
    def _execute_command(self, command: Union[AtlasCommand, AtlasBlock]) -> ExecutionResult:
        """Выполнение одной команды или блока"""
        
        if isinstance(command, AtlasBlock):
            return self._execute_block(command)
        
        if not isinstance(command, AtlasCommand):
            return ExecutionResult(False, "Неизвестный тип команды")
        
        self.logger.debug(f"🔧 Выполнение: {command.command_type.value}")
        
        try:
            # Маршрутизация команд
            if command.command_type == CommandType.OPEN:
                return self._execute_open(command)
            elif command.command_type == CommandType.CLICK:
                return self._execute_click(command)
            elif command.command_type == CommandType.TYPE:
                return self._execute_type(command)
            elif command.command_type == CommandType.WAIT:
                return self._execute_wait(command)
            elif command.command_type == CommandType.PRESS:
                return self._execute_press(command)
            elif command.command_type == CommandType.HOTKEY:
                return self._execute_hotkey(command)
            elif command.command_type == CommandType.SELENIUM_INIT:
                return self._execute_selenium_init(command)
            elif command.command_type == CommandType.SELENIUM_CLICK:
                return self._execute_selenium_click(command)
            elif command.command_type == CommandType.SELENIUM_TYPE:
                return self._execute_selenium_type(command)
            elif command.command_type == CommandType.SELENIUM_CLOSE:
                return self._execute_selenium_close(command)
            elif command.command_type == CommandType.SET_VARIABLE:
                return self._execute_set_variable(command)
            elif command.command_type == CommandType.SYSTEM_COMMAND:
                return self._execute_system_command(command)
            elif command.command_type == CommandType.LOG:
                return self._execute_log(command)
            elif command.command_type == CommandType.ABORT:
                return ExecutionResult(False, "Выполнение прервано командой abort")
            else:
                return ExecutionResult(True, f"Команда {command.command_type.value} пропущена")
                
        except Exception as e:
            return ExecutionResult(False, f"Ошибка выполнения команды: {e}")
    
    def _execute_open(self, command: AtlasCommand) -> ExecutionResult:
        """Открытие приложения"""
        app_name = command.target
        
        try:
            # Используем системную команду open на macOS
            subprocess.run(['open', '-a', app_name], check=True)
            return ExecutionResult(True, f"Приложение {app_name} открыто")
        except subprocess.CalledProcessError as e:
            return ExecutionResult(False, f"Не удалось открыть {app_name}: {e}")
    
    def _execute_click(self, command: AtlasCommand) -> ExecutionResult:
        """Выполнение клика"""
        if command.parameters.get('type') == 'coordinates':
            # Клик по координатам
            x = command.parameters['x']
            y = command.parameters['y']
            return self._click_coordinates(x, y)
        else:
            # Клик по шаблону
            template_name = command.target
            return self._click_template(template_name)
    
    def _click_coordinates(self, x: int, y: int) -> ExecutionResult:
        """Клик по координатам"""
        try:
            if not self.pyautogui:
                import pyautogui
                self.pyautogui = pyautogui
            
            self.pyautogui.click(x, y)
            return ExecutionResult(True, f"Клик по координатам ({x}, {y})")
        except Exception as e:
            return ExecutionResult(False, f"Ошибка клика по координатам: {e}")
    
    def _click_template(self, template_name: str) -> ExecutionResult:
        """Клик по шаблону (через Vision Engine)"""
        try:
            # TODO: Интеграция с Vision Engine
            # Пока используем заглушку
            self.logger.warning(f"⚠️ Vision Engine не реализован, пропускаем клик по {template_name}")
            return ExecutionResult(True, f"Клик по шаблону {template_name} (заглушка)")
        except Exception as e:
            return ExecutionResult(False, f"Ошибка клика по шаблону: {e}")
    
    def _execute_type(self, command: AtlasCommand) -> ExecutionResult:
        """Ввод текста"""
        try:
            if not self.pyautogui:
                import pyautogui
                self.pyautogui = pyautogui
            
            text = self._substitute_variables(command.value)
            self.pyautogui.typewrite(text)
            return ExecutionResult(True, f"Введен текст: {text}")
        except Exception as e:
            return ExecutionResult(False, f"Ошибка ввода текста: {e}")
    
    def _execute_wait(self, command: AtlasCommand) -> ExecutionResult:
        """Ожидание"""
        try:
            duration_str = command.value
            
            # Парсим длительность (3s, 1.5s, 500ms)
            if duration_str.endswith('s'):
                duration = float(duration_str[:-1])
            elif duration_str.endswith('ms'):
                duration = float(duration_str[:-2]) / 1000
            else:
                duration = float(duration_str)
            
            time.sleep(duration)
            return ExecutionResult(True, f"Ожидание {duration}с")
        except Exception as e:
            return ExecutionResult(False, f"Ошибка ожидания: {e}")
    
    def _execute_press(self, command: AtlasCommand) -> ExecutionResult:
        """Нажатие клавиши"""
        try:
            if not self.pyautogui:
                import pyautogui
                self.pyautogui = pyautogui
            
            key = command.target
            self.pyautogui.press(key)
            return ExecutionResult(True, f"Нажата клавиша: {key}")
        except Exception as e:
            return ExecutionResult(False, f"Ошибка нажатия клавиши: {e}")
    
    def _execute_hotkey(self, command: AtlasCommand) -> ExecutionResult:
        """Горячие клавиши"""
        try:
            if not self.pyautogui:
                import pyautogui
                self.pyautogui = pyautogui
            
            hotkey = command.target
            keys = hotkey.split('+')
            self.pyautogui.hotkey(*keys)
            return ExecutionResult(True, f"Горячие клавиши: {hotkey}")
        except Exception as e:
            return ExecutionResult(False, f"Ошибка горячих клавиш: {e}")
    
    def _execute_selenium_init(self, command: AtlasCommand) -> ExecutionResult:
        """Инициализация Selenium"""
        try:
            # TODO: Реализовать Selenium драйвер
            url = command.target
            self.logger.warning(f"⚠️ Selenium не реализован, пропускаем открытие {url}")
            return ExecutionResult(True, f"Selenium инициализирован для {url} (заглушка)")
        except Exception as e:
            return ExecutionResult(False, f"Ошибка инициализации Selenium: {e}")
    
    def _execute_selenium_click(self, command: AtlasCommand) -> ExecutionResult:
        """Selenium клик"""
        try:
            selector = command.target
            self.logger.warning(f"⚠️ Selenium клик по {selector} пропущен (не реализован)")
            return ExecutionResult(True, f"Selenium клик по {selector} (заглушка)")
        except Exception as e:
            return ExecutionResult(False, f"Ошибка Selenium клика: {e}")
    
    def _execute_selenium_type(self, command: AtlasCommand) -> ExecutionResult:
        """Selenium ввод текста"""
        try:
            selector = command.target
            text = self._substitute_variables(command.value)
            self.logger.warning(f"⚠️ Selenium ввод в {selector} пропущен (не реализован)")
            return ExecutionResult(True, f"Selenium ввод в {selector}: {text} (заглушка)")
        except Exception as e:
            return ExecutionResult(False, f"Ошибка Selenium ввода: {e}")
    
    def _execute_selenium_close(self, command: AtlasCommand) -> ExecutionResult:
        """Закрытие Selenium"""
        try:
            self.logger.warning("⚠️ Selenium закрытие пропущено (не реализован)")
            return ExecutionResult(True, "Selenium закрыт (заглушка)")
        except Exception as e:
            return ExecutionResult(False, f"Ошибка закрытия Selenium: {e}")
    
    def _execute_set_variable(self, command: AtlasCommand) -> ExecutionResult:
        """Установка переменной"""
        try:
            name = command.target
            value = self._substitute_variables(command.value)
            self.variables[name] = value
            return ExecutionResult(True, f"Переменная {name} = {value}")
        except Exception as e:
            return ExecutionResult(False, f"Ошибка установки переменной: {e}")
    
    def _execute_system_command(self, command: AtlasCommand) -> ExecutionResult:
        """Выполнение системной команды"""
        try:
            cmd = self._substitute_variables(command.value)
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return ExecutionResult(True, f"Команда выполнена: {cmd}")
            else:
                return ExecutionResult(False, f"Ошибка команды: {result.stderr}")
        except Exception as e:
            return ExecutionResult(False, f"Ошибка системной команды: {e}")
    
    def _execute_log(self, command: AtlasCommand) -> ExecutionResult:
        """Логирование"""
        try:
            message = self._substitute_variables(command.value)
            self.logger.info(f"📝 {message}")
            return ExecutionResult(True, f"Лог: {message}")
        except Exception as e:
            return ExecutionResult(False, f"Ошибка логирования: {e}")
    
    def _execute_block(self, block: AtlasBlock) -> ExecutionResult:
        """Выполнение блока команд"""
        try:
            if block.block_type == 'repeat':
                return self._execute_repeat_block(block)
            elif block.block_type == 'if':
                return self._execute_if_block(block)
            elif block.block_type == 'try':
                return self._execute_try_block(block)
            else:
                return ExecutionResult(False, f"Неизвестный тип блока: {block.block_type}")
        except Exception as e:
            return ExecutionResult(False, f"Ошибка выполнения блока: {e}")
    
    def _execute_repeat_block(self, block: AtlasBlock) -> ExecutionResult:
        """Выполнение repeat блока"""
        try:
            count = int(block.condition)
            
            for i in range(count):
                for command in block.commands:
                    result = self._execute_command(command)
                    if not result.success:
                        return result
            
            return ExecutionResult(True, f"Repeat блок выполнен {count} раз")
        except Exception as e:
            return ExecutionResult(False, f"Ошибка repeat блока: {e}")
    
    def _execute_if_block(self, block: AtlasBlock) -> ExecutionResult:
        """Выполнение if блока"""
        try:
            # TODO: Реализовать условную логику
            self.logger.warning("⚠️ If блоки не реализованы, пропускаем")
            return ExecutionResult(True, "If блок пропущен (не реализован)")
        except Exception as e:
            return ExecutionResult(False, f"Ошибка if блока: {e}")
    
    def _execute_try_block(self, block: AtlasBlock) -> ExecutionResult:
        """Выполнение try блока"""
        try:
            for command in block.commands:
                result = self._execute_command(command)
                if not result.success:
                    self.logger.warning(f"⚠️ Ошибка в try блоке: {result.message}")
                    # В try блоке продолжаем выполнение
            
            return ExecutionResult(True, "Try блок выполнен")
        except Exception as e:
            return ExecutionResult(False, f"Ошибка try блока: {e}")
    
    def _substitute_variables(self, text: str) -> str:
        """Подстановка переменных в тексте"""
        if not text:
            return text
        
        # Заменяем ${variable_name} на значения
        import re
        
        def replace_var(match):
            var_name = match.group(1)
            return str(self.variables.get(var_name, match.group(0)))
        
        return re.sub(r'\$\{(\w+)\}', replace_var, text)

# Пример использования
if __name__ == "__main__":
    from .atlas_parser import AtlasParser
    
    parser = AtlasParser()
    executor = AtlasExecutor()
    
    # Тестовый макрос
    test_content = """# Test Execution
open Calculator
wait 2s
click button_5
wait 0.5s
press enter
log "Тест завершен"
"""
    
    print("🧪 Тестирование AtlasExecutor")
    print("=" * 50)
    
    try:
        macro = parser.parse_content(test_content)
        result = executor.execute_macro(macro)
        
        if result.success:
            print(f"✅ Выполнение успешно: {result.message}")
            print(f"⚡ Время: {result.execution_time:.3f}с")
        else:
            print(f"❌ Ошибка выполнения: {result.message}")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n⚡ AtlasExecutor готов к работе!")
