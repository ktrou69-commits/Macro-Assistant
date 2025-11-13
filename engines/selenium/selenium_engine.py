#!/usr/bin/env python3
"""
🌐 Selenium Engine - Веб-автоматизация через браузер
Управление браузером для DOM автоматизации
"""

import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class WebElement:
    """Веб-элемент с информацией"""
    selector: str
    element_type: str
    text: str
    attributes: Dict[str, str]
    position: Dict[str, int]

class SeleniumEngine:
    """
    Движок веб-автоматизации через Selenium
    """
    
    def __init__(self):
        """Инициализация Selenium Engine"""
        # Ленивая загрузка Selenium
        self.webdriver = None
        self.By = None
        self.WebDriverWait = None
        self.EC = None
        self.ActionChains = None
        
        # Состояние драйвера
        self.driver = None
        self.current_url = None
        
        # Настройки
        self.default_timeout = 10
        self.implicit_wait = 5
        
        # Настройка логгера
        try:
            from core.logger import get_logger
            self.logger = get_logger("selenium_engine")
        except ImportError:
            import logging
            self.logger = logging.getLogger("selenium_engine")
        
        self.logger.info("🌐 SeleniumEngine инициализирован")
    
    def _lazy_import_selenium(self):
        """Ленивый импорт Selenium"""
        if self.webdriver is None:
            try:
                from selenium import webdriver
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.common.action_chains import ActionChains
                from selenium.webdriver.chrome.service import Service
                from selenium.webdriver.chrome.options import Options
                
                self.webdriver = webdriver
                self.By = By
                self.WebDriverWait = WebDriverWait
                self.EC = EC
                self.ActionChains = ActionChains
                self.Service = Service
                self.Options = Options
                
                self.logger.debug("📦 Selenium загружен")
            except ImportError:
                raise ImportError("Selenium не установлен. Установите: pip install selenium webdriver-manager")
    
    def init_browser(self, url: str, browser: str = "chrome", headless: bool = False) -> bool:
        """
        Инициализация браузера
        
        Args:
            url: URL для открытия
            browser: Тип браузера (chrome, firefox, safari)
            headless: Запуск в headless режиме
            
        Returns:
            True если инициализация успешна
        """
        try:
            self._lazy_import_selenium()
            
            if self.driver:
                self.logger.warning("⚠️ Браузер уже инициализирован, закрываем предыдущий")
                self.close_browser()
            
            self.logger.info(f"🚀 Инициализация браузера: {browser}")
            
            if browser.lower() == "chrome":
                self.driver = self._init_chrome(headless)
            elif browser.lower() == "firefox":
                self.driver = self._init_firefox(headless)
            elif browser.lower() == "safari":
                self.driver = self._init_safari()
            else:
                raise ValueError(f"Неподдерживаемый браузер: {browser}")
            
            # Настройки драйвера
            self.driver.implicitly_wait(self.implicit_wait)
            self.driver.maximize_window()
            
            # Открываем URL
            self.driver.get(url)
            self.current_url = url
            
            self.logger.info(f"✅ Браузер открыт: {url}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации браузера: {e}")
            return False
    
    def _init_chrome(self, headless: bool = False):
        """Инициализация Chrome драйвера"""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            
            options = self.Options()
            
            if headless:
                options.add_argument("--headless")
            
            # Настройки для стабильности
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            
            # Отключаем уведомления
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0
            }
            options.add_experimental_option("prefs", prefs)
            
            service = self.Service(ChromeDriverManager().install())
            return self.webdriver.Chrome(service=service, options=options)
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации Chrome: {e}")
            # Fallback: попробуем системный chromedriver
            options = self.Options()
            if headless:
                options.add_argument("--headless")
            return self.webdriver.Chrome(options=options)
    
    def _init_firefox(self, headless: bool = False):
        """Инициализация Firefox драйвера"""
        try:
            from webdriver_manager.firefox import GeckoDriverManager
            from selenium.webdriver.firefox.service import Service as FirefoxService
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            
            options = FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            
            service = FirefoxService(GeckoDriverManager().install())
            return self.webdriver.Firefox(service=service, options=options)
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации Firefox: {e}")
            raise
    
    def _init_safari(self):
        """Инициализация Safari драйвера (только macOS)"""
        try:
            return self.webdriver.Safari()
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации Safari: {e}")
            raise
    
    def navigate_to(self, url: str) -> bool:
        """
        Навигация на URL
        
        Args:
            url: URL для перехода
            
        Returns:
            True если переход успешен
        """
        try:
            if not self.driver:
                self.logger.error("❌ Браузер не инициализирован")
                return False
            
            self.driver.get(url)
            self.current_url = url
            self.logger.info(f"🔗 Переход на: {url}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка навигации: {e}")
            return False
    
    def find_element(self, selector: str, timeout: Optional[int] = None) -> Optional[Any]:
        """
        Поиск элемента на странице
        
        Args:
            selector: CSS селектор или XPath
            timeout: Таймаут поиска
            
        Returns:
            Веб-элемент или None
        """
        try:
            if not self.driver:
                self.logger.error("❌ Браузер не инициализирован")
                return None
            
            wait_time = timeout or self.default_timeout
            wait = self.WebDriverWait(self.driver, wait_time)
            
            # Определяем тип селектора
            if selector.startswith("//") or selector.startswith("("):
                # XPath
                element = wait.until(self.EC.presence_of_element_located((self.By.XPATH, selector)))
            else:
                # CSS селектор
                element = wait.until(self.EC.presence_of_element_located((self.By.CSS_SELECTOR, selector)))
            
            self.logger.debug(f"✅ Элемент найден: {selector}")
            return element
            
        except Exception as e:
            self.logger.warning(f"⚠️ Элемент не найден: {selector} - {e}")
            return None
    
    def click_element(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Клик по элементу
        
        Args:
            selector: CSS селектор или XPath
            timeout: Таймаут поиска
            
        Returns:
            True если клик выполнен
        """
        try:
            element = self.find_element(selector, timeout)
            if not element:
                return False
            
            # Ждем пока элемент станет кликабельным
            wait = self.WebDriverWait(self.driver, timeout or self.default_timeout)
            clickable_element = wait.until(self.EC.element_to_be_clickable(element))
            
            # Прокручиваем к элементу
            self.driver.execute_script("arguments[0].scrollIntoView(true);", clickable_element)
            time.sleep(0.5)
            
            # Кликаем
            clickable_element.click()
            
            self.logger.info(f"🖱️ Клик по элементу: {selector}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка клика: {selector} - {e}")
            return False
    
    def type_text(self, selector: str, text: str, clear: bool = True, timeout: Optional[int] = None) -> bool:
        """
        Ввод текста в элемент
        
        Args:
            selector: CSS селектор или XPath
            text: Текст для ввода
            clear: Очистить поле перед вводом
            timeout: Таймаут поиска
            
        Returns:
            True если ввод выполнен
        """
        try:
            element = self.find_element(selector, timeout)
            if not element:
                return False
            
            # Прокручиваем к элементу
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.3)
            
            # Очищаем поле если нужно
            if clear:
                element.clear()
            
            # Вводим текст
            element.send_keys(text)
            
            self.logger.info(f"⌨️ Ввод текста в {selector}: {text}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка ввода текста: {selector} - {e}")
            return False
    
    def get_element_text(self, selector: str, timeout: Optional[int] = None) -> Optional[str]:
        """
        Получение текста элемента
        
        Args:
            selector: CSS селектор или XPath
            timeout: Таймаут поиска
            
        Returns:
            Текст элемента или None
        """
        try:
            element = self.find_element(selector, timeout)
            if not element:
                return None
            
            text = element.text.strip()
            self.logger.debug(f"📝 Текст элемента {selector}: {text}")
            return text
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения текста: {selector} - {e}")
            return None
    
    def wait_for_element(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Ожидание появления элемента
        
        Args:
            selector: CSS селектор или XPath
            timeout: Таймаут ожидания
            
        Returns:
            True если элемент появился
        """
        element = self.find_element(selector, timeout)
        return element is not None
    
    def execute_script(self, script: str, *args) -> Any:
        """
        Выполнение JavaScript кода
        
        Args:
            script: JavaScript код
            *args: Аргументы для скрипта
            
        Returns:
            Результат выполнения скрипта
        """
        try:
            if not self.driver:
                self.logger.error("❌ Браузер не инициализирован")
                return None
            
            result = self.driver.execute_script(script, *args)
            self.logger.debug(f"🔧 Выполнен скрипт: {script[:50]}...")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка выполнения скрипта: {e}")
            return None
    
    def take_screenshot(self, file_path: Optional[str] = None) -> Optional[str]:
        """
        Создание скриншота страницы
        
        Args:
            file_path: Путь для сохранения (опционально)
            
        Returns:
            Путь к сохраненному файлу
        """
        try:
            if not self.driver:
                self.logger.error("❌ Браузер не инициализирован")
                return None
            
            if not file_path:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"data/screenshots/selenium_{timestamp}.png"
            
            # Создаем директорию
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Делаем скриншот
            self.driver.save_screenshot(file_path)
            
            self.logger.info(f"📸 Скриншот сохранен: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания скриншота: {e}")
            return None
    
    def get_page_info(self) -> Dict[str, Any]:
        """Получение информации о текущей странице"""
        try:
            if not self.driver:
                return {"error": "Браузер не инициализирован"}
            
            return {
                "url": self.driver.current_url,
                "title": self.driver.title,
                "window_size": self.driver.get_window_size(),
                "cookies_count": len(self.driver.get_cookies()),
                "page_source_length": len(self.driver.page_source)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def close_browser(self):
        """Закрытие браузера"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.current_url = None
                self.logger.info("🔒 Браузер закрыт")
        except Exception as e:
            self.logger.error(f"❌ Ошибка закрытия браузера: {e}")

# Пример использования
if __name__ == "__main__":
    engine = SeleniumEngine()
    
    print("🧪 Тестирование SeleniumEngine")
    print("=" * 50)
    
    try:
        # Инициализация браузера
        if engine.init_browser("https://www.google.com"):
            print("✅ Браузер инициализирован")
            
            # Информация о странице
            info = engine.get_page_info()
            print(f"📄 Страница: {info.get('title', 'N/A')}")
            
            # Поиск элемента
            search_box = engine.find_element("textarea[name='q']")
            if search_box:
                print("✅ Поле поиска найдено")
                
                # Ввод текста
                if engine.type_text("textarea[name='q']", "Selenium automation"):
                    print("✅ Текст введен")
                
                # Клик по кнопке поиска
                if engine.click_element("input[name='btnK']"):
                    print("✅ Поиск выполнен")
                else:
                    print("⚠️ Кнопка поиска не найдена")
            
            # Скриншот
            screenshot = engine.take_screenshot()
            if screenshot:
                print(f"📸 Скриншот: {screenshot}")
            
            # Ждем немного
            time.sleep(2)
            
            # Закрываем браузер
            engine.close_browser()
            print("🔒 Браузер закрыт")
        
        else:
            print("❌ Не удалось инициализировать браузер")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n🌐 SeleniumEngine готов к работе!")
