#!/usr/bin/env python3
"""
Быстрый тест TikTok макроса с улучшенным скроллом
"""

from simple_executor_enhanced import SimpleExecutorEnhanced

def test_tiktok_scroll():
    """Тест только скролла из TikTok макроса"""
    print("🧪 Тестируем TikTok скролл")
    
    # Используем режим продолжения при ошибках
    executor = SimpleExecutorEnhanced(continue_on_error=True)
    
    # Тестируем команды из макроса
    commands = [
        "wait 1s",
        "scroll down center 15",
        "wait 2s",
        "scroll down center 15", 
        "wait 2s",
        "scroll down center 15",
    ]
    
    print(f"📋 Выполняем {len(commands)} команд...")
    
    for i, command in enumerate(commands, 1):
        print(f"\n🔧 Команда {i}/{len(commands)}: {command}")
        result = executor._execute_command(command)
        
        if result.success:
            print(f"   ✅ Успешно: {result.message}")
        else:
            print(f"   ❌ Ошибка: {result.message}")
    
    return True

def main():
    print("🚀 ТЕСТ TIKTOK СКРОЛЛА")
    print("=" * 30)
    print("⚠️  Откройте TikTok в браузере!")
    print()
    
    input("📋 Нажмите Enter для начала...")
    
    test_tiktok_scroll()
    
    print("\n✨ Тест завершен!")
    print("💡 Теперь скролл должен быть более заметным (сила 15)")

if __name__ == "__main__":
    main()
