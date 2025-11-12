#!/usr/bin/env python3
"""
Скрипт для проверки AJAX запросов на странице personal_data.php

AJAX (Asynchronous JavaScript and XML) - это технология, которая позволяет
загружать данные с сервера без перезагрузки страницы.

Использование:
1. Откройте страницу https://lk.chuvsu.ru/student/personal_data.php в браузере
2. Откройте Developer Tools (F12)
3. Перейдите на вкладку "Network" (Сеть)
4. Обновите страницу (F5)
5. Посмотрите на запросы, особенно те, которые выполняются после загрузки страницы
6. Ищите запросы с типом "xhr" или "fetch" - это AJAX запросы
7. Проверьте ответы этих запросов - там могут быть данные студента

Этот скрипт поможет вам понять, какие запросы выполняются для загрузки данных.
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def check_page_for_ajax_urls(url: str, cookies: dict):
    """Проверяет HTML страницы на наличие AJAX запросов"""
    
    session = requests.Session()
    session.verify = False
    
    # Устанавливаем cookies
    for name, value in cookies.items():
        session.cookies.set(name, value)
    
    print(f"Загрузка страницы: {url}")
    response = session.get(url, timeout=10)
    
    if response.status_code != 200:
        print(f"Ошибка: HTTP {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print("\n=== Поиск AJAX запросов в JavaScript ===\n")
    
    # Ищем все script теги
    scripts = soup.find_all('script')
    print(f"Найдено {len(scripts)} script тегов\n")
    
    ajax_patterns = [
        r'\.ajax\s*\(',
        r'fetch\s*\(',
        r'XMLHttpRequest',
        r'\.get\s*\(',
        r'\.post\s*\(',
        r'axios\.',
        r'http\.',
    ]
    
    ajax_urls = []
    
    for i, script in enumerate(scripts):
        if not script.string:
            continue
        
        script_text = script.string
        
        # Ищем AJAX вызовы
        for pattern in ajax_patterns:
            if re.search(pattern, script_text, re.IGNORECASE):
                print(f"📜 Script #{i+1} содержит AJAX вызовы:")
                print(f"   Паттерн: {pattern}")
                
                # Ищем URL в этом скрипте
                url_patterns = [
                    r'url\s*:\s*["\']([^"\']+)["\']',
                    r'url\s*=\s*["\']([^"\']+)["\']',
                    r'fetch\s*\(\s*["\']([^"\']+)["\']',
                    r'\.get\s*\(\s*["\']([^"\']+)["\']',
                    r'\.post\s*\(\s*["\']([^"\']+)["\']',
                    r'["\']([^"\']*\.php[^"\']*)["\']',
                ]
                
                for url_pattern in url_patterns:
                    matches = re.findall(url_pattern, script_text, re.IGNORECASE)
                    for match in matches:
                        if match not in ajax_urls and ('php' in match or 'api' in match.lower()):
                            ajax_urls.append(match)
                            print(f"   🔗 Найден URL: {match}")
                
                # Показываем контекст вокруг AJAX вызова
                lines = script_text.split('\n')
                for line_num, line in enumerate(lines):
                    if re.search(pattern, line, re.IGNORECASE):
                        start = max(0, line_num - 2)
                        end = min(len(lines), line_num + 3)
                        print(f"   Контекст (строки {start+1}-{end}):")
                        for j in range(start, end):
                            prefix = ">>> " if j == line_num else "    "
                            print(f"   {prefix}{lines[j]}")
                        print()
                break
    
    # Ищем данные в JavaScript переменных
    print("\n=== Поиск данных в JavaScript переменных ===\n")
    
    data_patterns = [
        r'var\s+(\w+)\s*=\s*({[^}]+})',
        r'const\s+(\w+)\s*=\s*({[^}]+})',
        r'let\s+(\w+)\s*=\s*({[^}]+})',
        r'student\s*=\s*({[^}]+})',
        r'data\s*=\s*({[^}]+})',
    ]
    
    for script in scripts:
        if not script.string:
            continue
        
        for pattern in data_patterns:
            matches = re.findall(pattern, script.string, re.IGNORECASE | re.DOTALL)
            for match in matches:
                var_name = match[0] if isinstance(match, tuple) else 'unknown'
                var_value = match[1] if isinstance(match, tuple) else match
                if 'fam' in var_value.lower() or 'name' in var_value.lower():
                    print(f"📊 Найдена переменная: {var_name}")
                    print(f"   Значение: {var_value[:200]}...")
                    print()
    
    # Ищем все input поля
    print("\n=== Все input поля на странице ===\n")
    inputs = soup.find_all('input')
    print(f"Найдено {len(inputs)} input полей:\n")
    
    for inp in inputs:
        inp_id = inp.get('id', '')
        inp_name = inp.get('name', '')
        inp_value = inp.get('value', '')
        inp_type = inp.get('type', '')
        inp_class = inp.get('class', [])
        
        if inp_id or inp_name:
            print(f"  Input: id='{inp_id}', name='{inp_name}', type='{inp_type}'")
            print(f"    value: '{inp_value[:50]}{'...' if len(inp_value) > 50 else ''}'")
            print(f"    class: {inp_class}")
            print()
    
    print("\n=== Рекомендации ===\n")
    print("1. Откройте страницу в браузере с Developer Tools (F12)")
    print("2. Перейдите на вкладку 'Network' (Сеть)")
    print("3. Обновите страницу (F5)")
    print("4. Отфильтруйте запросы по типу 'XHR' или 'Fetch'")
    print("5. Проверьте ответы этих запросов - там могут быть данные студента")
    print("6. Скопируйте URL запроса, который содержит данные")
    print("7. Добавьте этот URL в scraper для прямого получения данных\n")
    
    if ajax_urls:
        print("Найденные потенциальные AJAX URL:")
        for url in ajax_urls:
            print(f"  - {url}")
    else:
        print("⚠️  AJAX URL не найдены в JavaScript. Данные могут быть:")
        print("   - В атрибуте value input полей (но они пустые)")
        print("   - Загружаются через динамический JavaScript после загрузки")
        print("   - Требуют специальных заголовков или параметров")


if __name__ == "__main__":
    # Пример использования
    print("=" * 60)
    print("Проверка AJAX запросов на странице personal_data.php")
    print("=" * 60)
    print()
    print("Для использования этого скрипта:")
    print("1. Укажите URL страницы")
    print("2. Укажите cookies (можно получить из браузера)")
    print()
    print("Или откройте страницу в браузере и используйте Developer Tools:")
    print("- F12 -> Network -> XHR -> Обновите страницу")
    print("- Посмотрите, какие запросы выполняются")
    print("- Проверьте ответы этих запросов")
    print()

