# GTU_Sikvel

Клиент-серверное приложение на Python. Название и назначение проекта уточняются.

## Оглавление
- [Статус](#статус)
- [Технологии](#технологии)
- [Структура проекта](#структура-проекта)
- [Установка и запуск](#установка-и-запуск)
- [Тестирование](#тестирование)
- [Участники](#участники)

## Статус
Проект в разработке. Доступна базовая клиент-серверная архитектура.

## Технологии
- **Язык**: Python 3.x (100% кода)
- **Фреймворки / библиотеки**: указаны в `requirements.txt` (файл добавлен, но содержимое недоступно из выгрузки)
- **Тестирование**: `pytest` (наличие `pytest.ini` и папки `tests/`)

## Структура проекта
GTU_Sikvel/
├── client/ # Клиентская часть
├── server/ # Серверная часть
├── tests/ # Модульные и интеграционные тесты (pytest)
├── run.py # Точка входа для запуска приложения
├── requirements.txt # Зависимости Python
├── pytest.ini # Конфигурация pytest
├── .env.example # Пример переменных окружения
├── .gitignore
└── README.md


## Установка и запуск

1. Клонировать репозиторий:
   ```bash
   git clone https://github.com/TheMaker1610/GTU_Sikvel.git
   cd GTU_Sikvel
   python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
cp .env.example .env
# Отредактировать .env при необходимости
python run.py

pytest
# или
python -m pytest
