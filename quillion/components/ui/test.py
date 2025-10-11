import os
import ast
from pathlib import Path
from typing import List, Set

def is_function_exportable(name: str, file_path: Path) -> bool:
    """Проверяет, нужно ли экспортировать функцию"""
    # Не экспортируем приватные функции и служебные
    if name.startswith('_'):
        return False
    
    # Не экспортируем функции из самого скрипта генерации
    if file_path.name == 'generate_init.py':
        return False
    
    return True

def extract_exportable_functions(file_path: Path) -> List[str]:
    """Извлекает имена функций для экспорта из файла, игнорируя методы классов"""
    functions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Собираем все имена классов в файле
        class_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_names.add(node.name)
        
        # Теперь ищем функции, которые НЕ являются методами классов
        for node in ast.walk(tree):
            # Ищем функции на верхнем уровне
            if isinstance(node, ast.FunctionDef):
                # Проверяем, что функция не внутри класса
                current = node
                is_method = False
                while hasattr(current, 'parent') and current.parent:
                    if isinstance(current.parent, ast.ClassDef):
                        is_method = True
                        break
                    current = current.parent
                
                if not is_method and is_function_exportable(node.name, file_path):
                    functions.append(node.name)
            
            # Ищем функции, объявленные через присваивание на верхнем уровне
            elif isinstance(node, ast.Assign):
                # Проверяем, что присваивание на верхнем уровне (не в классе)
                current = node
                is_in_class = False
                while hasattr(current, 'parent') and current.parent:
                    if isinstance(current.parent, ast.ClassDef):
                        is_in_class = True
                        break
                    current = current.parent
                
                if not is_in_class:
                    for target in node.targets:
                        if isinstance(target, ast.Name) and is_function_exportable(target.name, file_path):
                            # Проверяем, что присваивается функция (lambda или вызов)
                            if isinstance(node.value, (ast.Lambda, ast.Call)):
                                functions.append(target.name)
    
    except Exception as e:
        print(f"⚠️ Ошибка при чтении {file_path}: {e}")
    
    return functions

def generate_init_with_functions(package_root: str = ".") -> None:
    """Генерирует __init__.py с импортами конкретных функций и __all__"""
    
    imports = []
    all_functions: Set[str] = set()
    module_functions = {}
    
    # Рекурсивно находим все Python файлы
    for root, dirs, files in os.walk(package_root):
        # Пропускаем служебные директории
        if '__pycache__' in root or any(x in root for x in ['.git', '.vscode', '__pycache__']):
            continue
            
        for file in files:
            if file.endswith('.py') and file not in ['__init__.py', 'generate_init.py']:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(package_root)
                
                # Преобразуем путь в формат импорта
                import_parts = list(relative_path.parts)
                import_parts[-1] = import_parts[-1][:-3]  # Убираем .py
                module_path = '.'.join(import_parts)
                
                # Извлекаем функции из файла
                functions = extract_exportable_functions(file_path)
                
                if functions:
                    # Сортируем функции для порядка
                    functions.sort()
                    
                    # Добавляем импорт
                    imports.append(f"from .{module_path} import {', '.join(functions)}")
                    
                    # Добавляем функции в __all__
                    all_functions.update(functions)
                    
                    # Сохраняем для отчета
                    module_functions[module_path] = functions
    
    # Сортируем импорты для красоты
    imports.sort()
    sorted_functions = sorted(all_functions)
    
    # Создаем содержимое файла
    content = '''"""
Автоматически сгенерированный файл __init__
"""

'''

    # Добавляем импорты
    content += '\n'.join(imports)
    content += '\n\n'
    
    # Добавляем __all__
    content += '__all__ = [\n'
    for func in sorted_functions:
        content += f'    "{func}",\n'
    content += ']\n'
    
    # Записываем файл
    init_path = Path(package_root) / "__init__.py"
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Выводим отчет
    print(f"✅ Сгенерирован {init_path}")
    print(f"📦 Модулей: {len(imports)}")
    print(f"🚀 Функций: {len(sorted_functions)}")
    print("\n📋 Импортированные функции:")
    for module, funcs in sorted(module_functions.items()):
        print(f"   {module}: {', '.join(funcs)}")

# Запуск
if __name__ == "__main__":
    generate_init_with_functions(".")