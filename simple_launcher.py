#!/usr/bin/env python3
"""
simple_launcher.py
Простой консольный лаунчер макросов
"""

import sys
from pathlib import Path
from datetime import datetime
import subprocess

def scan_macros():
    """Сканирует папку с макросами"""
    macros_dir = Path("data/generated_macros")
    
    if not macros_dir.exists():
        print(f"❌ Папка с макросами не найдена: {macros_dir}")
        return []
    
    # Находим все .atlas файлы
    atlas_files = list(macros_dir.glob("*.atlas"))
    
    if not atlas_files:
        print(f"❌ Макросы не найдены в: {macros_dir}")
        return []
    
    # Сортируем по времени изменения (новые сверху)
    atlas_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    return atlas_files

def get_macro_description(macro_file):
    """Извлекает описание из макроса"""
    try:
        with open(macro_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Ищем строку с Description
        for line in lines:
            if line.startswith("# Description:"):
                return line.replace("# Description:", "").strip()
        
        # Если нет описания, возвращаем имя файла
        return macro_file.stem.replace("_", " ")
        
    except Exception as e:
        return f"Ошибка чтения: {e}"

def display_macros(macros):
    """Отображает список макросов"""
    print("\n" + "=" * 80)
    print("🚀 ДОСТУПНЫЕ МАКРОСЫ")
    print("=" * 80)
    
    for i, macro_file in enumerate(macros, 1):
        # Читаем описание из файла
        description = get_macro_description(macro_file)
        
        # Время создания
        mtime = macro_file.stat().st_mtime
        time_str = datetime.fromtimestamp(mtime).strftime("%d.%m %H:%M")
        
        print(f"{i:2d}. 📄 {macro_file.stem}")
        print(f"    📝 {description}")
        print(f"    🕐 {time_str}")
        print()

def preview_macro(macro_file):
    """Показывает превью макроса"""
    try:
        with open(macro_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n" + "=" * 60)
        print(f"📋 ПРЕВЬЮ: {macro_file.name}")
        print("=" * 60)
        
        lines = content.split('\n')
        for i, line in enumerate(lines[:10], 1):  # Показываем первые 10 строк
            print(f"{i:2d}: {line}")
        
        if len(lines) > 10:
            print(f"... и еще {len(lines) - 10} строк")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")

def execute_macro(macro_file):
    """Выполняет выбранный макрос"""
    print(f"\n🚀 Запуск макроса: {macro_file.name}")
    print("=" * 60)
    
    try:
        # Импортируем SimpleExecutor
        from simple_executor import SimpleExecutor
        
        # Создаем исполнитель
        executor = SimpleExecutor()
        
        # Выполняем макрос
        result = executor.execute_atlas_file(str(macro_file))
        
        if result.success:
            print(f"✅ Макрос выполнен успешно!")
            print(f"⚡ Время выполнения: {result.execution_time:.2f}с")
            print(f"📋 Результат: {result.message}")
        else:
            print(f"❌ Ошибка выполнения: {result.message}")
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

def main():
    """Главная функция"""
    print("🚀 Macro-Assistant Simple Launcher")
    
    # Сканируем макросы
    macros = scan_macros()
    if not macros:
        return
    
    # Отображаем список
    display_macros(macros)
    
    # Меню
    print("КОМАНДЫ:")
    print("  1-N  - Выбрать и запустить макрос")
    print("  p N  - Превью макроса (например: p 1)")
    print("  q    - Выход")
    
    while True:
        try:
            choice = input("\n👉 Ваш выбор: ").strip().lower()
            
            if choice == 'q':
                print("👋 До свидания!")
                break
            elif choice.startswith('p '):
                # Превью макроса
                try:
                    num = int(choice.split()[1])
                    if 1 <= num <= len(macros):
                        preview_macro(macros[num - 1])
                    else:
                        print("❌ Неверный номер макроса")
                except (IndexError, ValueError):
                    print("❌ Неверный формат команды. Используйте: p N")
            else:
                # Выполнение макроса
                try:
                    num = int(choice)
                    if 1 <= num <= len(macros):
                        selected_macro = macros[num - 1]
                        
                        # Подтверждение
                        confirm = input(f"🤔 Запустить '{selected_macro.stem}'? (y/n): ").strip().lower()
                        if confirm in ['y', 'yes', 'да', 'д']:
                            execute_macro(selected_macro)
                        else:
                            print("❌ Отменено")
                    else:
                        print("❌ Неверный номер макроса")
                except ValueError:
                    print("❌ Неверный ввод. Введите номер макроса или команду")
            
        except KeyboardInterrupt:
            print("\n\n👋 Выход по Ctrl+C")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
