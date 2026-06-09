gtukm4/
│
├── server/                          # Серверная часть
│   ├── __init__.py                  # Пакетный файл
│   ├── api.py                       # REST API сервер (Flask)
│   ├── auth.py                      # Аутентификация (JWT)
│   ├── analyzer.py                  # Анализ аномалий
│   ├── config.py                    # Конфигурация и нормы
│   ├── data_acquisition.py          # Опрос датчиков
│   ├── database.py                  # Работа с БД (SQLAlchemy)
│   ├── logger.py                    # Логирование (Singleton)
│   ├── models.py                    # Data models (dataclass)
│   └── storage.py                   # In-memory хранилище
│
├── client/                          # Клиентская часть
│   ├── __init__.py                  # Пакетный файл
│   ├── api_client.py                # HTTP клиент для API
│   ├── main_window.py               # Главное окно PyQt5
│   └── widgets.py                   # Пользовательские виджеты
│
├── tests/                           # Тесты
│   ├── __init__.py                  # Пакетный файл
│   ├── conftest.py                  # Pytest конфигурация
│   ├── test_analyzer.py             # Тесты анализатора
│   └── test_storage.py              # Тесты хранилища
│
├── requirements.txt                 # Зависимости Python
├── run.py                           # Точка входа
└── gtu_data.db                      # SQLite БД (создается при запуске)
