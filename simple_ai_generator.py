#!/usr/bin/env python3
"""
🤖 Simple AI Generator - Простой генератор .atlas макросов
Использует DSL справочник для создания макросов из естественного языка
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

class SimpleAIGenerator:
    """
    Простой AI генератор .atlas макросов
    """
    
    def __init__(self, dsl_reference_path: str = "data/DSL_REFERENCE.txt"):
        """
        Инициализация генератора
        
        Args:
            dsl_reference_path: Путь к DSL справочнику
        """
        self.dsl_reference_path = Path(dsl_reference_path)
        self.dsl_reference = ""
        self.output_dir = Path("data/generated_macros")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Загружаем DSL справочник
        self._load_dsl_reference()
        
        print("🤖 SimpleAIGenerator инициализирован")
    
    def _load_dsl_reference(self):
        """Загрузка DSL справочника"""
        if self.dsl_reference_path.exists():
            try:
                with open(self.dsl_reference_path, 'r', encoding='utf-8') as f:
                    self.dsl_reference = f.read()
                print(f"📋 DSL справочник загружен: {len(self.dsl_reference)} символов")
            except Exception as e:
                print(f"❌ Ошибка загрузки DSL справочника: {e}")
                self.dsl_reference = self._get_fallback_reference()
        else:
            print(f"⚠️ DSL справочник не найден: {self.dsl_reference_path}")
            self.dsl_reference = self._get_fallback_reference()
    
    def _get_fallback_reference(self) -> str:
        """Базовый DSL справочник если файл не найден"""
        return """
DSL КОМАНДЫ:
- open <template> - открыть приложение
- click <template> - кликнуть по элементу  
- type "text" - ввести текст
- wait 3s - ждать 3 секунды
- press enter - нажать клавишу
- hotkey cmd+c - комбинация клавиш

