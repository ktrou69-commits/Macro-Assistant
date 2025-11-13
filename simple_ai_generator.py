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

# AI интеграция
try:
    from dotenv import load_dotenv
    from google import genai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

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
        
        # Автообновление справочника если нужно
        self._auto_update_reference()
        
        # Инициализация AI
        self.ai_client = None
        self.ai_model = None
        self._init_ai()
        
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
    
    def _auto_update_reference(self):
        """Автоматическое обновление DSL справочника из templates"""
        try:
            from pathlib import Path
            import subprocess
            import os
            
            templates_path = Path("templates")
            if not templates_path.exists():
                print("⚠️ Папка templates не найдена, пропускаем автообновление")
                return
            
            # Проверяем есть ли новые файлы в templates
            reference_time = 0
            if self.dsl_reference_path.exists():
                reference_time = self.dsl_reference_path.stat().st_mtime
            
            # Находим самый новый файл в templates
            newest_template_time = 0
            for template_file in templates_path.rglob("*"):
                if template_file.is_file():
                    file_time = template_file.stat().st_mtime
                    if file_time > newest_template_time:
                        newest_template_time = file_time
            
            # Если templates новее справочника - обновляем
            if newest_template_time > reference_time:
                print("🔄 Обнаружены новые шаблоны, обновляем DSL справочник...")
                
                # Запускаем генератор
                result = subprocess.run([
                    "python3", "dsl_reference_generator.py", 
                    "--output", str(self.dsl_reference_path)
                ], capture_output=True, text=True, cwd=Path.cwd())
                
                if result.returncode == 0:
                    print("✅ DSL справочник автоматически обновлен")
                    # Перезагружаем справочник
                    self._load_dsl_reference()
                else:
                    print(f"❌ Ошибка автообновления: {result.stderr}")
            else:
                print("✅ DSL справочник актуален")
                
        except Exception as e:
            print(f"⚠️ Ошибка автообновления DSL справочника: {e}")
    
    def _init_ai(self):
        """Инициализация AI клиента"""
        if not AI_AVAILABLE:
            print("⚠️ AI библиотеки не установлены. Используется keyword-based генерация")
            return
        
        try:
            # Загружаем переменные окружения
            load_dotenv()
            
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                print("⚠️ GEMINI_API_KEY не найден в .env файле")
                return
            
            # Инициализируем клиент
            self.ai_client = genai.Client(api_key=api_key)
            self.ai_model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
            
            print(f"✅ Gemini AI инициализирован: {self.ai_model}")
            
        except Exception as e:
            print(f"❌ Ошибка инициализации AI: {e}")
            self.ai_client = None
    
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
    
    def generate_macro(self, user_request: str, use_ai: Optional[bool] = None) -> Dict[str, Any]:
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
            # Автоматически определяем использование AI
            if use_ai is None:
                use_ai = self.ai_client is not None
            
            if use_ai and self.ai_client:
                # Используем реальный Gemini AI
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
            
            result = {
                "success": True,
                "atlas_code": atlas_code,
                "file_path": str(file_path),
                "execution_time": execution_time,
                "user_request": user_request,
                "method": "ai_api" if use_ai else "keywords"
            }
            
            # Предлагаем сохранить как переменную
            if self._should_offer_variable_save(atlas_code, user_request):
                result["offer_variable_save"] = True
                result["suggested_variable_name"] = self._suggest_variable_name(user_request)
            
            return result
        
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
        
        # 3. Прямой переход на сайт (tiktok.com, youtube.com, etc)
        if any(site in request_lower for site in ['tiktok.com', 'youtube.com', 'google.com', '.com', '.ru']):
            atlas_lines.append("click ChromeSearchField")
            atlas_lines.append("wait 1s")
            
            # Извлекаем URL
            url = self._extract_url(user_request)
            if url:
                atlas_lines.append(f'type "{url}"')
            else:
                atlas_lines.append('type "google.com"')
            
            atlas_lines.append("press enter")
            atlas_lines.append("wait 5s")
        
        # 4. Поиск (только если нет прямого URL)
        elif any(word in request_lower for word in ['поиск', 'search', 'найди', 'find']):
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
    
    def _extract_url(self, text: str) -> str:
        """Извлекает URL из текста"""
        import re
        
        # Ищем явные URL
        url_patterns = [
            r'(tiktok\.com)',
            r'(youtube\.com)', 
            r'(google\.com)',
            r'(github\.com)',
            r'(\w+\.com)',
            r'(\w+\.ru)',
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1)
        
        return ""
    
    def _should_offer_variable_save(self, atlas_code: str, user_request: str) -> bool:
        """Определяет стоит ли предложить сохранить макрос как переменную"""
        # Предлагаем сохранить если:
        # 1. Макрос содержит более 3 команд
        # 2. Есть циклы или сложная логика
        # 3. Запрос содержит ключевые слова для повторного использования
        
        lines = [line.strip() for line in atlas_code.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        # Более 3 команд
        if len(lines) > 3:
            return True
        
        # Есть циклы
        if any('repeat' in line for line in lines):
            return True
        
        # Ключевые слова для повторного использования
        reuse_keywords = ['часто', 'обычно', 'всегда', 'каждый раз', 'постоянно', 'регулярно']
        if any(keyword in user_request.lower() for keyword in reuse_keywords):
            return True
        
        return False
    
    def _suggest_variable_name(self, user_request: str) -> str:
        """Предлагает имя для переменной на основе запроса"""
        # Извлекаем ключевые слова
        words = re.findall(r'\b[а-яё]+\b|\b[a-z]+\b', user_request.lower())
        
        # Фильтруем служебные слова
        stop_words = {'и', 'в', 'на', 'с', 'по', 'для', 'от', 'до', 'из', 'к', 'о', 'у', 'за', 'под', 'над', 'при', 'через', 'между'}
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Берем первые 2-3 слова и делаем CamelCase
        if meaningful_words:
            selected_words = meaningful_words[:3]
            return ''.join(word.capitalize() for word in selected_words)
        
        return "CustomMacro"
    
    def save_as_variable(self, atlas_code: str, user_request: str, variable_name: str = None):
        """Сохраняет макрос как переменную"""
        try:
            from utils.variable_creator import VariableCreator
            
            creator = VariableCreator()
            
            if not variable_name:
                variable_name = self._suggest_variable_name(user_request)
            
            # Очищаем код
            cleaned_code = self._clean_atlas_for_variable(atlas_code)
            
            # Сохраняем переменную
            creator._save_variable(variable_name, user_request, cleaned_code)
            creator._update_dsl_reference()
            
            print(f"✅ Макрос сохранен как переменная ${{{variable_name}}}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка сохранения переменной: {e}")
            return False
    
    def _clean_atlas_for_variable(self, atlas_code: str) -> str:
        """Очищает .atlas код для сохранения как переменная"""
        lines = atlas_code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            # Пропускаем метаданные
            if (line_stripped.startswith("# Generated") or 
                line_stripped.startswith("# Created") or
                line_stripped.startswith("# Description:")):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _generate_with_ai_api(self, user_request: str) -> str:
        """
        Генерация с помощью Gemini AI API
        """
        print("🤖 Gemini AI генерация...")
        
        try:
            # Формируем промпт
            prompt = f"""Ты - эксперт по созданию .atlas макросов для автоматизации macOS.

DSL СПРАВОЧНИК:
{self.dsl_reference}

ЗАДАЧА: Создай .atlas макрос для запроса: "{user_request}"

ТРЕБОВАНИЯ:
1. Используй ТОЛЬКО команды из DSL справочника выше
2. Используй ТОЛЬКО существующие шаблоны из справочника
3. Добавь комментарии для понимания
4. Макрос должен быть логичным и выполнимым
5. НЕ используй несуществующие команды или шаблоны

ВАЖНО: Отвечай ТОЛЬКО кодом .atlas без дополнительных объяснений!

ФОРМАТ ОТВЕТА:
# Generated Macro
# Description: {user_request}

[твой .atlas код здесь]"""

            # Вызов Gemini API
            response = self.ai_client.models.generate_content(
                model=self.ai_model,
                contents=prompt
            )
            
            if response and response.text:
                atlas_code = self._extract_atlas_code(response.text)
                print(f"✅ AI сгенерировал {len(atlas_code.split())} строк кода")
                return atlas_code
            else:
                print("⚠️ AI не вернул результат, используем keyword генерацию")
                return self._generate_with_keywords(user_request)
                
        except Exception as e:
            print(f"❌ Ошибка AI генерации: {e}")
            print("🔄 Переключаемся на keyword генерацию")
            return self._generate_with_keywords(user_request)
    
    def _extract_atlas_code(self, ai_response: str) -> str:
        """Извлечение .atlas кода из ответа AI"""
        try:
            # Убираем markdown блоки если есть
            if '```atlas' in ai_response:
                # Извлекаем код между ```atlas и ```
                start = ai_response.find('```atlas') + 8
                end = ai_response.find('```', start)
                if end != -1:
                    return ai_response[start:end].strip()
            elif '```' in ai_response:
                # Извлекаем код между ``` и ```
                start = ai_response.find('```') + 3
                end = ai_response.find('```', start)
                if end != -1:
                    return ai_response[start:end].strip()
            
            # Если нет markdown блоков, возвращаем весь ответ
            return ai_response.strip()
            
        except Exception as e:
            print(f"⚠️ Ошибка извлечения кода: {e}")
            return ai_response.strip()
    
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
