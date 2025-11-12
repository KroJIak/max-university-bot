#!/usr/bin/env python3
"""
Скраппер для сайта https://dev.max.ru/docs
Скачивает документацию с сохранением структуры директорий
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from pathlib import Path


class MaxDocsScraper:
    def __init__(self, base_url="https://dev.max.ru", output_dir="docs"):
        self.base_url = base_url
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_page(self, url):
        """Получить HTML страницы"""
        try:
            print(f"Загрузка: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Ошибка при загрузке {url}: {e}")
            return None
    
    def find_main_tabs(self, html):
        """Найти основные вкладки в навигации"""
        soup = BeautifulSoup(html, 'html.parser')
        main_tabs = []
        target_tabs = ['Документация', 'API', 'MAX UI']
        found_tabs = set()
        
        # Ищем навигацию сверху (обычно это nav или header)
        nav = soup.find('nav') or soup.find('header')
        if nav:
            # Ищем ссылки на основные разделы
            links = nav.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                # Фильтруем основные вкладки
                if text in target_tabs and text not in found_tabs:
                    full_url = urljoin(self.base_url, href)
                    main_tabs.append({
                        'name': text,
                        'url': full_url,
                        'href': href
                    })
                    found_tabs.add(text)
        
        # Если не нашли все вкладки через nav, ищем по всей странице
        if len(found_tabs) < len(target_tabs):
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                text = link.get_text(strip=True)
                if text in target_tabs and text not in found_tabs:
                    href = link.get('href', '')
                    full_url = urljoin(self.base_url, href)
                    main_tabs.append({
                        'name': text,
                        'url': full_url,
                        'href': href
                    })
                    found_tabs.add(text)
        
        return main_tabs
    
    def parse_sidebar(self, html):
        """Парсинг боковой панели и извлечение структуры"""
        soup = BeautifulSoup(html, 'html.parser')
        sidebar = soup.find('aside')
        
        if not sidebar:
            print("Боковая панель не найдена")
            return []
        
        return self._parse_sidebar_recursive(sidebar)
    
    def _parse_sidebar_recursive(self, element, path=[]):
        """Рекурсивный парсинг элементов боковой панели"""
        items = []
        
        # Обрабатываем прямые дочерние элементы
        for child in element.children:
            if not hasattr(child, 'name') or child.name is None:
                continue
            
            # Если это section с ссылкой - это страница
            if child.name == 'section':
                link = child.find('a', href=True)
                if link:
                    href = link.get('href', '')
                    # Создаем копию для безопасного удаления элементов
                    link_copy = BeautifulSoup(str(link), 'html.parser').find('a')
                    # Убираем div с методом (GET, POST и т.д.)
                    method_div = link_copy.find('div', class_=lambda x: x and 'XCNJPIzn7u' in str(x))
                    if method_div:
                        method_div.decompose()
                    name = link_copy.get_text(strip=True)
                    
                    if name and href:
                        items.append({
                            'type': 'page',
                            'name': name,
                            'href': href,
                            'path': path.copy()
                        })
                continue
            
            # Если это div - проверяем, папка это или элемент
            if child.name == 'div':
                # Проверяем, есть ли внутри section (это значит, что это контейнер)
                has_sections = child.find('section') is not None
                # Проверяем, есть ли прямая ссылка (если есть, это не папка)
                has_direct_link = child.find('a', href=True, recursive=False) is not None
                
                # Если есть вложенные section или другие div'ы без прямой ссылки - это папка
                if has_sections or (child.find('div', recursive=False) and not has_direct_link):
                    # Получаем название папки
                    folder_name = None
                    
                    # Ищем первый div без ссылки - это обычно название папки
                    for sub_div in child.find_all('div', recursive=False):
                        if not sub_div.find('a', href=True):
                            folder_name = sub_div.get_text(strip=True)
                            break
                    
                    # Если не нашли явное название, берем первый текстовый узел
                    if not folder_name:
                        # Получаем весь текст и берем первую непустую строку
                        all_text = child.get_text('\n', strip=True)
                        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                        if lines:
                            folder_name = lines[0]
                    
                    if folder_name:
                        new_path = path + [folder_name]
                        # Рекурсивно парсим содержимое папки
                        nested_items = self._parse_sidebar_recursive(child, new_path)
                        items.extend(nested_items)
                # Если это div с прямой ссылкой - это тоже страница
                elif has_direct_link:
                    link = child.find('a', href=True)
                    if link:
                        href = link.get('href', '')
                        link_copy = BeautifulSoup(str(link), 'html.parser').find('a')
                        method_div = link_copy.find('div', class_=lambda x: x and 'XCNJPIzn7u' in str(x))
                        if method_div:
                            method_div.decompose()
                        name = link_copy.get_text(strip=True)
                        
                        if name and href:
                            items.append({
                                'type': 'page',
                                'name': name,
                                'href': href,
                                'path': path.copy()
                            })
        
        return items
    
    def extract_main_content(self, html):
        """Извлечь только содержимое блока <main> из HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        main_block = soup.find('main')
        
        if main_block:
            # Возвращаем только содержимое main в виде HTML
            return str(main_block)
        else:
            # Если main не найден, возвращаем весь HTML с предупреждением
            print("  ⚠ Блок <main> не найден, сохраняется весь HTML")
            return html
    
    def save_html(self, html, filepath, extract_main=True):
        """Сохранить HTML в файл"""
        dirname = os.path.dirname(filepath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        
        # Извлекаем только содержимое <main>, если требуется
        if extract_main:
            html = self.extract_main_content(html)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Сохранено: {filepath}")
    
    def scrape_tab(self, tab_name, tab_url):
        """Скрапить одну основную вкладку"""
        print(f"\n{'='*60}")
        print(f"Обработка вкладки: {tab_name}")
        print(f"URL: {tab_url}")
        print(f"{'='*60}\n")
        
        # Получаем главную страницу вкладки
        html = self.get_page(tab_url)
        if not html:
            return
        
        # Парсим боковую панель
        sidebar_items = self.parse_sidebar(html)
        
        if not sidebar_items:
            print(f"Не найдено элементов в боковой панели для {tab_name}")
            return
        
        print(f"Найдено элементов: {len(sidebar_items)}")
        
        # Создаем директорию для вкладки
        tab_dir = os.path.join(self.output_dir, tab_name)
        os.makedirs(tab_dir, exist_ok=True)
        
        # Сохраняем главную страницу вкладки
        main_file = os.path.join(tab_dir, 'index.html')
        self.save_html(html, main_file, extract_main=True)
        
        # Скачиваем все страницы
        for idx, item in enumerate(sidebar_items, 1):
            if item['type'] == 'page':
                # Строим путь к файлу
                if item['path']:
                    file_path_parts = item['path'] + [self._sanitize_filename(item['name']) + '.html']
                else:
                    file_path_parts = [self._sanitize_filename(item['name']) + '.html']
                file_path = os.path.join(tab_dir, *file_path_parts)
                
                # Получаем полный URL
                page_url = urljoin(self.base_url, item['href'])
                
                print(f"[{idx}/{len(sidebar_items)}] Скачивание: {item['name']}")
                
                # Скачиваем страницу
                page_html = self.get_page(page_url)
                if page_html:
                    self.save_html(page_html, file_path, extract_main=True)
                else:
                    print(f"  ⚠ Пропущено из-за ошибки загрузки")
                
                # Небольшая задержка, чтобы не перегружать сервер
                time.sleep(0.5)
    
    def _sanitize_filename(self, filename):
        """Очистить имя файла от недопустимых символов"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        # Убираем лишние пробелы
        filename = '_'.join(filename.split())
        return filename[:200]  # Ограничиваем длину
    
    def scrape_all(self):
        """Скрапить весь сайт"""
        print("Начало скраппинга сайта https://dev.max.ru/docs")
        
        # Получаем главную страницу
        main_url = urljoin(self.base_url, '/docs')
        main_html = self.get_page(main_url)
        
        if not main_html:
            print("Не удалось загрузить главную страницу")
            return
        
        # Находим основные вкладки
        main_tabs = self.find_main_tabs(main_html)
        
        if not main_tabs:
            print("Основные вкладки не найдены, используем только /docs")
            main_tabs = [{'name': 'Документация', 'url': main_url, 'href': '/docs'}]
        
        print(f"\nНайдено основных вкладок: {len(main_tabs)}")
        for tab in main_tabs:
            print(f"  - {tab['name']}: {tab['url']}")
        
        # Скрапим каждую вкладку
        for tab in main_tabs:
            self.scrape_tab(tab['name'], tab['url'])
            time.sleep(1)  # Задержка между вкладками
        
        print(f"\n{'='*60}")
        print("Скраппинг завершен!")
        print(f"Результаты сохранены в: {os.path.abspath(self.output_dir)}")
        print(f"{'='*60}")


if __name__ == "__main__":
    scraper = MaxDocsScraper()
    scraper.scrape_all()

