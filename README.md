# Convos

Backend приложения **Convos** для общения.

## Технологии

- Python 3.12.7
- Django 5.1
- Django REST Framework 3.15.2
- Channels 4.1.0
- Djoser 2.2.3

## Установка

Склонируйте проект:

`$ git clone https://github.com/Govorov1705/convos-backend.git`

Перейдите в папку _convos-backend/_:

`$ cd ./convos-backend/`

Создайте виртуальное окружение:

`$ python3 -m venv venv`

Активируйте виртуальное окружение:

`$ source ./venv/bin/activate`

Установите зависимости:

`$ pip3 install -r requirements.txt`

Создайте файл с переменными окружения _.env_, скопируйте в него примеры из файла _.env.example_ и внесите необходимые данные, следуя примерам:

```
SECRET_KEY=yourdjangosecretkey
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
EMAIL_HOST_USER=someappinbox@gmail.com # Email-адрес Gmail, для которого создан пароль приложения.
EMAIL_HOST_PASSWORD=some app password here # Пароль приложения для email-адреса, указанного выше.
DOMAIN=localhost:5173
```

Выполните миграции:

`$ python3 manage.py migrate`

Запустите локальный сервер:

`$ python3 manage.py runserver localhost:8000`

Готово! Backend доступен по адресу [http://localhost:8000](http://localhost:8000).

Следующий шаг - запуск frontend-части приложения. Для этого прочитайте _README.md_ в соответствующем [репозитории](https://github.com/Govorov1705/convos-frontend).