ДОСТУПНЫЕ ШАБЛОНЫ:
- ChromeApp - иконка Chrome
- ChromeNewTab - кнопка новой вкладки
- ChromeSearchField - поле поиска
- Chrome-YouTube-SearchField - поле поиска YouTube
- Chrome-TikTok-Like - кнопка лайка TikTok
"""
    
    def generate_macro(self, user_request: str, use_ai: bool = False) -> Dict[str, Any]:
        """
        Генерация .atlas макроса
        
        Args:
            user_request: Запрос пользователя
            use_ai: Использовать AI API (пока заглушка)
            
        Returns:
            Результат генерации
        """
        print(f"🎯 Генерация макроса: {user_request[:50]}...")
        
        start_time = datetime.now()
        
        try:
            if use_ai:
                # TODO: Интеграция с реальным AI API
                atlas_code = self._generate_with_ai_api(user_request)
            else:
                # Простая логика на основе ключевых слов
                atlas_code = self._generate_with_keywords(user_request)
            
            if not atlas_code:
                return {
                    "success": False,
                    "error": "Не удалось сгенерировать макрос",
                    "execution_time": (datetime.now() - start_time).total_seconds()
                }
            
            # Сохраняем макрос
            file_path = self._save_macro(atlas_code, user_request)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "atlas_code": atlas_code,
                "file_path": str(file_path),
                "execution_time": execution_time,
                "user_request": user_request,
                "method": "ai_api" if use_ai else "keywords"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
    
    def _generate_with_keywords(self, user_request: str) -> str:
        """
        Генерация макроса на основе ключевых слов
        (простая логика без AI API)
        """
        request_lower = user_request.lower()
        atlas_lines = []
        
        # Заголовок
        atlas_lines.append(f"# Generated Macro")
        atlas_lines.append(f"# Description: {user_request}")
        atlas_lines.append(f"# Generated: {datetime.now().isoformat()}")
        atlas_lines.append("")
        
        # Анализируем запрос и генерируем команды
        
        # 1. Открытие приложений
        if any(word in request_lower for word in ['chrome', 'хром', 'браузер']):
            atlas_lines.append("open ChromeApp")
            atlas_lines.append("wait 2s")
        
        # 2. Новая вкладка
        if any(word in request_lower for word in ['новая вкладка', 'new tab', 'вкладка']):
            atlas_lines.append("click ChromeNewTab")
            atlas_lines.append("wait 1s")
        
        # 3. Поиск
        if any(word in request_lower for word in ['поиск', 'search', 'найди', 'find']):
            atlas_lines.append("click ChromeSearchField")
            atlas_lines.append("wait 1s")
            
            # Извлекаем поисковый запрос
            search_query = self._extract_search_query(user_request)
            if search_query:
                atlas_lines.append(f'type "{search_query}"')
            else:
                atlas_lines.append('type "search query"')
            
            atlas_lines.append("press enter")
            atlas_lines.append("wait 3s")
        
        # 4. YouTube
        if any(word in request_lower for word in ['youtube', 'ютуб', 'видео']):
            if 'поиск' in request_lower or 'search' in request_lower:
                atlas_lines.append("click Chrome-YouTube-SearchField")
                atlas_lines.append("wait 1s")
                
                search_query = self._extract_search_query(user_request)
                if search_query:
                    atlas_lines.append(f'type "{search_query}"')
                else:
                    atlas_lines.append('type "video search"')
                
                atlas_lines.append("press enter")
                atlas_lines.append("wait 3s")
            else:
                # Просто открыть YouTube
                atlas_lines.append("click ChromeSearchField")
                atlas_lines.append("wait 1s")
                atlas_lines.append('type "youtube.com"')
                atlas_lines.append("press enter")
                atlas_lines.append("wait 5s")
        
        # 5. TikTok
        if any(word in request_lower for word in ['tiktok', 'тикток']):
            atlas_lines.append("click ChromeSearchField")
            atlas_lines.append("wait 1s")
            atlas_lines.append('type "tiktok.com"')
            atlas_lines.append("press enter")
            atlas_lines.append("wait 5s")
            
            # Лайки
            if any(word in request_lower for word in ['лайк', 'like', 'поставь лайк']):
                # Извлекаем количество лайков
                like_count = self._extract_number(user_request, default=3)
                atlas_lines.append(f"repeat {like_count}:")
                atlas_lines.append("  click Chrome-TikTok-Like")
                atlas_lines.append("  wait 1.5s")
                atlas_lines.append("  scroll down")
                atlas_lines.append("  wait 2s")
                atlas_lines.append("end")
        
        # 6. Калькулятор
        if any(word in request_lower for word in ['калькулятор', 'calculator', 'посчитай']):
            atlas_lines.append("open Calculator")
            atlas_lines.append("wait 2s")
            
            # Простые вычисления
            numbers = re.findall(r'\d+', user_request)
            if len(numbers) >= 2:
                atlas_lines.append(f"type \"{numbers[0]}\"")
                atlas_lines.append("wait 0.5s")
                
                if '+' in user_request or 'плюс' in request_lower:
                    atlas_lines.append("press +")
                elif '-' in user_request or 'минус' in request_lower:
                    atlas_lines.append("press -")
                elif '*' in user_request or 'умножить' in request_lower:
                    atlas_lines.append("press *")
                elif '/' in user_request or 'разделить' in request_lower:
                    atlas_lines.append("press /")
                else:
                    atlas_lines.append("press +")
                
                atlas_lines.append("wait 0.5s")
                atlas_lines.append(f"type \"{numbers[1]}\"")
                atlas_lines.append("wait 0.5s")
                atlas_lines.append("press enter")
        
        # 7. Общие действия
        if not atlas_lines or len(atlas_lines) <= 4:  # Только заголовок
            # Базовый макрос если ничего не распознали
            atlas_lines.append("# Базовый макрос")
            atlas_lines.append("wait 1s")
            atlas_lines.append("# Добавьте нужные команды")
        
        return "\n".join(atlas_lines)
    
    def _extract_search_query(self, text: str) -> Optional[str]:
        """Извлечение поискового запроса из текста"""
        # Паттерны для поиска
        patterns = [
            r'найди\s+"([^"]+)"',
            r'search\s+"([^"]+)"',
            r'поищи\s+"([^"]+)"',
            r'"([^"]+)"',  # Любой текст в кавычках
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Попробуем извлечь после ключевых слов
        keywords = ['найди', 'search', 'поищи', 'про', 'about']
        text_lower = text.lower()
        
        for keyword in keywords:
            if keyword in text_lower:
                # Берем текст после ключевого слова
                parts = text_lower.split(keyword, 1)
                if len(parts) > 1:
                    query = parts[1].strip()
                    # Убираем лишние слова
                    query = re.sub(r'^(на|в|по|для|about|on|in|for)\s+', '', query)
                    if query and len(query) > 2:
                        return query[:50]  # Ограничиваем длину
        
        return None
    
    def _extract_number(self, text: str, default: int = 1) -> int:
        """Извлечение числа из текста"""
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        
        # Словесные числа
        word_numbers = {
            'один': 1, 'одну': 1, 'one': 1,
            'два': 2, 'две': 2, 'two': 2,
            'три': 3, 'three': 3,
            'четыре': 4, 'four': 4,
            'пять': 5, 'five': 5,
            'десять': 10, 'ten': 10
        }
        
        text_lower = text.lower()
        for word, num in word_numbers.items():
            if word in text_lower:
                return num
        
        return default
    
    def _generate_with_ai_api(self, user_request: str) -> str:
        """
        Генерация с помощью AI API (заглушка)
        
        TODO: Интегрировать с OpenAI/Gemini/Anthropic
        """
        print("🤖 AI API генерация (заглушка)")
        
        # Формируем промпт
        prompt = f"""
