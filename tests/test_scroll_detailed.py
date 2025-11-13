#!/usr/bin/env python3
"""
Детальный тест скролла с разными параметрами
"""

import time
from simple_executor_enhanced import SimpleExecutorEnhanced

def test_scroll_strength():
    """Тест разной силы скролла"""
    print("🧪 Тестируем силу скролла")
    
    executor = SimpleExecutorEnhanced()
    
    strengths = [1, 3, 5, 10, 20]
    
    for strength in strengths:
        print(f"\n📜 Тест скролла с силой {strength}:")
        result = executor._execute_scroll(f"down {strength}")
        print(f"   Результат: {'✅' if result.success else '❌'} - {result.message}")
        time.sleep(1)  # Пауза между тестами
    
    return True

def test_scroll_methods_manual():
    """Ручной тест разных методов скролла"""
    print("\n🧪 Тестируем разные методы скролла вручную")
    
    try:
        import pyautogui
        
        print("\n1️⃣ PyAutoGUI scroll(5):")
        pyautogui.scroll(5)
        time.sleep(2)
        
        print("2️⃣ PyAutoGUI scroll(-5):")
        pyautogui.scroll(-5)
        time.sleep(2)
        
        print("3️⃣ PyAutoGUI scroll(10):")
        pyautogui.scroll(10)
        time.sleep(2)
        
        print("✅ Ручные тесты PyAutoGUI завершены")
        
    except Exception as e:
        print(f"❌ Ошибка PyAutoGUI: {e}")
    
    # Тест AppleScript
    print("\n4️⃣ Тест AppleScript scroll:")
    try:
        import subprocess
        # Скролл через AppleScript
        script = 'tell application "System Events" to scroll 5'
        subprocess.run(['osascript', '-e', script], check=True)
        print("✅ AppleScript scroll работает")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Ошибка AppleScript: {e}")
    
    # Тест клавиш стрелок
    print("\n5️⃣ Тест клавиш стрелок:")
    try:
        import subprocess
        # Нажимаем стрелку вниз 3 раза
        for i in range(3):
            subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 125'], check=True)
            time.sleep(0.5)
        print("✅ Клавиши стрелок работают")
    except Exception as e:
        print(f"❌ Ошибка клавиш: {e}")
    
    return True

def test_scroll_with_focus():
    """Тест скролла с фокусом на окне"""
    print("\n🧪 Тестируем скролл с фокусом на активном окне")
    
    try:
        import subprocess
        import pyautogui
        
        # Получаем активное окно
        print("1️⃣ Получаем активное окно...")
        
        # Кликаем в центр экрана для фокуса
        screen_width, screen_height = pyautogui.size()
        center_x, center_y = screen_width // 2, screen_height // 2
        pyautogui.click(center_x, center_y)
        time.sleep(1)
        
        print(f"2️⃣ Клик в центр экрана ({center_x}, {center_y})")
        
        # Пробуем разные методы скролла
        methods = [
            ("PyAutoGUI scroll(10)", lambda: pyautogui.scroll(10)),
            ("PyAutoGUI scroll(-10)", lambda: pyautogui.scroll(-10)),
            ("Page Down key", lambda: subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 121'], check=True)),
            ("Page Up key", lambda: subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 116'], check=True)),
        ]
        
        for name, method in methods:
            print(f"\n3️⃣ Тест: {name}")
            try:
                method()
                print(f"   ✅ {name} выполнен")
                time.sleep(2)
            except Exception as e:
                print(f"   ❌ {name} ошибка: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Общая ошибка теста фокуса: {e}")
        return False

def test_scroll_in_browser():
    """Специальный тест скролла в браузере"""
    print("\n🧪 Тестируем скролл специально для браузера")
    
    try:
        import pyautogui
        import subprocess
        
        # Открываем Chrome если не открыт
        print("1️⃣ Проверяем Chrome...")
        subprocess.run(['open', '-a', 'Google Chrome'], check=False)
        time.sleep(2)
        
        # Кликаем в область контента браузера
        screen_width, screen_height = pyautogui.size()
        browser_x, browser_y = screen_width // 2, screen_height // 2 + 100  # Чуть ниже центра
        pyautogui.click(browser_x, browser_y)
        time.sleep(1)
        
        print(f"2️⃣ Клик в область браузера ({browser_x}, {browser_y})")
        
        # Тестируем разные методы скролла для браузера
        browser_methods = [
            ("Колесо мыши (большое)", lambda: pyautogui.scroll(20)),
            ("Колесо мыши (среднее)", lambda: pyautogui.scroll(10)),
            ("Колесо мыши (малое)", lambda: pyautogui.scroll(5)),
            ("Пробел (Page Down)", lambda: pyautogui.press('space')),
            ("Стрелка вниз x5", lambda: [pyautogui.press('down') for _ in range(5)]),
        ]
        
        for name, method in browser_methods:
            print(f"\n3️⃣ Браузер тест: {name}")
            try:
                method()
                print(f"   ✅ {name} выполнен")
                time.sleep(3)  # Больше времени для наблюдения
            except Exception as e:
                print(f"   ❌ {name} ошибка: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка браузер теста: {e}")
        return False

def main():
    print("🚀 ДЕТАЛЬНОЕ ТЕСТИРОВАНИЕ СКРОЛЛА")
    print("=" * 50)
    print("⚠️  Убедитесь что у вас открыт браузер с контентом для скролла!")
    print("⚠️  Наблюдайте за экраном во время тестов!")
    print()
    
    input("📋 Нажмите Enter когда будете готовы...")
    
    # Тест 1: Сила скролла
    success1 = test_scroll_strength()
    
    # Тест 2: Ручные методы
    success2 = test_scroll_methods_manual()
    
    # Тест 3: Скролл с фокусом
    success3 = test_scroll_with_focus()
    
    # Тест 4: Скролл в браузере
    success4 = test_scroll_in_browser()
    
    # Итоги
    print("\n📊 Результаты тестов:")
    print(f"   Сила скролла:        {'✅' if success1 else '❌'}")
    print(f"   Ручные методы:        {'✅' if success2 else '❌'}")
    print(f"   Скролл с фокусом:     {'✅' if success3 else '❌'}")
    print(f"   Скролл в браузере:    {'✅' if success4 else '❌'}")
    
    print("\n💡 Рекомендации:")
    print("   • Если PyAutoGUI не работает - используйте клавиши")
    print("   • Если нет скролла - проверьте фокус окна")
    print("   • Для TikTok лучше использовать клавиши стрелок")
    print("   • Увеличьте силу скролла до 10-20")

if __name__ == "__main__":
    main()
