"""Тест проверки API ключа в настройках"""
import os
from kivy.storage.jsonstore import JsonStore

# Путь к настройкам в user_data_dir приложения
# В Windows это обычно: %USERPROFILE%\.kivy\smarttest
user_data = os.path.expanduser('~/.kivy/smarttest')
settings_path = os.path.join(user_data, 'settings.json')

print(f"Проверяем файл настроек: {settings_path}")
print(f"Файл существует: {os.path.exists(settings_path)}")

if os.path.exists(settings_path):
    store = JsonStore(settings_path)
    print(f"\nЕсть секция 'api': {store.exists('api')}")
    
    if store.exists('api'):
        data = store.get('api')
        print(f"Содержимое секции 'api':")
        for key, value in data.items():
            # Скрываем часть ключа для безопасности
            if 'key' in key.lower() and isinstance(value, str) and len(value) > 10:
                print(f"  {key}: {value[:10]}...{value[-4:]}")
            else:
                print(f"  {key}: {value}")
    
    # Проверяем все секции
    print(f"\nВсе секции в файле:")
    for key in store.keys():
        print(f"  - {key}")
else:
    print("\n❌ Файл настроек не найден!")
    print("Запустите приложение и сохраните API ключ в настройках.")
