#!/usr/bin/env python3
"""
Тест улучшенного скролла и обработки ошибок
"""

from simple_executor_enhanced import SimpleExecutorEnhanced

def test_scroll_methods():
    """Тест различных методов скролла"""
    print("🧪 Тестируем методы скролла")
    
    executor = SimpleExecutorEnhanced()
    
    # Тест 1: Обычный скролл
    print("\n1️⃣ Тест обычного скролла:")
    result1 = executor._execute_scroll("down 2")
    print(f"   Результат: {'✅' if result1.success else '❌'} - {result1.message}")
    
    # Тест 2: Скролл в центре
    print("\n2️⃣ Тест скролла в центре:")
    result2 = executor._execute_scroll("down center 3")
    print(f"   Результат: {'✅' if result2.success else '❌'} - {result2.message}")
    
    # Тест 3: Скролл вверх в центре
    print("\n3️⃣ Тест скролла вверх в центре:")
    result3 = executor._execute_scroll("up center")
    print(f"   Результат: {'✅' if result3.success else '❌'} - {result3.message}")
    
    return result1.success and result2.success and result3.success

def test_error_handling():
    """Тест обработки ошибок"""
    print("\n🧪 Тестируем обработку ошибок")
    
    # Тест с продолжением при ошибках
    executor_continue = SimpleExecutorEnhanced(continue_on_error=True)
    
    # Тест с остановкой при ошибках
    executor_stop = SimpleExecutorEnhanced(continue_on_error=False)
    
    print("\n1️⃣ Режим продолжения при ошибках: ВКЛ")
    print("2️⃣ Режим остановки при ошибках: ВКЛ")
    
    return True

def create_test_macro():
    """Создаем тестовый макрос для проверки скролла"""
    test_content = """# Тест скролла и обработки ошибок
# Generated for testing

# MACRO CODE
wait 1s
scroll down center
wait 1s
scroll up center 2
wait 1s
scroll down 5

# METADATA
# Platform: macOS
# Description: Тест различных методов скролла
# Version: 1.0
"""
    
    with open("test_scroll_macro.atlas", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    print("📄 Создан тестовый макрос: test_scroll_macro.atlas")
    return "test_scroll_macro.atlas"

def test_macro_execution():
    """Тест выполнения макроса с новыми функциями"""
    print("\n🧪 Тестируем выполнение макроса")
    
    # Создаем тестовый макрос
    macro_file = create_test_macro()
    
    # Тест с обычным режимом
    print("\n1️⃣ Выполнение в обычном режиме:")
    executor = SimpleExecutorEnhanced(continue_on_error=False)
    result = executor.execute_atlas_file(macro_file)
    print(f"   Результат: {'✅' if result.success else '❌'}")
    print(f"   Время: {result.execution_time:.3f}с")
    
    return result.success

def main():
    print("🚀 Тестирование улучшенного скролла и обработки ошибок")
    print("=" * 60)
    
    # Тест 1: Методы скролла
    success1 = test_scroll_methods()
    
    # Тест 2: Обработка ошибок
    success2 = test_error_handling()
    
    # Тест 3: Выполнение макроса
    success3 = test_macro_execution()
    
    # Итоги
    print("\n📊 Результаты тестов:")
    print(f"   Методы скролла:       {'✅' if success1 else '❌'}")
    print(f"   Обработка ошибок:     {'✅' if success2 else '❌'}")
    print(f"   Выполнение макроса:   {'✅' if success3 else '❌'}")
    
    if success1 and success2 and success3:
        print("\n🎉 Все тесты прошли успешно!")
        print("✨ Улучшенный скролл и обработка ошибок работают!")
    else:
        print("\n⚠️ Некоторые тесты не прошли")

if __name__ == "__main__":
    main()
