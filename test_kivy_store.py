from kivy.storage.jsonstore import JsonStore
import os

try:
    if os.path.exists('test_settings.json'):
        os.remove('test_settings.json')
        
    store = JsonStore('test_settings.json')
    # This matches the code in main.py
    store.put('api', api_key='12345')
    print("Success put")
    print(f"Retrieved: {store.get('api')['api_key']}")
except Exception as e:
    print(f"Error: {e}")
