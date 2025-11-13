#!/usr/bin/env python3
"""
variable_creator.py
Утилита для создания DSL переменных

Позволяет пользователю создавать переменные из .atlas кода
и сохранять их в data/dsl_variables.txt
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import re

class VariableCreator:
    """Создатель DSL переменных"""
    
    def __init__(self):
        self.variables_file = Path("data/dsl_variables.txt")
        self.variables_file.parent.mkdir(parents=True, exist_ok=True)
        
    def create_variable_interactive(self):
        """Интерактивное создание переменной"""
        print("🔧 Создание DSL Переменной")
        print("=" * 50)
        
        # Получаем имя переменной
        while True:
            var_name = input("📝 Введите имя переменной (например: QuickSearch): ").strip()
            if self._validate_variable_name(var_name):
                break
            print("❌ Неверное имя. Используйте только буквы, цифры и подчеркивания")
        
        # Получаем описание
        description = input("📋 Введите описание переменной: ").strip()
        if not description:
            description = f"Пользовательская переменная {var_name}"
        
        # Получаем .atlas код
        print("\n💻 Введите .atlas код (введите 'END' на новой строке для завершения):")
        atlas_lines = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            atlas_lines.append(line)
        
        atlas_code = '\n'.join(atlas_lines)
        
        if not atlas_code.strip():
            print("❌ Код не может быть пустым")
            return
        
        # Создаем переменную
        self._save_variable(var_name, description, atlas_code)
        
        # Обновляем DSL справочник
        self._update_dsl_reference()
        
        print(f"✅ Переменная ${{{var_name}}} создана успешно!")
        
    def create_variable_from_file(self, atlas_file: str, var_name: str = None, description: str = None):
        """Создание переменной из .atlas файла"""
        atlas_path = Path(atlas_file)
        
        if not atlas_path.exists():
            print(f"❌ Файл не найден: {atlas_file}")
            return False
        
        # Читаем содержимое файла
        try:
            with open(atlas_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Ошибка чтения файла: {e}")
            return False
        
        # Извлекаем описание из файла если не задано
        if not description:
            description = self._extract_description_from_atlas(content)
        
        # Генерируем имя переменной если не задано
        if not var_name:
            var_name = self._generate_variable_name_from_file(atlas_path)
        
        # Очищаем код от комментариев метаданных
        atlas_code = self._clean_atlas_code(content)
        
        # Сохраняем переменную
        self._save_variable(var_name, description, atlas_code)
        
        # Обновляем DSL справочник
        self._update_dsl_reference()
        
        print(f"✅ Переменная ${{{var_name}}} создана из файла {atlas_file}")
        return True
    
    def _validate_variable_name(self, name: str) -> bool:
        """Проверка корректности имени переменной"""
        if not name:
            return False
        # Только буквы, цифры и подчеркивания
        return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name) is not None
    
    def _extract_description_from_atlas(self, content: str) -> str:
        """Извлечение описания из .atlas файла"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith("# Description:"):
                return line.replace("# Description:", "").strip()
        
        # Если нет описания, ищем первый комментарий
        for line in lines:
            line = line.strip()
            if line.startswith("#") and not line.startswith("# Generated") and not line.startswith("# Created"):
                return line[1:].strip()
        
        return "Пользовательская переменная"
    
    def _generate_variable_name_from_file(self, file_path: Path) -> str:
        """Генерация имени переменной из имени файла"""
        name = file_path.stem
        # Убираем временные метки
        name = re.sub(r'_\d{8}_\d{6}$', '', name)
        # Заменяем разделители на CamelCase
        parts = re.split(r'[_\-\s]+', name)
        return ''.join(word.capitalize() for word in parts if word)
    
    def _clean_atlas_code(self, content: str) -> str:
        """Очистка .atlas кода от метаданных"""
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            # Пропускаем метаданные
            if (line_stripped.startswith("# Generated") or 
                line_stripped.startswith("# Created") or
                line_stripped.startswith("# Description:")):
                continue
            cleaned_lines.append(line)
        
        # Убираем пустые строки в начале
        while cleaned_lines and not cleaned_lines[0].strip():
            cleaned_lines.pop(0)
        
        return '\n'.join(cleaned_lines)
    
    def _save_variable(self, var_name: str, description: str, atlas_code: str):
        """Сохранение переменной в файл"""
        # Проверяем существует ли файл
        if not self.variables_file.exists():
            self._create_variables_file_header()
        
        # Добавляем переменную
        variable_entry = f"""
${{{var_name}}}
--------------------------------------------------------------------------------
# {description}
{atlas_code}

ИСПОЛЬЗОВАНИЕ:
${{{var_name}}}

# Создано: {datetime.now().isoformat()}
# Использований: 0

--------------------------------------------------------------------------------
"""
        
        # Добавляем в файл
        with open(self.variables_file, 'a', encoding='utf-8') as f:
            f.write(variable_entry)
    
    def _create_variables_file_header(self):
        """Создание заголовка файла переменных"""
        header = """================================================================================
ПОЛЬЗОВАТЕЛЬСКИЕ DSL ПЕРЕМЕННЫЕ
================================================================================

📌 Этот файл содержит переменные, созданные пользователем через AI.
   Они автоматически загружаются парсером и доступны в AI промпте.

================================================================================
"""
        with open(self.variables_file, 'w', encoding='utf-8') as f:
            f.write(header)
    
    def _update_dsl_reference(self):
        """Обновление DSL справочника"""
        try:
            import subprocess
            result = subprocess.run([
                "python3", "dsl_reference_generator.py", 
                "--output", "data/DSL_REFERENCE.txt"
            ], capture_output=True, text=True, cwd=Path.cwd())
            
            if result.returncode == 0:
                print("🔄 DSL справочник обновлен")
            else:
                print(f"⚠️ Ошибка обновления справочника: {result.stderr}")
        except Exception as e:
            print(f"⚠️ Не удалось обновить справочник: {e}")
    
    def list_variables(self):
        """Список всех переменных"""
        if not self.variables_file.exists():
            print("📝 Переменные не найдены")
            return
        
        try:
            with open(self.variables_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ищем переменные
            variables = re.findall(r'\$\{([^}]+)\}', content)
            
            print("📋 Доступные DSL переменные:")
            print("=" * 40)
            for i, var in enumerate(variables, 1):
                print(f"{i:2d}. ${{{var}}}")
            
        except Exception as e:
            print(f"❌ Ошибка чтения переменных: {e}")


def main():
    """Главная функция"""
    creator = VariableCreator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            creator.create_variable_interactive()
        elif command == "from-file" and len(sys.argv) > 2:
            atlas_file = sys.argv[2]
            var_name = sys.argv[3] if len(sys.argv) > 3 else None
            description = sys.argv[4] if len(sys.argv) > 4 else None
            creator.create_variable_from_file(atlas_file, var_name, description)
        elif command == "list":
            creator.list_variables()
        else:
            print("❌ Неверная команда")
            print("Использование:")
            print("  python3 variable_creator.py create")
            print("  python3 variable_creator.py from-file <file.atlas> [name] [description]")
            print("  python3 variable_creator.py list")
    else:
        creator.create_variable_interactive()


if __name__ == "__main__":
    main()
