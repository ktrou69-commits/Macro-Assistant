#!/usr/bin/env python3
"""
test_cv_enhanced.py
Тест улучшенного Computer Vision
"""

from simple_executor_enhanced import SimpleExecutorEnhanced
from pathlib import Path

def test_cv_macro():
    """Тестируем макрос с Computer Vision"""
    
    # Создаем тестовый макрос
    test_macro = """# CV Test Macro
# Description: Тест улучшенного Computer Vision
# Created: 2025-11-13T17:10:00

# Открываем Chrome
open ChromeApp
wait 3s

# Тестируем клик по новой вкладке (Computer Vision)
click ChromeNewTab
wait 2s

# Тестируем клик по поле поиска
click ChromeSearchField
wait 1s

# Вводим тест
type "CV Test Success!"
wait 1s

# Готово"""
    
    # Сохраняем тестовый макрос
    test_file = Path("data/generated_macros/cv_test_enhanced.atlas")
    test_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_macro)
    
    print(f"📝 Создан тестовый макрос: {test_file}")
    
    # Создаем улучшенный исполнитель
    executor = SimpleExecutorEnhanced()
    
    # Выполняем тест
    print("\n🚀 Запуск теста Computer Vision...")
    result = executor.execute_atlas_file(str(test_file))
    
    print(f"\n📊 Результат теста:")
    print(f"   Успех: {result.success}")
    print(f"   Сообщение: {result.message}")
    print(f"   Время: {result.execution_time:.3f}с")
    
    return result.success

if __name__ == "__main__":
    success = test_cv_macro()
    
    if success:
        print("\n✅ Тест Computer Vision прошел успешно!")
    else:
        print("\n❌ Тест Computer Vision не прошел!")
