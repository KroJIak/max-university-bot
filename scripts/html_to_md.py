#!/usr/bin/env python3
"""
Конвертер HTML в Markdown
Конвертирует все HTML файлы из docs/ в Markdown файлы в docs_md/
"""

import os
import re
import shutil
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote
import html2text


class HTMLToMarkdownConverter:
    def __init__(self, source_dir="docs", output_dir="docs_md"):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.html_files = []
        
        # Настройка html2text
        self.h = html2text.HTML2Text()
        self.h.ignore_links = False
        self.h.ignore_images = False
        self.h.body_width = 0  # Не переносить строки
        self.h.unicode_snob = True
        self.h.mark_code = True
        self.h.skip_internal_links = False
        
    def find_html_files(self):
        """Найти все HTML файлы в исходной директории (кроме MAX UI)"""
        for root, dirs, files in os.walk(self.source_dir):
            # Пропускаем папку MAX UI
            if 'MAX UI' in root:
                continue
            for file in files:
                if file.endswith('.html'):
                    html_path = Path(root) / file
                    self.html_files.append(html_path)
        print(f"Найдено HTML файлов: {len(self.html_files)}")
        return self.html_files
    
    def get_relative_path(self, from_file, to_file):
        """Вычислить относительный путь от одного файла к другому"""
        from_dir = from_file.parent
        to_path = to_file
        
        try:
            relative = os.path.relpath(to_path, from_dir)
            # Заменяем обратные слеши на прямые для Markdown
            return relative.replace('\\', '/')
        except ValueError:
            # Если файлы на разных дисках, возвращаем абсолютный путь
            return str(to_path).replace('\\', '/')
    
    def find_html_file_by_path(self, href_path):
        """Найти HTML файл по пути из ссылки"""
        # Пробуем разные варианты пути
        clean_href = href_path.lstrip('/')
        possible_paths = [
            self.source_dir / clean_href,
            self.source_dir / clean_href / 'index.html',
            self.source_dir / f"{clean_href}.html",
        ]
        
        # Если путь начинается с /docs/, убираем /docs
        if href_path.startswith('/docs/'):
            clean_path = href_path[6:]  # Убираем /docs/
            possible_paths.extend([
                self.source_dir / clean_path,
                self.source_dir / clean_path / 'index.html',
                self.source_dir / f"{clean_path}.html",
            ])
        
        for path in possible_paths:
            if path.exists() and path.is_file():
                return path
        
        return None
    
    def convert_link(self, href, current_file_path):
        """Конвертировать ссылку в относительный путь для Markdown"""
        if not href:
            return href
        
        # Разделяем href на путь и якорь
        if '#' in href:
            path_part, anchor = href.split('#', 1)
            anchor = '#' + anchor
        else:
            path_part = href
            anchor = ''
        
        # Если это якорная ссылка (начинается с #)
        if not path_part or path_part == '#':
            return href
        
        # Если это внешняя ссылка (http/https)
        if path_part.startswith(('http://', 'https://')):
            return href
        
        # Если это абсолютный путь, начинающийся с /
        if path_part.startswith('/'):
            # Ищем соответствующий HTML файл
            target_html = self.find_html_file_by_path(path_part)
            if target_html:
                # Конвертируем в .md путь
                target_relative = target_html.relative_to(self.source_dir)
                md_path = self.output_dir / str(target_relative).replace('.html', '.md')
                current_md_dir = self.output_dir / current_file_path.parent.relative_to(self.source_dir)
                relative_md = self.get_relative_path(current_md_dir, md_path)
                return relative_md + anchor
            # Если файл не найден, оставляем как есть
            return href
        
        # Относительная ссылка
        # Вычисляем абсолютный путь относительно текущего файла
        current_dir = current_file_path.parent
        target_path = (current_dir / path_part).resolve()
        
        # Проверяем, находится ли целевой файл в исходной директории
        try:
            target_relative = target_path.relative_to(self.source_dir)
            if target_path.exists() and target_path.is_file():
                # Конвертируем в .md путь
                md_path = self.output_dir / str(target_relative).replace('.html', '.md')
                current_md_dir = self.output_dir / current_file_path.parent.relative_to(self.source_dir)
                relative_md = self.get_relative_path(current_md_dir, md_path)
                return relative_md + anchor
        except ValueError:
            pass
        
        return href
    
    def convert_image(self, src, current_file_path):
        """Конвертировать путь к изображению"""
        if not src:
            return src
        
        # Если это внешняя ссылка
        if src.startswith(('http://', 'https://')):
            return src
        
        # Если это абсолютный путь, начинающийся с /
        if src.startswith('/'):
            # Для абсолютных путей (например /assets/...) оставляем как есть
            # так как они обычно указывают на статические ресурсы сайта
            return src
        
        # Относительная ссылка
        current_dir = current_file_path.parent
        img_path = (current_dir / src).resolve()
        
        # Проверяем, находится ли изображение в исходной директории
        try:
            img_relative = img_path.relative_to(self.source_dir)
            if img_path.exists() and img_path.is_file():
                # Копируем изображение в выходную директорию
                target_img = self.output_dir / img_relative
                target_img.parent.mkdir(parents=True, exist_ok=True)
                if not target_img.exists():
                    shutil.copy2(img_path, target_img)
                # Возвращаем относительный путь
                current_md_dir = self.output_dir / current_file_path.parent.relative_to(self.source_dir)
                return self.get_relative_path(current_md_dir, target_img)
        except (ValueError, Exception) as e:
            # Если не удалось обработать, оставляем исходный путь
            pass
        
        return src
    
    def process_html_content(self, html_content, current_file_path):
        """Обработать HTML контент и конвертировать в Markdown"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Обрабатываем все ссылки
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            new_href = self.convert_link(href, current_file_path)
            link['href'] = new_href
        
        # Обрабатываем все изображения
        for img in soup.find_all('img', src=True):
            src = img.get('src', '')
            new_src = self.convert_image(src, current_file_path)
            img['src'] = new_src
        
        # Конвертируем в Markdown
        html_str = str(soup)
        markdown = self.h.handle(html_str)
        
        # Дополнительная обработка для улучшения форматирования
        # Убираем лишние пустые строки
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        # Исправляем форматирование заголовков с якорями
        markdown = re.sub(r'#+\s*\[([^\]]+)\]\(#[^\)]+\)', r'# \1', markdown)
        
        return markdown.strip()
    
    def convert_file(self, html_file):
        """Конвертировать один HTML файл в Markdown"""
        try:
            # Читаем HTML
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Обрабатываем и конвертируем
            markdown_content = self.process_html_content(html_content, html_file)
            
            # Вычисляем путь для Markdown файла
            relative_path = html_file.relative_to(self.source_dir)
            md_file = self.output_dir / str(relative_path).replace('.html', '.md')
            
            # Создаем директорию если нужно
            md_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Сохраняем Markdown
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"✓ Конвертирован: {relative_path}")
            return True
            
        except Exception as e:
            print(f"✗ Ошибка при конвертации {html_file}: {e}")
            return False
    
    def convert_all(self):
        """Конвертировать все HTML файлы"""
        print(f"Начало конвертации HTML → Markdown")
        print(f"Исходная директория: {self.source_dir}")
        print(f"Выходная директория: {self.output_dir}")
        print(f"{'='*60}\n")
        
        # Находим все HTML файлы
        html_files = self.find_html_files()
        
        if not html_files:
            print("HTML файлы не найдены!")
            return
        
        # Конвертируем каждый файл
        success_count = 0
        for html_file in html_files:
            if self.convert_file(html_file):
                success_count += 1
        
        print(f"\n{'='*60}")
        print(f"Конвертация завершена!")
        print(f"Успешно: {success_count}/{len(html_files)}")
        
        # Копируем папку MAX UI без конвертации
        print(f"\nКопирование папки MAX UI (без конвертации)...")
        self.copy_max_ui_folder()
        
        # Упрощаем структуру директорий
        print(f"\nУпрощение структуры директорий...")
        self.simplify_directory_structure()
        
        print(f"\nРезультаты сохранены в: {os.path.abspath(self.output_dir)}")
        print(f"{'='*60}")
    
    def copy_max_ui_folder(self):
        """Скопировать папку MAX UI из исходной директории в выходную без конвертации"""
        max_ui_source = self.source_dir / 'MAX UI'
        max_ui_dest = self.output_dir / 'MAX UI'
        
        if max_ui_source.exists() and max_ui_source.is_dir():
            try:
                # Удаляем старую папку если есть
                if max_ui_dest.exists():
                    shutil.rmtree(max_ui_dest)
                
                # Копируем всю папку
                shutil.copytree(max_ui_source, max_ui_dest)
                print(f"✓ Скопирована папка MAX UI")
            except Exception as e:
                print(f"✗ Ошибка при копировании MAX UI: {e}")
    
    def simplify_directory_structure(self):
        """Удалить лишние вложенные папки (когда в папке только одна подпапка)"""
        if not self.output_dir.exists():
            return
        
        # Пропускаем папку MAX UI при упрощении
        
        simplified_count = 0
        
        # Повторяем процесс, пока есть что упрощать (максимум 20 итераций для безопасности)
        for iteration in range(20):
            simplified_in_iteration = False
            
            # Обходим директории снизу вверх (от самых глубоких к корню)
            for root, dirs, files in os.walk(self.output_dir, topdown=False):
                dir_path = Path(root)
                
                # Пропускаем только корневую директорию
                if dir_path == self.output_dir:
                    continue
                
                try:
                    # Получаем список элементов в директории
                    items = list(dir_path.iterdir())
                    
                    # Проверяем: если в директории только одна поддиректория и нет файлов
                    subdirs = [item for item in items if item.is_dir()]
                    files_list = [item for item in items if item.is_file()]
                    
                    if len(subdirs) == 1 and len(files_list) == 0:
                        # Есть только одна поддиректория, схлопываем её
                        subdir = subdirs[0]
                        parent_dir = dir_path.parent
                        
                        # Перемещаем все содержимое поддиректории в родительскую директорию
                        items_to_move = list(subdir.iterdir())
                        for item in items_to_move:
                            new_path = parent_dir / item.name
                            
                            # Если элемент с таким именем уже существует, пропускаем
                            if new_path.exists():
                                continue
                            
                            # Перемещаем элемент
                            try:
                                item.rename(new_path)
                            except Exception as e:
                                # Если не удалось переместить, пропускаем
                                continue
                        
                        # Удаляем пустую поддиректорию
                        try:
                            if not any(subdir.iterdir()):
                                subdir.rmdir()
                        except:
                            pass
                        
                        # Если текущая директория теперь пустая, удаляем её тоже
                        try:
                            if not any(dir_path.iterdir()):
                                dir_path.rmdir()
                        except:
                            pass
                        
                        simplified_in_iteration = True
                        simplified_count += 1
                        
                except Exception:
                    # Игнорируем ошибки при обработке отдельных директорий
                    continue
            
            # Если в этой итерации ничего не упростили, выходим
            if not simplified_in_iteration:
                break
        
        if simplified_count > 0:
            print(f"Упрощено директорий: {simplified_count}")


if __name__ == "__main__":
    converter = HTMLToMarkdownConverter()
    converter.convert_all()

