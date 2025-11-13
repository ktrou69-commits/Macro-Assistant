# 🚀 Macro-Assistant - Идеальная Архитектура

## 📁 Структура Проекта

```
Macro-Assistant/
├── 📋 README.md                           # Главная документация
├── 📄 LICENSE                             # MIT License
├── ⚙️ pyproject.toml                      # Современная конфигурация Python
├── 🐳 docker-compose.yml                  # Контейнеризация
├── 🔧 .env.example                        # Пример переменных окружения
│
├── 📚 docs/                               # Документация
│   ├── architecture.md                    # Архитектура системы
│   ├── api-reference.md                   # API справочник
│   ├── user-guide.md                      # Руководство пользователя
│   └── development.md                     # Руководство разработчика
│
├── 🧠 core/                               # Ядро системы
│   ├── __init__.py
│   ├── main.py                            # Точка входа
│   ├── ai_router.py                       # 🎯 Умный роутер запросов
│   ├── context_manager.py                 # 💾 Управление контекстом
│   ├── dsl_engine.py                      # 🔧 DSL парсер и исполнитель
│   ├── executor.py                        # ⚡ Исполнитель команд
│   ├── logger.py                          # 📝 Централизованное логирование
│   └── config.py                          # ⚙️ Конфигурация
│
├── 🧩 modules/                            # Модульная система
│   ├── __init__.py
│   ├── base_module.py                     # 🏗️ Базовый класс модуля
│   │
│   ├── 🎭 macro_generator/                # ГЛАВНЫЙ МОДУЛЬ
│   │   ├── __init__.py
│   │   ├── main.py                        # Логика генерации
│   │   ├── prompts/
│   │   │   ├── base_prompt.txt            # Базовый промпт (2-3K tokens)
│   │   │   ├── dsl_reference.txt          # Автогенерируемый DSL справочник
│   │   │   ├── templates_overview.txt     # Список шаблонов
│   │   │   └── examples.txt               # Примеры для Few-Shot Learning
│   │   ├── rules/
│   │   │   ├── pause_rules.json           # Правила пауз
│   │   │   ├── naming_rules.json          # Правила именования
│   │   │   └── safety_rules.json          # Правила безопасности
│   │   └── config.json                    # Настройки модуля
│   │
│   ├── 🏗️ structure_builder/              # Создание архитектуры UI
│   │   ├── main.py
│   │   ├── prompts/base_prompt.txt
│   │   ├── templates/                     # Примеры интерфейсов
│   │   └── config.json
│   │
│   ├── 🔧 variable_creator/               # Создание переменных
│   │   ├── main.py
│   │   ├── prompts/base_prompt.txt
│   │   ├── examples/                      # Примеры переменных
│   │   └── config.json
│   │
│   ├── 🖼️ template_parser/                # Парсинг фото-шаблонов
│   │   ├── main.py
│   │   ├── prompts/base_prompt.txt
│   │   ├── vision_engine.py               # OpenCV обработка
│   │   └── config.json
│   │
│   ├── 🌐 selector_creator/               # DOM селекторы
│   │   ├── main.py
│   │   ├── prompts/base_prompt.txt
│   │   ├── examples/
│   │   │   ├── youtube_selectors.json
│   │   │   ├── tiktok_selectors.json
│   │   │   └── chrome_selectors.json
│   │   └── config.json
│   │
│   └── 📋 module_template/                # Шаблон для новых модулей
│       ├── main.py
│       ├── prompts/base_prompt.txt
│       └── config.json
│
├── 🎨 templates/                          # Визуальные шаблоны
│   ├── Chrome/
│   │   ├── ChromeBasicGuiButtons/
│   │   │   ├── ChromeApp-btn.png          # Запуск Chrome
│   │   │   ├── ChromeNewTab-btn.png       # Новая вкладка
│   │   │   └── ChromeSearchField-btn.png  # Адресная строка
│   │   └── YouTube/
│   │       ├── Chrome-YouTube-Search.png
│   │       └── Chrome-YouTube-Like.png
│   ├── TikTok/
│   └── index.db                           # SQLite индекс шаблонов
│
├── 🗄️ data/                               # Данные системы
│   ├── cache/                             # Кэш результатов
│   ├── logs/                              # Логи выполнения
│   ├── history/                           # История команд
│   ├── variables/                         # Сохраненные переменные
│   └── selectors/                         # DOM селекторы
│
├── 🎮 ui/                                 # Пользовательский интерфейс
│   ├── gui/
│   │   ├── main.py                        # Главное окно
│   │   ├── components/                    # UI компоненты
│   │   └── styles/                        # Стили интерфейса
│   ├── voice/
│   │   ├── listener.py                    # "Эй макро" активация
│   │   ├── speech_to_text.py              # Распознавание речи
│   │   └── text_to_speech.py              # Синтез речи
│   └── cli/
│       └── main.py                        # CLI интерфейс
│
├── 🧪 tests/                              # Тестирование
│   ├── unit/                              # Юнит тесты
│   ├── integration/                       # Интеграционные тесты
│   ├── e2e/                               # End-to-end тесты
│   └── fixtures/                          # Тестовые данные
│
├── 📦 examples/                           # Примеры использования
│   ├── basic_automation.atlas             # Простые примеры
│   ├── advanced_workflows.atlas           # Сложные сценарии
│   └── voice_commands.md                  # Голосовые команды
│
├── 🔧 scripts/                            # Утилиты
│   ├── setup.sh                           # Установка и настройка
│   ├── build.sh                           # Сборка проекта
│   ├── test.sh                            # Запуск тестов
│   └── deploy.sh                          # Деплой
│
└── 🚀 dist/                               # Готовые сборки
    ├── macos/
    ├── windows/
    └── linux/
```

## 🎯 Ключевые Принципы Архитектуры

### 1. **Модульность**
- Каждый модуль = автономное AI-приложение
- Легко добавлять новые модули
- Стандартизированный интерфейс

### 2. **Скорость (1-3 секунды)**
- Быстрый роутинг по ключевым словам
- Кэширование результатов
- Ленивая загрузка модулей

### 3. **Масштабируемость**
- Модули можно выносить в отдельные процессы
- Горизонтальное масштабирование
- Микросервисная архитектура (опционально)

### 4. **Безопасность**
- Sandbox для выполнения команд
- Whitelist системных команд
- Audit логирование

### 5. **Удобство**
- Минималистичный GUI
- Голосовое управление
- Интуитивный DSL язык
