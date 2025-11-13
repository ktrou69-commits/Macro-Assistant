#!/usr/bin/env python3
"""
Тест улучшенного скролла
"""

from simple_executor_enhanced import SimpleExecutorEnhanced
import time

def test_enhanced_scroll():
    """Тест улучшенного скролла с разными методами"""
    print("🧪 Тестируем улучшенный скролл")
    
    executor = SimpleExecutorEnhanced()
    
    tests = [
        ("scroll down center", "Скролл вниз в центре (сила 10)"),
        ("scroll down center 5", "Скролл вниз в центре (сила 5)"),
        ("scroll down center 20", "Скролл вниз в центре (сила 20)"),
        ("scroll up center", "Скролл вверх в центре"),
    ]
    
    for command, description in tests:
        print(f"\n📜 {description}:")
        print(f"   Команда: {command}")
        
        result = executor._execute_scroll(command.replace("scroll ", ""))
        print(f"   Результат: {'✅' if result.success else '❌'} - {result.message}")
        
        time.sleep(3)  # Пауза для наблюдения
    
    return True

def main():
    print("🚀 ТЕСТ УЛУЧШЕННОГО СКРОЛЛА")
    print("=" * 40)
    print("⚠️  Откройте браузер с длинной страницей!")
    print("⚠️  Наблюдайте за экраном!")
    print()
    
    input("📋 Нажмите Enter для начала...")
    
    test_enhanced_scroll()
    
    print("\n✨ Тест завершен!")
    print("💡 Если скролл не работает, проверьте:")
    print("   • Активное окно с контентом")
    print("   • Права доступности для Terminal")
    print("   • Фокус на прокручиваемой области")

if __name__ == "__main__":
    main()