Ты - эксперт по созданию .atlas макросов для автоматизации.

DSL СПРАВОЧНИК:
{self.dsl_reference[:2000]}...

ЗАДАЧА: Создай .atlas макрос для запроса: "{user_request}"

ТРЕБОВАНИЯ:
1. Используй только команды из DSL справочника
2. Используй только существующие шаблоны из справочника  
3. Добавь комментарии для понимания
4. Макрос должен быть логичным и выполнимым

ФОРМАТ ОТВЕТА:
```atlas
# Generated Macro
# Description: {user_request}

[ваш код здесь]
```
"""
        
        # TODO: Вызов AI API
        # response = openai.chat.completions.create(...)
        # return extract_atlas_code(response)
        
        # Пока возвращаем результат keyword генерации
        return self._generate_with_keywords(user_request)
    
    def _save_macro(self, atlas_code: str, user_request: str) -> Path:
        """Сохранение макроса в файл"""
        # Генерируем имя файла
        safe_name = re.sub(r'[^\w\s-]', '', user_request)
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        safe_name = safe_name[:30].lower().strip('_')
        
        if not safe_name:
            safe_name = "generated_macro"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_{timestamp}.atlas"
        
        file_path = self.output_dir / filename
        
        # Сохраняем
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(atlas_code)
        
        print(f"💾 Макрос сохранен: {file_path}")
        return file_path
    
    def get_available_templates(self) -> list:
        """Получение списка доступных шаблонов из справочника"""
        templates = []
        
        # Парсим справочник для извлечения имен шаблонов
        lines = self.dsl_reference.split('\n')
        in_templates_section = False
        
        for line in lines:
            if 'ДОСТУПНЫЕ ШАБЛОНЫ' in line or 'AVAILABLE TEMPLATES' in line:
                in_templates_section = True
                continue
            
            if in_templates_section and line.strip().startswith('•'):
                template_name = line.strip()[1:].strip()
                if template_name:
                    templates.append(template_name)
        
        return templates
    
    def validate_atlas_code(self, atlas_code: str) -> Dict[str, Any]:
        """Простая валидация .atlas кода"""
        errors = []
        warnings = []
        
        lines = atlas_code.split('\n')
        available_templates = self.get_available_templates()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            # Проверяем команды
            if line.startswith('click ') or line.startswith('open '):
                parts = line.split(' ', 1)
                if len(parts) > 1:
                    template = parts[1]
                    if template not in available_templates and not template.startswith('('):
                        warnings.append(f"Строка {i}: Шаблон '{template}' не найден в справочнике")
            
            # Проверяем синтаксис wait
            if line.startswith('wait '):
                duration = line.split(' ', 1)[1] if ' ' in line else ''
                if not re.match(r'^\d+(\.\d+)?(s|ms)$', duration):
                    errors.append(f"Строка {i}: Неверный формат времени '{duration}'. Используйте: 3s, 1.5s, 500ms")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "lines_count": len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        }

# Пример использования
if __name__ == "__main__":
    generator = SimpleAIGenerator()
    
    test_requests = [
        "открой Chrome и найди видео про Python на YouTube",
        "поставь 3 лайка в TikTok",
        "посчитай 25 плюс 17 в калькуляторе",
        "открой новую вкладку в браузере"
    ]
    
    print("🧪 Тестирование SimpleAIGenerator")
    print("=" * 60)
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n{i}. Запрос: '{request}'")
        
        result = generator.generate_macro(request)
        
        if result["success"]:
            print(f"   ✅ Успех: {result['file_path']}")
            print(f"   ⚡ Время: {result['execution_time']:.3f}с")
            print(f"   📝 Код:")
            print("   " + "\n   ".join(result["atlas_code"].split('\n')[:10]))
            if len(result["atlas_code"].split('\n')) > 10:
                print("   ...")
        else:
            print(f"   ❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
    
    print("\n🤖 SimpleAIGenerator готов к работе!")
