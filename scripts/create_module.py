#!/usr/bin/env python3
"""
🚀 Генератор Новых Модулей для Macro-Assistant

Использование:
    python scripts/create_module.py my_awesome_module
    python scripts/create_module.py video_processor --description "Обработка видео файлов"
"""

import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime

def create_module(module_name: str, description: str = None, author: str = "Macro-Assistant Team"):
    """
    Создает новый модуль на основе шаблона
    
    Args:
        module_name: Имя нового модуля
        description: Описание модуля
        author: Автор модуля
    """
    
    # Пути
    project_root = Path(__file__).parent.parent
    template_dir = project_root / "modules" / "module_template"
    new_module_dir = project_root / "modules" / module_name
    
    # Проверки
    if not template_dir.exists():
        print(f"❌ Шаблон не найден: {template_dir}")
        return False
    
    if new_module_dir.exists():
        print(f"❌ Модуль уже существует: {new_module_dir}")
        return False
    
    # Создание модуля
    print(f"🚀 Создание модуля '{module_name}'...")
    
    try:
        # Копируем шаблон
        shutil.copytree(template_dir, new_module_dir)
        print(f"✅ Скопирован шаблон в {new_module_dir}")
        
        # Обновляем конфигурацию
        config_file = new_module_dir / "config.json"
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Обновляем поля
        config["name"] = module_name
        config["description"] = description or f"AI модуль {module_name} для Macro-Assistant"
        config["author"] = author
        config["created"] = datetime.now().isoformat()
        
        # Обновляем ключевые слова
        config["keywords"] = [
            module_name,
            module_name.replace("_", " "),
            "custom_module"
        ]
        
        # Сохраняем обновленную конфигурацию
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Обновлена конфигурация")
        
        # Обновляем промпт
        prompt_file = new_module_dir / "prompts" / "base_prompt.txt"
        prompt_content = prompt_file.read_text(encoding='utf-8')
        
        # Заменяем placeholder на реальное имя модуля
        updated_prompt = prompt_content.replace(
            "шаблонный модуль", 
            f"модуль {module_name}"
        )
        updated_prompt = updated_prompt.replace(
            "демонстрирует правильную архитектуру",
            description or f"выполняет задачи {module_name}"
        )
        
        prompt_file.write_text(updated_prompt, encoding='utf-8')
        print(f"✅ Обновлен промпт")
        
        # Обновляем main.py
        main_file = new_module_dir / "main.py"
        main_content = main_file.read_text(encoding='utf-8')
        
        # Заменяем класс
        class_name = ''.join(word.capitalize() for word in module_name.split('_'))
        updated_main = main_content.replace("ModuleTemplate", class_name)
        updated_main = updated_main.replace(
            "module_template", 
            module_name
        )
        updated_main = updated_main.replace(
            "Шаблон для создания новых модулей",
            description or f"Модуль {module_name}"
        )
        
        main_file.write_text(updated_main, encoding='utf-8')
        print(f"✅ Обновлен main.py")
        
        # Создаем README для модуля
        readme_content = f"""# 🧩 {class_name}

## Описание
{description or f'AI модуль {module_name} для системы Macro-Assistant'}

## Автор
{author}

## Создан
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Использование

```python
from modules.{module_name}.main import {class_name}

# Создание модуля
module = {class_name}()

# Обработка запроса
result = module.handle("ваш запрос")
print(result)
```

## Конфигурация
Настройки модуля находятся в `config.json`.

## Промпт
Базовый промпт для AI находится в `prompts/base_prompt.txt`.

## Разработка
1. Обновите промпт в `prompts/base_prompt.txt`
2. Настройте конфигурацию в `config.json`
3. Реализуйте логику в `main.py`
4. Добавьте тесты в `tests/`

## Тестирование
```bash
python modules/{module_name}/main.py
```
"""
        
        readme_file = new_module_dir / "README.md"
        readme_file.write_text(readme_content, encoding='utf-8')
        print(f"✅ Создан README.md")
        
        # Создаем папку для примеров
        examples_dir = new_module_dir / "examples"
        examples_dir.mkdir(exist_ok=True)
        
        example_file = examples_dir / "example_usage.py"
        example_content = f"""#!/usr/bin/env python3
\"\"\"
Пример использования модуля {class_name}
\"\"\"

import sys
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.{module_name}.main import {class_name}

def main():
    # Создание модуля
    module = {class_name}()
    
    # Тестовые запросы
    test_requests = [
        "Привет, что ты умеешь?",
        "Помоги мне с задачей",
        "Покажи свои возможности"
    ]
    
    print(f"🧪 Тестирование модуля {class_name}")
    print("=" * 50)
    
    for i, request in enumerate(test_requests, 1):
        print(f"\\n{{i}}. Запрос: '{{request}}'")
        result = module.handle(request)
        
        if result.get("success"):
            print(f"   ✅ Результат: {{result.get('result', 'N/A')}}")
        else:
            print(f"   ❌ Ошибка: {{result.get('error', 'N/A')}}")

if __name__ == "__main__":
    main()
"""
        
        example_file.write_text(example_content, encoding='utf-8')
        print(f"✅ Создан пример использования")
        
        print(f"\n🎉 Модуль '{module_name}' успешно создан!")
        print(f"📁 Расположение: {new_module_dir}")
        print(f"\n🚀 Следующие шаги:")
        print(f"1. Отредактируйте промпт: {new_module_dir}/prompts/base_prompt.txt")
        print(f"2. Настройте конфигурацию: {new_module_dir}/config.json")
        print(f"3. Реализуйте логику: {new_module_dir}/main.py")
        print(f"4. Протестируйте: python {new_module_dir}/main.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания модуля: {e}")
        # Удаляем частично созданный модуль
        if new_module_dir.exists():
            shutil.rmtree(new_module_dir)
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Создание нового AI модуля для Macro-Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python scripts/create_module.py video_processor
  python scripts/create_module.py email_sender --description "Отправка email сообщений"
  python scripts/create_module.py data_analyzer --author "John Doe"
        """
    )
    
    parser.add_argument(
        "module_name",
        help="Имя нового модуля (используйте snake_case)"
    )
    
    parser.add_argument(
        "--description", "-d",
        help="Описание модуля",
        default=None
    )
    
    parser.add_argument(
        "--author", "-a",
        help="Автор модуля",
        default="Macro-Assistant Team"
    )
    
    args = parser.parse_args()
    
    # Валидация имени модуля
    if not args.module_name.replace("_", "").isalnum():
        print("❌ Имя модуля должно содержать только буквы, цифры и подчеркивания")
        return
    
    if args.module_name.startswith("_") or args.module_name.endswith("_"):
        print("❌ Имя модуля не должно начинаться или заканчиваться подчеркиванием")
        return
    
    # Создание модуля
    success = create_module(
        module_name=args.module_name,
        description=args.description,
        author=args.author
    )
    
    if success:
        print(f"\n✨ Модуль '{args.module_name}' готов к использованию!")
    else:
        print(f"\n💥 Не удалось создать модуль '{args.module_name}'")

if __name__ == "__main__":
    main()
