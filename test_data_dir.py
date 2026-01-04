"""Определяем user_data_dir для SmartTest"""
from kivy.app import App

# Имитируем класс приложения
class TestApp(App):
    pass

# Создаём экземпляр
app = TestApp()
print(f"App name: {app.name}")
print(f"user_data_dir: {app.user_data_dir}")

# Проверяем есть ли файлы
import os
if os.path.exists(app.user_data_dir):
    print(f"\nФайлы в директории:")
    for file in os.listdir(app.user_data_dir):
        full_path = os.path.join(app.user_data_dir, file)
        size = os.path.getsize(full_path) if os.path.isfile(full_path) else "DIR"
        print(f"  - {file} ({size})")
else:
    print(f"\n❌ Директория не существует")
