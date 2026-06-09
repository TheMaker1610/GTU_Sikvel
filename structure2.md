GTU_Sikvel/ 

├── run.py                      Точка запуска: поднимает сервер, затем клиент 

├── requirements.txt 

├── pytest.ini 

├── .env.example 

│ 

├── server/                     Серверная часть 

│   ├── main.py                 Запуск оркестратора + uvicorn (asyncio.gather) 

│   ├── api/ 

│   │   ├── app.py              Фабрика FastAPI-приложения, lifespan 

│   │   └── routes.py           REST-маршруты и зависимости авторизации 

│   ├── orchestrator/ 

│   │   └── orchestrator.py     Фоновый цикл опроса и анализа 

│   ├── sensors/ 

│   │   ├── sensor_service.py   Источник показаний датчиков (симулятор) 

│   │   ├── rules_loader.py     Загрузка норм из CSV (Приложение 2) 

│   │   └── notebook_loader.py  Загрузка истории из .ipynb (Приложение 1) 

│   ├── analytics/ 

│   │   ├── anomaly_detector.py Проверка показаний на выход из диапазона 

│   │   └── classifier.py       Классификатор режима по показаниям 

│   ├── auth/ 

│   │   └── auth_service.py     JWT, bcrypt, пользователь по умолчанию 

│   ├── storage/ 

│   │   ├── database.py         Engine, сессии, init_db, get_db 

│   │   └── models.py           ORM-модели SensorRecord, User 

│   ├── logging_service/ 

│   │   └── logger.py           Логирование в консоль и файл 

│   └── config/ 

│       └── settings.py         Переменные окружения, словарь GTU_MODES 

│ 

├── client/                     Клиентская часть (PyQt5) 

│   ├── main.py                 QApplication, цикл «вход → окно → выход» 

│   ├── api_client.py           HTTP-клиент к серверу 

│   └── ui/ 

│       ├── login_dialog.py     Диалог аутентификации 

│       └── main_window.py      Главное окно: мониторинг, история, логи 

│ 

└── tests/                      pytest: auth, api, sensor, classifier, anomaly 
