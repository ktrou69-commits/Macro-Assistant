#!/usr/bin/env python3
"""
🚀 Macro-Assistant - Простая система автоматизации
INPUT → AI Generator → .atlas файл → Executor → Выполнение
"""

import sys
import argparse
from pathlib import Path
from simple_ai_generator import SimpleAIGenerator
from simple_executor import SimpleExecutor

class MacroAssistant:
    """
    Главное приложение Macro-Assistant
    """
    
    def __init__(self):
        """Инициализация системы"""
        self.generator = SimpleAIGenerator()
        self.executor = SimpleExecutor()
        
        print("🚀 Macro-Assistant инициализирован")
        print("=" * 50)
    
    def process_request(self, user_input: str, execute: bool = True) -> dict:
        """
        Обработка запроса пользователя
        
        Args:
            user_input: Запрос пользователя
            execute: Выполнить макрос после генерации
            
        Returns:
            Результат обработки
        """
        print(f"🎯 Запрос: {user_input}")
        print("-" * 30)
        
        # 1. Генерируем макрос
        print("🤖 Генерация макроса...")
        gen_result = self.generator.generate_macro(user_input)
        
        if not gen_result["success"]:
            return {
                "success": False,
                "error": f"Ошибка генерации: {gen_result['error']}",
                "stage": "generation"
            }
        
        print(f"✅ Макрос сгенерирован: {gen_result['file_path']}")
        print(f"⚡ Время генерации: {gen_result['execution_time']:.3f}с")
        
        result = {
            "success": True,
            "generation": gen_result,
            "atlas_code": gen_result["atlas_code"],
            "file_path": gen_result["file_path"]
        }
        
        # 2. Выполняем макрос (если нужно)
        if execute:
            print("\n⚡ Выполнение макроса...")
            exec_result = self.executor.execute_atlas_file(gen_result["file_path"])
            
            result["execution"] = exec_result
            result["success"] = exec_result.success
            
            if exec_result.success:
                print(f"✅ Макрос выполнен: {exec_result.message}")
                print(f"⚡ Время выполнения: {exec_result.execution_time:.3f}с")
            else:
                print(f"❌ Ошибка выполнения: {exec_result.message}")
                result["error"] = exec_result.message
                result["stage"] = "execution"
        
        return result
    
    def interactive_mode(self):
        """Интерактивный режим"""
        print("\n🎮 Интерактивный режим")
        print("Введите запрос или 'quit' для выхода")
        print("Примеры:")
        print("  - открой Chrome и найди видео про Python")
        print("  - поставь 3 лайка в TikTok")
        print("  - посчитай 25 плюс 17")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n🤖 Ваш запрос: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'выход']:
                    print("👋 До свидания!")
                    break
                
                # Обрабатываем запрос
                result = self.process_request(user_input)
                
                if result["success"]:
                    print(f"\n🎉 Готово! Макрос выполнен успешно")
                else:
                    print(f"\n❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
                
                print("=" * 50)
                
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
            except Exception as e:
                print(f"❌ Неожиданная ошибка: {e}")
    
    def list_generated_macros(self):
        """Список сгенерированных макросов"""
        macros_dir = Path("data/generated_macros")
        
        if not macros_dir.exists():
            print("📂 Нет сгенерированных макросов")
            return
        
        atlas_files = list(macros_dir.glob("*.atlas"))
        
        if not atlas_files:
            print("📂 Нет .atlas файлов")
            return
        
        print(f"📋 Найдено макросов: {len(atlas_files)}")
        print("-" * 50)
        
        for i, file_path in enumerate(sorted(atlas_files), 1):
            # Читаем описание из файла
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                description = "Без описания"
                for line in lines:
                    if line.startswith('# Description:'):
                        description = line[14:].strip()
                        break
                
                print(f"{i:2d}. {file_path.name}")
                print(f"    📝 {description}")
                print(f"    📅 {file_path.stat().st_mtime}")
            
            except Exception as e:
                print(f"{i:2d}. {file_path.name} (ошибка чтения: {e})")
    
    def execute_file(self, file_path: str):
        """Выполнение конкретного .atlas файла"""
        print(f"⚡ Выполнение файла: {file_path}")
        
        result = self.executor.execute_atlas_file(file_path)
        
        if result.success:
            print(f"✅ Выполнено: {result.message}")
            print(f"⚡ Время: {result.execution_time:.3f}с")
        else:
            print(f"❌ Ошибка: {result.message}")
        
        return result.success

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description='🚀 Macro-Assistant - Простая система автоматизации',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Интерактивный режим
  python3 main.py

  # Выполнить запрос напрямую
  python3 main.py --request "открой Chrome и найди видео про Python"

  # Только сгенерировать макрос (не выполнять)
  python3 main.py --request "поставь лайк в TikTok" --no-execute

  # Выполнить существующий .atlas файл
  python3 main.py --execute data/generated_macros/my_macro.atlas

  # Список сгенерированных макросов
  python3 main.py --list

Система работает по принципу:
INPUT → AI Generator → .atlas файл → Executor → Выполнение
        """
    )
    
    parser.add_argument(
        '--request', '-r',
        type=str,
        help='Запрос для генерации и выполнения макроса'
    )
    
    parser.add_argument(
        '--execute', '-e',
        type=str,
        help='Выполнить существующий .atlas файл'
    )
    
    parser.add_argument(
        '--no-execute',
        action='store_true',
        help='Только сгенерировать макрос, не выполнять'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='Показать список сгенерированных макросов'
    )
    
    args = parser.parse_args()
    
    # Создаем приложение
    app = MacroAssistant()
    
    # Обрабатываем аргументы
    if args.list:
        app.list_generated_macros()
    
    elif args.execute:
        app.execute_file(args.execute)
    
    elif args.request:
        execute = not args.no_execute
        result = app.process_request(args.request, execute=execute)
        
        if not result["success"]:
            sys.exit(1)
    
    else:
        # Интерактивный режим
        app.interactive_mode()

if __name__ == "__main__":
    main()
