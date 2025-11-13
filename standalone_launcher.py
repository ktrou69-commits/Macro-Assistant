#!/usr/bin/env python3
"""
standalone_launcher.py
Полностью автономный лаунчер макросов
Не зависит от других модулей системы, работает самостоятельно
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

class StandaloneLauncher:
    """Автономный лаунчер макросов"""
    
    def __init__(self):
        self.macros_dir = Path("data/generated_macros")
        
    def scan_macros(self):
        """Сканирует папку с макросами"""
        if not self.macros_dir.exists():
            print(f"❌ Папка с макросами не найдена: {self.macros_dir}")
            return []
        
        # Находим все .atlas файлы
        atlas_files = list(self.macros_dir.glob("*.atlas"))
        
        if not atlas_files:
            print(f"❌ Макросы не найдены в: {self.macros_dir}")
            return []
        
        # Сортируем по времени изменения (новые сверху)
        atlas_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        return atlas_files
    
    def display_macros(self, macros):
        """Отображает список макросов"""
        print("\n" + "=" * 80)
        print("🚀 АВТОНОМНЫЙ ЛАУНЧЕР МАКРОСОВ")
        print("=" * 80)
        
        for i, macro_file in enumerate(macros, 1):
            # Читаем описание из файла
            description = self.get_macro_description(macro_file)
            
            # Время создания
            mtime = macro_file.stat().st_mtime
            time_str = datetime.fromtimestamp(mtime).strftime("%d.%m.%Y %H:%M")
            
            # Размер файла
            size = macro_file.stat().st_size
            
            print(f"{i:2d}. 📄 {macro_file.stem}")
            print(f"    📝 {description}")
            print(f"    🕐 {time_str} | 📊 {size} байт")
            print()
    
    def get_macro_description(self, macro_file):
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
    
    def preview_macro(self, macro_file):
        """Показывает превью макроса"""
        try:
            with open(macro_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print("\n" + "=" * 60)
            print(f"📋 ПРЕВЬЮ: {macro_file.name}")
            print("=" * 60)
            
            lines = content.split('\n')
            for i, line in enumerate(lines[:15], 1):  # Показываем первые 15 строк
                print(f"{i:2d}: {line}")
            
            if len(lines) > 15:
                print(f"... и еще {len(lines) - 15} строк")
            
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Ошибка чтения файла: {e}")
    
    def execute_macro_standalone(self, macro_file):
        """Выполняет макрос через main.py (автономно)"""
        print(f"\n🚀 Запуск макроса: {macro_file.name}")
        print("=" * 60)
        
        try:
            # Запускаем через main.py как отдельный процесс
            result = subprocess.run([
                "python3", "main.py", "--execute", str(macro_file)
            ], capture_output=True, text=True, timeout=120)
            
            print("📤 ВЫВОД ВЫПОЛНЕНИЯ:")
            print("-" * 40)
            if result.stdout:
                print(result.stdout)
            
            if result.stderr:
                print("⚠️ ПРЕДУПРЕЖДЕНИЯ/ОШИБКИ:")
                print("-" * 40)
                print(result.stderr)
            
            if result.returncode == 0:
                print("\n✅ Макрос выполнен успешно!")
            else:
                print(f"\n❌ Ошибка выполнения (код: {result.returncode})")
                
        except subprocess.TimeoutExpired:
            print("❌ Превышено время ожидания (120с)")
        except FileNotFoundError:
            print("❌ Файл main.py не найден. Убедитесь что вы в правильной папке.")
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
    
    def run(self):
        """Главный цикл приложения"""
        print("🚀 Standalone Macro Launcher")
        print("Автономный лаунчер макросов (независимый от других модулей)")
        
        while True:
            # Сканируем макросы
            macros = self.scan_macros()
            if not macros:
                input("\nНажмите Enter для выхода...")
                break
            
            # Отображаем список
            self.display_macros(macros)
            
            # Меню
            print("КОМАНДЫ:")
            print("  1-N  - Выбрать макрос по номеру")
            print("  p N  - Превью макроса (например: p 1)")
            print("  r    - Обновить список")
            print("  q    - Выход")
            
            # Получаем ввод пользователя
            try:
                choice = input("\n👉 Ваш выбор: ").strip().lower()
                
                if choice == 'q':
                    print("👋 До свидания!")
                    break
                elif choice == 'r':
                    print("🔄 Обновление списка...")
                    continue
                elif choice.startswith('p '):
                    # Превью макроса
                    try:
                        num = int(choice.split()[1])
                        if 1 <= num <= len(macros):
                            self.preview_macro(macros[num - 1])
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
                                self.execute_macro_standalone(selected_macro)
                            else:
                                print("❌ Отменено")
                        else:
                            print("❌ Неверный номер макроса")
                    except ValueError:
                        print("❌ Неверный ввод. Введите номер макроса или команду")
                
                # Пауза перед следующей итерацией
                input("\nНажмите Enter для продолжения...")
                print("\n" * 2)  # Очищаем экран
                
            except KeyboardInterrupt:
                print("\n\n👋 Выход по Ctrl+C")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")


def main():
    """Главная функция"""
    launcher = StandaloneLauncher()
    launcher.run()


if __name__ == "__main__":
    main()
