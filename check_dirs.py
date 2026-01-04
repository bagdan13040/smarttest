"""Проверяем директорию MyApp"""
import os
from pathlib import Path

# Проверяем несколько возможных путей
possible_dirs = [
    os.path.expanduser('~/.kivy/my'),
    os.path.expanduser('~/.kivy/myapp'),
    os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'my'),
    os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'myapp'),
    os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'MyApp'),
]

for d in possible_dirs:
    if os.path.exists(d):
        print(f"✅ Найдена директория: {d}")
        files = os.listdir(d)
        if files:
            print(f"   Файлы:")
            for f in files:
                full_path = os.path.join(d, f)
                if os.path.isfile(full_path):
                    size = os.path.getsize(full_path)
                    print(f"     - {f} ({size} байт)")
        else:
            print("   (пустая)")
    else:
        print(f"❌ Не найдена: {d}")
