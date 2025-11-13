#!/usr/bin/env python3
"""
📸 Template Parser - Управление визуальными шаблонами
Сканирование, индексация и организация шаблонов для Computer Vision
"""

import re
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class TemplateInfo:
    """Информация о шаблоне"""
    name: str
    path: str
    size: Tuple[int, int]
    file_size: int
    app: Optional[str]
    element: Optional[str]
    element_type: Optional[str]
    created_at: str
    hash: str
    confidence_threshold: float = 0.8

class TemplateParser:
    """
    Модуль управления визуальными шаблонами
    """
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Инициализация Template Parser
        
        Args:
            templates_dir: Путь к директории с шаблонами
        """
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Индекс шаблонов
        self.template_index = {}
        self.name_mapping = {}
        
        # Поддерживаемые форматы
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
        
        # Настройка логгера
        try:
            from core.logger import get_logger
            self.logger = get_logger("template_parser")
        except ImportError:
            import logging
            self.logger = logging.getLogger("template_parser")
        
        # Загружаем существующий индекс
        self._load_index()
        
        self.logger.info("📸 TemplateParser инициализирован")
    
    def handle(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Обработка запроса к модулю
        
        Args:
            user_input: Ввод пользователя
            context: Контекст выполнения
            
        Returns:
            Результат обработки
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"📸 Обработка запроса: {user_input[:50]}...")
            
            # Определяем тип запроса
            if self._is_scan_request(user_input):
                return self._handle_scan_request(user_input, context, start_time)
            elif self._is_create_request(user_input):
                return self._handle_create_request(user_input, context, start_time)
            elif self._is_search_request(user_input):
                return self._handle_search_request(user_input, context, start_time)
            elif self._is_info_request(user_input):
                return self._handle_info_request(user_input, context, start_time)
            else:
                return self._format_error_response("Неизвестный тип запроса", start_time)
        
        except Exception as e:
            self.logger.exception(f"❌ Ошибка обработки: {e}")
            return self._format_error_response(str(e), start_time)
    
    def _is_scan_request(self, user_input: str) -> bool:
        """Проверка запроса на сканирование"""
        scan_keywords = ['сканируй', 'обнови', 'индексируй', 'scan', 'update', 'index']
        return any(keyword in user_input.lower() for keyword in scan_keywords)
    
    def _is_create_request(self, user_input: str) -> bool:
        """Проверка запроса на создание шаблона"""
        create_keywords = ['создай шаблон', 'create template', 'новый шаблон', 'добавь шаблон']
        return any(keyword in user_input.lower() for keyword in create_keywords)
    
    def _is_search_request(self, user_input: str) -> bool:
        """Проверка запроса на поиск шаблонов"""
        search_keywords = ['найди шаблон', 'find template', 'поищи', 'список шаблонов']
        return any(keyword in user_input.lower() for keyword in search_keywords)
    
    def _is_info_request(self, user_input: str) -> bool:
        """Проверка запроса на информацию"""
        info_keywords = ['информация', 'статистика', 'info', 'stats', 'сколько шаблонов']
        return any(keyword in user_input.lower() for keyword in info_keywords)
    
    def _handle_scan_request(self, user_input: str, context: Optional[Dict[str, Any]], 
                           start_time: datetime) -> Dict[str, Any]:
        """Обработка запроса на сканирование"""
        try:
            # Сканируем директорию шаблонов
            scan_result = self.scan_templates()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "result": f"Сканирование завершено: найдено {scan_result['total']} шаблонов",
                "scan_info": scan_result,
                "execution_time": execution_time,
                "metadata": {
                    "module": "template_parser",
                    "action": "scan"
                }
            }
        
        except Exception as e:
            return self._format_error_response(f"Ошибка сканирования: {e}", start_time)
    
    def _handle_create_request(self, user_input: str, context: Optional[Dict[str, Any]], 
                             start_time: datetime) -> Dict[str, Any]:
        """Обработка запроса на создание шаблона"""
        try:
            # Извлекаем информацию о шаблоне из запроса
            template_info = self._extract_template_info(user_input)
            
            # Генерируем имя шаблона
            suggested_name = self._generate_template_name(
                template_info.get('app'),
                template_info.get('element'),
                template_info.get('type')
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "result": f"Предложено имя шаблона: {suggested_name}",
                "template_info": template_info,
                "suggested_name": suggested_name,
                "execution_time": execution_time,
                "metadata": {
                    "module": "template_parser",
                    "action": "create_suggestion"
                }
            }
        
        except Exception as e:
            return self._format_error_response(f"Ошибка создания шаблона: {e}", start_time)
    
    def _handle_search_request(self, user_input: str, context: Optional[Dict[str, Any]], 
                             start_time: datetime) -> Dict[str, Any]:
        """Обработка запроса на поиск шаблонов"""
        try:
            # Извлекаем поисковый запрос
            search_query = self._extract_search_query(user_input)
            
            # Ищем шаблоны
            found_templates = self.search_templates(search_query)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "result": f"Найдено {len(found_templates)} шаблонов по запросу: {search_query}",
                "templates": found_templates,
                "search_query": search_query,
                "execution_time": execution_time,
                "metadata": {
                    "module": "template_parser",
                    "action": "search"
                }
            }
        
        except Exception as e:
            return self._format_error_response(f"Ошибка поиска: {e}", start_time)
    
    def _handle_info_request(self, user_input: str, context: Optional[Dict[str, Any]], 
                           start_time: datetime) -> Dict[str, Any]:
        """Обработка запроса на информацию"""
        try:
            stats = self.get_statistics()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "result": f"Статистика шаблонов: {stats['total']} файлов в {stats['apps']} приложениях",
                "statistics": stats,
                "execution_time": execution_time,
                "metadata": {
                    "module": "template_parser",
                    "action": "info"
                }
            }
        
        except Exception as e:
            return self._format_error_response(f"Ошибка получения информации: {e}", start_time)
    
    def scan_templates(self) -> Dict[str, Any]:
        """
        Сканирование директории шаблонов
        
        Returns:
            Результат сканирования
        """
        self.logger.info("🔍 Сканирование шаблонов...")
        
        scanned = 0
        new_templates = 0
        updated_templates = 0
        
        # Сканируем все изображения
        for image_file in self.templates_dir.rglob("*"):
            if image_file.suffix.lower() in self.supported_formats:
                try:
                    template_info = self._analyze_template(image_file)
                    
                    if template_info.name not in self.template_index:
                        new_templates += 1
                    else:
                        # Проверяем изменения
                        existing = self.template_index[template_info.name]
                        if existing.hash != template_info.hash:
                            updated_templates += 1
                    
                    self.template_index[template_info.name] = template_info
                    self._update_name_mapping(template_info)
                    
                    scanned += 1
                
                except Exception as e:
                    self.logger.warning(f"⚠️ Ошибка анализа {image_file}: {e}")
        
        # Сохраняем индекс
        self._save_index()
        
        result = {
            "total": scanned,
            "new": new_templates,
            "updated": updated_templates,
            "apps": len(self._get_apps_list()),
            "directory": str(self.templates_dir)
        }
        
        self.logger.info(f"✅ Сканирование завершено: {result}")
        return result
    
    def _analyze_template(self, image_path: Path) -> TemplateInfo:
        """Анализ шаблона и извлечение метаданных"""
        try:
            # Ленивый импорт PIL
            from PIL import Image
            
            # Получаем информацию о файле
            stat = image_path.stat()
            
            # Открываем изображение для получения размеров
            with Image.open(image_path) as img:
                size = img.size
            
            # Вычисляем хэш файла
            file_hash = self._calculate_file_hash(image_path)
            
            # Парсим имя файла
            app, element, element_type = self._parse_filename(image_path.stem)
            
            return TemplateInfo(
                name=image_path.stem,
                path=str(image_path),
                size=size,
                file_size=stat.st_size,
                app=app,
                element=element,
                element_type=element_type,
                created_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                hash=file_hash
            )
        
        except Exception as e:
            self.logger.error(f"❌ Ошибка анализа шаблона {image_path}: {e}")
            raise
    
    def _parse_filename(self, filename: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Парсинг имени файла для извлечения компонентов
        
        Args:
            filename: Имя файла без расширения
            
        Returns:
            (app, element, type)
        """
        # Паттерны именования
        patterns = [
            r'^([A-Za-z]+)-([A-Za-z0-9]+)-([a-z]+)$',  # Chrome-NewTab-btn
            r'^([A-Za-z]+)-([A-Za-z0-9]+)$',           # Chrome-NewTab
            r'^([A-Za-z]+)([A-Z][a-z]+)([A-Z][a-z]+)$', # ChromeNewTabBtn
        ]
        
        for pattern in patterns:
            match = re.match(pattern, filename)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    return groups[0], groups[1], groups[2]
                elif len(groups) == 2:
                    return groups[0], groups[1], None
        
        # Если паттерн не подошел, пробуем извлечь приложение
        app_keywords = ['chrome', 'safari', 'firefox', 'calculator', 'finder', 'youtube', 'google']
        
        filename_lower = filename.lower()
        for app in app_keywords:
            if app in filename_lower:
                return app.capitalize(), filename.replace(app, '').replace('-', '').replace('_', ''), None
        
        return None, filename, None
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Вычисление хэша файла"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _update_name_mapping(self, template_info: TemplateInfo):
        """Обновление маппинга имен для быстрого поиска"""
        name = template_info.name
        
        # Добавляем различные варианты имени
        self.name_mapping[name.lower()] = name
        
        # Без дефисов и подчеркиваний
        clean_name = name.replace('-', '').replace('_', '').lower()
        self.name_mapping[clean_name] = name
        
        # По компонентам
        if template_info.app:
            app_key = template_info.app.lower()
            if app_key not in self.name_mapping:
                self.name_mapping[app_key] = []
            if isinstance(self.name_mapping[app_key], str):
                self.name_mapping[app_key] = [self.name_mapping[app_key]]
            if name not in self.name_mapping[app_key]:
                self.name_mapping[app_key].append(name)
    
    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """
        Поиск шаблонов по запросу
        
        Args:
            query: Поисковый запрос
            
        Returns:
            Список найденных шаблонов
        """
        query_lower = query.lower()
        found = []
        
        for name, template_info in self.template_index.items():
            # Поиск по имени
            if query_lower in name.lower():
                found.append(asdict(template_info))
                continue
            
            # Поиск по приложению
            if template_info.app and query_lower in template_info.app.lower():
                found.append(asdict(template_info))
                continue
            
            # Поиск по элементу
            if template_info.element and query_lower in template_info.element.lower():
                found.append(asdict(template_info))
                continue
        
        return found
    
    def _generate_template_name(self, app: Optional[str], element: Optional[str], 
                              element_type: Optional[str]) -> str:
        """
        Генерация имени шаблона
        
        Args:
            app: Приложение
            element: Элемент
            element_type: Тип элемента
            
        Returns:
            Предложенное имя шаблона
        """
        parts = []
        
        if app:
            parts.append(app.capitalize())
        
        if element:
            parts.append(element.capitalize())
        
        if element_type:
            parts.append(element_type.lower())
        
        if not parts:
            # Генерируем имя по времени
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"Template_{timestamp}"
        
        return "-".join(parts)
    
    def _extract_template_info(self, user_input: str) -> Dict[str, Any]:
        """Извлечение информации о шаблоне из запроса"""
        info = {}
        
        # Ищем приложение
        app_patterns = [
            r'(chrome|safari|firefox|calculator|finder|youtube|google)',
            r'для ([a-zA-Z]+)',
            r'в ([a-zA-Z]+)'
        ]
        
        for pattern in app_patterns:
            match = re.search(pattern, user_input.lower())
            if match:
                info['app'] = match.group(1).capitalize()
                break
        
        # Ищем элемент
        element_patterns = [
            r'кнопк[ау] ([a-zA-Z0-9]+)',
            r'поле ([a-zA-Z0-9]+)',
            r'элемент ([a-zA-Z0-9]+)',
            r'button ([a-zA-Z0-9]+)',
            r'field ([a-zA-Z0-9]+)'
        ]
        
        for pattern in element_patterns:
            match = re.search(pattern, user_input.lower())
            if match:
                info['element'] = match.group(1).capitalize()
                break
        
        # Определяем тип
        if 'кнопк' in user_input.lower() or 'button' in user_input.lower():
            info['type'] = 'btn'
        elif 'поле' in user_input.lower() or 'field' in user_input.lower():
            info['type'] = 'field'
        elif 'иконк' in user_input.lower() or 'icon' in user_input.lower():
            info['type'] = 'icon'
        
        return info
    
    def _extract_search_query(self, user_input: str) -> str:
        """Извлечение поискового запроса"""
        # Убираем служебные слова
        query = user_input.lower()
        
        remove_words = ['найди', 'шаблон', 'шаблоны', 'find', 'template', 'templates', 'поищи']
        for word in remove_words:
            query = query.replace(word, '')
        
        return query.strip()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики шаблонов"""
        apps = self._get_apps_list()
        
        total_size = sum(template.file_size for template in self.template_index.values())
        
        return {
            "total": len(self.template_index),
            "apps": len(apps),
            "apps_list": apps,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "directory": str(self.templates_dir),
            "supported_formats": list(self.supported_formats)
        }
    
    def _get_apps_list(self) -> List[str]:
        """Получение списка приложений"""
        apps = set()
        for template in self.template_index.values():
            if template.app:
                apps.add(template.app)
        return sorted(list(apps))
    
    def _load_index(self):
        """Загрузка индекса шаблонов"""
        index_file = self.templates_dir / "template_index.json"
        
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for name, template_data in data.items():
                    template_info = TemplateInfo(**template_data)
                    self.template_index[name] = template_info
                    self._update_name_mapping(template_info)
                
                self.logger.debug(f"📋 Загружен индекс: {len(self.template_index)} шаблонов")
            
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка загрузки индекса: {e}")
    
    def _save_index(self):
        """Сохранение индекса шаблонов"""
        index_file = self.templates_dir / "template_index.json"
        
        try:
            data = {}
            for name, template_info in self.template_index.items():
                data[name] = asdict(template_info)
            
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.debug(f"💾 Индекс сохранен: {len(self.template_index)} шаблонов")
        
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения индекса: {e}")
    
    def _format_error_response(self, error: str, start_time: datetime) -> Dict[str, Any]:
        """Форматирование ответа об ошибке"""
        return {
            "success": False,
            "error": error,
            "execution_time": (datetime.now() - start_time).total_seconds(),
            "metadata": {
                "module": "template_parser",
                "type": "error"
            }
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Информация о модуле"""
        return {
            "name": "template_parser",
            "description": "Модуль управления визуальными шаблонами",
            "version": "1.0.0",
            "templates_count": len(self.template_index),
            "apps_count": len(self._get_apps_list()),
            "supported_formats": list(self.supported_formats),
            "templates_directory": str(self.templates_dir),
            "status": "ready"
        }

# Пример использования
if __name__ == "__main__":
    parser = TemplateParser()
    
    test_requests = [
        "сканируй шаблоны",
        "найди шаблоны Chrome",
        "создай шаблон для кнопки YouTube Play",
        "статистика шаблонов"
    ]
    
    print("🧪 Тестирование TemplateParser")
    print("=" * 60)
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n{i}. Запрос: '{request}'")
        
        result = parser.handle(request)
        
        if result["success"]:
            print(f"   ✅ Успех: {result['result']}")
            print(f"   ⚡ Время: {result['execution_time']:.3f}с")
        else:
            print(f"   ❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
    
    print(f"\n📊 Информация о модуле:")
    info = parser.get_info()
    print(f"   Шаблонов: {info['templates_count']}")
    print(f"   Приложений: {info['apps_count']}")
    print(f"   Директория: {info['templates_directory']}")
    
    print("\n📸 TemplateParser готов к работе!")
