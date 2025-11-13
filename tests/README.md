# 🧪 Tests

Тесты и примеры для Macro-Assistant v2.0

## 📋 Список Тестов

### Computer Vision
- **`test_cv_enhanced.py`** - тест продвинутого Computer Vision
- **`test_new_commands.py`** - тест команд repeat и scroll center

### Скролл
- **`test_enhanced_scroll.py`** - тест улучшенного скролла
- **`test_scroll_detailed.py`** - детальная диагностика скролла
- **`test_scroll_and_errors.py`** - тест обработки ошибок
- **`test_tiktok_scroll.py`** - специальный тест для TikTok

### Макросы
- **`test_scroll_macro.atlas`** - тестовый макрос скролла

## 🚀 Запуск

```bash
# Тест Computer Vision
python3 tests/test_cv_enhanced.py

# Тест скролла
python3 tests/test_enhanced_scroll.py

# Все тесты
python3 -m pytest tests/ -v
```

## 📊 Результаты

Все тесты должны показывать ✅ для корректной работы системы.
