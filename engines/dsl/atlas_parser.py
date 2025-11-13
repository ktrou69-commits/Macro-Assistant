#!/usr/bin/env python3
"""
🔧 Atlas DSL Parser - Парсер .atlas файлов
Конвертирует .atlas DSL в исполняемые команды
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class CommandType(Enum):
    """Типы команд DSL"""
    # Базовые команды
    OPEN = "open"
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    TYPE = "type"
    PASTE = "paste"
    PRESS = "press"
    HOTKEY = "hotkey"
    SCROLL = "scroll"
    WAIT = "wait"
    SLEEP = "sleep"
    
    # Selenium команды
    SELENIUM_INIT = "selenium_init"
    SELENIUM_CLICK = "selenium_click"
    SELENIUM_TYPE = "selenium_type"
    SELENIUM_CLOSE = "selenium_close"
    
    # Системные команды
    SYSTEM_COMMAND = "system_command"
    
    # Переменные
    SET_VARIABLE = "set_variable"
    GET_VARIABLE = "get_variable"
    
    # Управляющие структуры
    IF = "if"
    ELSE = "else"
    END = "end"
    REPEAT = "repeat"
    WHILE = "while"
    FOR_EACH = "for_each"
    
    # Обработка ошибок
    TRY = "try"
    CATCH = "catch"
    LOG = "log"
    ABORT = "abort"
    
    # Комментарии
    COMMENT = "comment"

@dataclass
class AtlasCommand:
    """Команда Atlas DSL"""
    command_type: CommandType
    target: Optional[str] = None
    value: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    line_number: int = 0
    raw_line: str = ""
    indent_level: int = 0

@dataclass
class AtlasBlock:
    """Блок команд (для циклов, условий)"""
    block_type: str
    condition: Optional[str] = None
    commands: List[Union[AtlasCommand, 'AtlasBlock']] = field(default_factory=list)
    line_number: int = 0
    indent_level: int = 0

@dataclass
class AtlasMacro:
    """Полный макрос Atlas"""
    title: str
    description: str
    commands: List[Union[AtlasCommand, AtlasBlock]]
    variables: Dict[str, Any]
    metadata: Dict[str, Any]
    file_path: Optional[str] = None

class AtlasParser:
    """
    Парсер .atlas файлов в исполняемые команды
    """
    
    def __init__(self, templates_dir: str = "templates", dom_selectors_dir: str = "data/dom_selectors"):
        """
        Инициализация парсера
        
        Args:
            templates_dir: Путь к директории с шаблонами
            dom_selectors_dir: Путь к DOM селекторам
        """
        self.templates_dir = Path(templates_dir)
        self.dom_selectors_dir = Path(dom_selectors_dir)
        
        # Кэш для ускорения
        self.template_cache = {}
        self.dom_cache = {}
        self.variables_cache = {}
        
        # Настройка логгера
        try:
            from core.logger import get_logger
            self.logger = get_logger("atlas_parser")
        except ImportError:
            import logging
            self.logger = logging.getLogger("atlas_parser")
        
        # Загружаем доступные ресурсы
        self._load_templates()
        self._load_dom_selectors()
        self._load_dsl_variables()
        
        self.logger.info("🔧 AtlasParser инициализирован")
    
    def parse_file(self, file_path: str) -> AtlasMacro:
        """
        Парсинг .atlas файла
        
        Args:
            file_path: Путь к .atlas файлу
            
        Returns:
            Объект AtlasMacro
        """
        atlas_path = Path(file_path)
        
        if not atlas_path.exists():
            raise FileNotFoundError(f"Atlas файл не найден: {file_path}")
        
        try:
            content = atlas_path.read_text(encoding='utf-8')
            return self.parse_content(content, str(atlas_path))
        except Exception as e:
            self.logger.error(f"❌ Ошибка чтения файла {file_path}: {e}")
            raise
    
    def parse_content(self, content: str, file_path: Optional[str] = None) -> AtlasMacro:
        """
        Парсинг содержимого .atlas
        
        Args:
            content: Содержимое .atlas файла
            file_path: Путь к файлу (опционально)
            
        Returns:
            Объект AtlasMacro
        """
        lines = content.split('\n')
        
        # Извлекаем метаданные из комментариев
        metadata = self._extract_metadata(lines)
        
        # Парсим команды
        commands, variables = self._parse_commands(lines)
        
        # Создаем макрос
        macro = AtlasMacro(
            title=metadata.get('title', 'Untitled Macro'),
            description=metadata.get('description', ''),
            commands=commands,
            variables=variables,
            metadata=metadata,
            file_path=file_path
        )
        
        self.logger.debug(f"📋 Парсинг завершен: {len(commands)} команд, {len(variables)} переменных")
        return macro
    
    def _extract_metadata(self, lines: List[str]) -> Dict[str, Any]:
        """Извлечение метаданных из комментариев"""
        metadata = {
            'generated': datetime.now().isoformat(),
            'platform': 'macOS',
            'version': '1.0'
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                # Парсим метаданные из комментариев
                if 'Title:' in line:
                    metadata['title'] = line.split('Title:', 1)[1].strip()
                elif 'Description:' in line:
                    metadata['description'] = line.split('Description:', 1)[1].strip()
                elif 'Date:' in line:
                    metadata['date'] = line.split('Date:', 1)[1].strip()
                elif 'Platform:' in line:
                    metadata['platform'] = line.split('Platform:', 1)[1].strip()
        
        return metadata
    
    def _parse_commands(self, lines: List[str]) -> Tuple[List[Union[AtlasCommand, AtlasBlock]], Dict[str, Any]]:
        """Парсинг команд из строк"""
        commands = []
        variables = {}
        
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            
            # Пропускаем пустые строки и комментарии
            if not line.strip() or line.strip().startswith('#'):
                i += 1
                continue
            
            # Определяем уровень отступа
            indent_level = len(line) - len(line.lstrip())
            clean_line = line.strip()
            
            # Парсим команду
            if clean_line.startswith(('if ', 'repeat ', 'while ', 'for_each ', 'try:')):
                # Блочная команда
                block, consumed_lines = self._parse_block(lines, i)
                commands.append(block)
                i += consumed_lines
            else:
                # Обычная команда
                command = self._parse_single_command(clean_line, i + 1, line)
                if command:
                    commands.append(command)
                    
                    # Если это переменная, сохраняем ее
                    if command.command_type == CommandType.SET_VARIABLE:
                        var_name = command.target
                        var_value = command.value
                        variables[var_name] = var_value
                
                i += 1
        
        return commands, variables
    
    def _parse_single_command(self, line: str, line_number: int, raw_line: str) -> Optional[AtlasCommand]:
        """Парсинг одной команды"""
        if not line.strip():
            return None
        
        # Определяем уровень отступа
        indent_level = len(raw_line) - len(raw_line.lstrip())
        
        # Парсим различные типы команд
        
        # 1. Открытие приложения: open AppName
        if line.startswith('open '):
            app_name = line[5:].strip()
            return AtlasCommand(
                command_type=CommandType.OPEN,
                target=app_name,
                line_number=line_number,
                raw_line=raw_line,
                indent_level=indent_level
            )
        
        # 2. Клик: click ElementName
        elif line.startswith('click '):
            element = line[6:].strip()
            # Проверяем координаты: click (x, y)
            coord_match = re.match(r'click\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', line)
            if coord_match:
                x, y = coord_match.groups()
                return AtlasCommand(
                    command_type=CommandType.CLICK,
                    parameters={'x': int(x), 'y': int(y), 'type': 'coordinates'},
                    line_number=line_number,
                    raw_line=raw_line,
                    indent_level=indent_level
                )
            else:
                return AtlasCommand(
                    command_type=CommandType.CLICK,
                    target=element,
                    parameters={'type': 'template'},
                    line_number=line_number,
                    raw_line=raw_line,
                    indent_level=indent_level
                )
        
        # 3. Ввод текста: type "text"
        elif line.startswith('type '):
            text_match = re.match(r'type\s+"([^"]*)"', line)
            if text_match:
                text = text_match.group(1)
                return AtlasCommand(
                    command_type=CommandType.TYPE,
                    value=text,
                    line_number=line_number,
                    raw_line=raw_line,
                    indent_level=indent_level
                )
        
        # 4. Ожидание: wait 3s
        elif line.startswith('wait '):
            duration = line[5:].strip()
            return AtlasCommand(
                command_type=CommandType.WAIT,
                value=duration,
                line_number=line_number,
                raw_line=raw_line,
                indent_level=indent_level
            )
        
        # 5. Нажатие клавиши: press enter
        elif line.startswith('press '):
            key = line[6:].strip()
            return AtlasCommand(
                command_type=CommandType.PRESS,
                target=key,
                line_number=line_number,
                raw_line=raw_line,
                indent_level=indent_level
            )
        
        # 6. Горячие клавиши: hotkey cmd+c
        elif line.startswith('hotkey '):
            hotkey = line[7:].strip()
            return AtlasCommand(
                command_type=CommandType.HOTKEY,
                target=hotkey,
                line_number=line_number,
                raw_line=raw_line,
                indent_level=indent_level
            )
        
        # 7. Selenium команды
        elif line.startswith('selenium_init '):
            # selenium_init url="https://site.com"
            url_match = re.match(r'selenium_init\s+url="([^"]*)"', line)
            if url_match:
                url = url_match.group(1)
                return AtlasCommand(
                    command_type=CommandType.SELENIUM_INIT,
                    target=url,
                    line_number=line_number,
                    raw_line=raw_line,
                    indent_level=indent_level
                )
        
        elif line.startswith('selenium_click '):
            # selenium_click selector="button"
            selector_match = re.match(r'selenium_click\s+selector="([^"]*)"', line)
            if selector_match:
                selector = selector_match.group(1)
                return AtlasCommand(
                    command_type=CommandType.SELENIUM_CLICK,
                    target=selector,
                    line_number=line_number,
                    raw_line=raw_line,
                    indent_level=indent_level
                )
        
        elif line.startswith('selenium_type '):
            # selenium_type selector="input" text="hello"
            type_match = re.match(r'selenium_type\s+selector="([^"]*)"\s+text="([^"]*)"', line)
            if type_match:
                selector, text = type_match.groups()
                return AtlasCommand(
                    command_type=CommandType.SELENIUM_TYPE,
                    target=selector,
                    value=text,
                    line_number=line_number,
                    raw_line=raw_line,
                    indent_level=indent_level
                )
        
        elif line == 'selenium_close':
            return AtlasCommand(
                command_type=CommandType.SELENIUM_CLOSE,
                line_number=line_number,
                raw_line=raw_line,
                indent_level=indent_level
            )
        
        # 8. Переменные: set_variable name="value"
        elif line.startswith('set_variable '):
            var_match = re.match(r'set_variable\s+(\w+)="([^"]*)"', line)
            if var_match:
                name, value = var_match.groups()
                return AtlasCommand(
                    command_type=CommandType.SET_VARIABLE,
                    target=name,
                    value=value,
                    line_number=line_number,
                    raw_line=raw_line,
                    indent_level=indent_level
                )
        
        # 9. Системные команды: system_command "ls -la"
        elif line.startswith('system_command '):
            cmd_match = re.match(r'system_command\s+"([^"]*)"', line)
            if cmd_match:
                command = cmd_match.group(1)
                return AtlasCommand(
                    command_type=CommandType.SYSTEM_COMMAND,
                    value=command,
                    line_number=line_number,
                    raw_line=raw_line,
                    indent_level=indent_level
                )
        
        # 10. Логирование: log "message"
        elif line.startswith('log '):
            log_match = re.match(r'log\s+"([^"]*)"', line)
            if log_match:
                message = log_match.group(1)
                return AtlasCommand(
                    command_type=CommandType.LOG,
                    value=message,
                    line_number=line_number,
                    raw_line=raw_line,
                    indent_level=indent_level
                )
        
        # 11. Прерывание: abort
        elif line == 'abort':
            return AtlasCommand(
                command_type=CommandType.ABORT,
                line_number=line_number,
                raw_line=raw_line,
                indent_level=indent_level
            )
        
        # Неизвестная команда
        else:
            self.logger.warning(f"⚠️ Неизвестная команда на строке {line_number}: {line}")
            return AtlasCommand(
                command_type=CommandType.COMMENT,
                value=line,
                line_number=line_number,
                raw_line=raw_line,
                indent_level=indent_level
            )
    
    def _parse_block(self, lines: List[str], start_index: int) -> Tuple[AtlasBlock, int]:
        """Парсинг блочных команд (if, repeat, try)"""
        start_line = lines[start_index].strip()
        indent_level = len(lines[start_index]) - len(lines[start_index].lstrip())
        
        # Определяем тип блока
        if start_line.startswith('if '):
            condition = start_line[3:].rstrip(':')
            block_type = 'if'
        elif start_line.startswith('repeat '):
            condition = start_line[7:].rstrip(':')
            block_type = 'repeat'
        elif start_line.startswith('try:'):
            condition = None
            block_type = 'try'
        else:
            condition = start_line.rstrip(':')
            block_type = 'unknown'
        
        block = AtlasBlock(
            block_type=block_type,
            condition=condition,
            line_number=start_index + 1,
            indent_level=indent_level
        )
        
        # Парсим содержимое блока
        i = start_index + 1
        while i < len(lines):
            line = lines[i].rstrip()
            
            if not line.strip():
                i += 1
                continue
            
            current_indent = len(line) - len(line.lstrip())
            clean_line = line.strip()
            
            # Конец блока
            if current_indent <= indent_level and clean_line in ['end', 'catch:', 'else:']:
                if clean_line == 'end':
                    break
                elif clean_line in ['catch:', 'else:']:
                    # TODO: Обработка catch и else блоков
                    break
            
            # Вложенная команда
            if current_indent > indent_level:
                if clean_line.startswith(('if ', 'repeat ', 'while ', 'try:')):
                    # Вложенный блок
                    nested_block, consumed = self._parse_block(lines, i)
                    block.commands.append(nested_block)
                    i += consumed
                else:
                    # Обычная команда
                    command = self._parse_single_command(clean_line, i + 1, line)
                    if command:
                        block.commands.append(command)
                    i += 1
            else:
                break
        
        consumed_lines = i - start_index + 1
        return block, consumed_lines
    
    def _load_templates(self):
        """Загрузка доступных шаблонов"""
        if not self.templates_dir.exists():
            self.logger.warning(f"⚠️ Директория шаблонов не найдена: {self.templates_dir}")
            return
        
        template_count = 0
        for png_file in self.templates_dir.rglob("*.png"):
            # Создаем короткое имя
            short_name = png_file.stem
            
            # Убираем префиксы
            for prefix in ["Chrome-", "Safari-", "Atlas-", "YouTube-", "TikTok-"]:
                if short_name.startswith(prefix):
                    short_name = short_name[len(prefix):]
            
            # Убираем суффиксы
            short_name = short_name.replace("-btn", "").replace("_btn", "")
            
            # Сохраняем в кэш
            self.template_cache[short_name] = str(png_file)
            self.template_cache[png_file.stem] = str(png_file)
            template_count += 1
        
        self.logger.info(f"📸 Загружено {template_count} шаблонов")
    
    def _load_dom_selectors(self):
        """Загрузка DOM селекторов"""
        if not self.dom_selectors_dir.exists():
            self.logger.warning(f"⚠️ Директория DOM селекторов не найдена: {self.dom_selectors_dir}")
            return
        
        # TODO: Реализовать загрузку DOM селекторов
        self.logger.debug("🌐 DOM селекторы будут загружены позже")
    
    def _load_dsl_variables(self):
        """Загрузка DSL переменных"""
        # TODO: Реализовать загрузку DSL переменных из templates/DSL_VARIABLES.txt
        self.logger.debug("💾 DSL переменные будут загружены позже")
    
    def get_template_path(self, template_name: str) -> Optional[str]:
        """Получение пути к шаблону по имени"""
        return self.template_cache.get(template_name)
    
    def validate_macro(self, macro: AtlasMacro) -> List[str]:
        """Валидация макроса"""
        errors = []
        
        # Проверяем команды
        for i, command in enumerate(macro.commands):
            if isinstance(command, AtlasCommand):
                # Проверяем шаблоны
                if command.command_type == CommandType.CLICK and command.target:
                    if command.parameters.get('type') == 'template':
                        if not self.get_template_path(command.target):
                            errors.append(f"Шаблон '{command.target}' не найден (строка {command.line_number})")
        
        return errors

# Пример использования
if __name__ == "__main__":
    parser = AtlasParser()
    
    # Тестовый .atlas контент
    test_content = """# Test Macro
