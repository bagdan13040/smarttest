"""Проверяем содержимое settings.json"""
import json
import os

settings_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'my', 'settings.json')

if os.path.exists(settings_path):
    print(f"Читаем: {settings_path}\n")
    with open(settings_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Содержимое файла:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    print("\n" + "="*50)
    print("Проверка секции 'api':")
    if 'api' in data:
        api_section = data['api']
        print(f"  Ключи в секции: {list(api_section.keys())}")
        for key, value in api_section.items():
            if 'key' in key.lower() and isinstance(value, str):
                print(f"  {key}: {value[:15]}...{value[-5:]if len(value) > 20 else value}")
            else:
                print(f"  {key}: {value}")
    else:
        print("  ❌ Секция 'api' отсутствует!")
else:
    print(f"❌ Файл не найден: {settings_path}")
