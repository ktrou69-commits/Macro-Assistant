#!/usr/bin/env python3
"""
Тест новых команд: repeat и scroll down center
"""

from simple_executor_enhanced import SimpleExecutorEnhanced

def test_scroll_center():
    """Тест команды scroll down center"""
    print("🧪 Тестируем команду 'scroll down center'")
    
    executor = SimpleExecutorEnhanced()
    result = executor._execute_scroll("down center")
    
    print(f"✅ Результат: {result.success}")
    print(f"📝 Сообщение: {result.message}")
    return result.success

def test_repeat():
    """Тест команды repeat"""
    print("🧪 Тестируем команду 'repeat 5:'")
    
    executor = SimpleExecutorEnhanced()
    result = executor._execute_repeat("5:")
    
    print(f"✅ Результат: {result.success}")
    print(f"📝 Сообщение: {result.message}")
    return result.success

def main():
    print("🚀 Тестирование новых команд")
    print("=" * 50)
    
    # Тест 1: scroll down center
    success1 = test_scroll_center()
    print()
    
    # Тест 2: repeat
    success2 = test_repeat()
    print()
    
    # Итоги
    print("📊 Результаты тестов:")
    print(f"   scroll down center: {'✅' if success1 else '❌'}")
    print(f"   repeat 5:          {'✅' if success2 else '❌'}")
    
    if success1 and success2:
        print("🎉 Все тесты прошли успешно!")
    else:
        print("⚠️ Некоторые тесты не прошли")

if __name__ == "__main__":
    main()