# Description: Тестовый макрос

open ChromeApp
wait 2s
click ChromeNewTab
wait 1s
type "hello world"
press enter
hotkey cmd+c
selenium_init url="https://google.com"
selenium_type selector="input[name='q']" text="test"
selenium_click selector="button[type='submit']"
wait 3s
selenium_close
"""
    
    print("🧪 Тестирование AtlasParser")
    print("=" * 50)
    
    try:
        macro = parser.parse_content(test_content)
        
        print(f"📋 Макрос: {macro.title}")
        print(f"📝 Описание: {macro.description}")
        print(f"🔧 Команд: {len(macro.commands)}")
        print(f"💾 Переменных: {len(macro.variables)}")
        
        print("\n📋 Команды:")
        for i, cmd in enumerate(macro.commands, 1):
            if isinstance(cmd, AtlasCommand):
                print(f"  {i}. {cmd.command_type.value}: {cmd.target or cmd.value or 'N/A'}")
            elif isinstance(cmd, AtlasBlock):
                print(f"  {i}. {cmd.block_type} блок: {cmd.condition or 'N/A'}")
        
        # Валидация
        errors = parser.validate_macro(macro)
        if errors:
            print(f"\n❌ Ошибки валидации:")
            for error in errors:
                print(f"   - {error}")
        else:
            print(f"\n✅ Макрос валиден!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n🔧 AtlasParser готов к работе!")
