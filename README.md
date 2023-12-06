# Сайт доставки еды Star Burger

Это сайт сети ресторанов Star Burger. Здесь можно заказать превосходные бургеры с доставкой на дом. Демо версия сайта доступна по ссылке https://antongoryniadev.ru/

![скриншот сайта](https://dvmn.org/filer/canonical/1594651635/686/)


Сеть Star Burger объединяет несколько ресторанов, действующих под единой франшизой. У всех ресторанов одинаковое меню и одинаковые цены. Просто выберите блюдо из меню на сайте и укажите место доставки. Мы сами найдём ближайший к вам ресторан, всё приготовим и привезём.

На сайте есть три независимых интерфейса. Первый — это публичная часть, где можно выбрать блюда из меню, и быстро оформить заказ без регистрации и SMS.

Второй интерфейс предназначен для менеджера. Здесь происходит обработка заказов. Менеджер видит поступившие новые заказы и первым делом созванивается с клиентом, чтобы подтвердить заказ. После оператор выбирает ближайший ресторан и передаёт туда заказ на исполнение. Там всё приготовят и сами доставят еду клиенту.

Третий интерфейс — это админка. Преимущественно им пользуются программисты при разработке сайта. Также сюда заходит менеджер, чтобы обновить меню ресторанов Star Burger.

Ниже будет рассмотрено 2 варианта установки. В локальном и дев окружении.
# Установка в Local окружении

## Скачайте код
Скачайте код:
```sh
git clone https://github.com/devmanorg/star-burger.git
```

## Установка докера
Установите [Docker](https://docs.docker.com/engine/install/ubuntu/)

## Заполните .env файлы
Файл `.env` в каталоге `backend/` вида:
```commandline
YANDEX_KEY='0000-1111-2222-3333-4444'
```
Переменная хранит ключ от [API яндекса](https://developer.tech.yandex.ru/) для работы с геокодером.

## Запустите контейнер
```commandline
docker-compose up
```
После успешной сборки выполните миграцию и создайте супер пользователя.
```commandline
docker exec -it star-burger_gunicorn_1 python3 ./manage.py migrate
docker exec -it star-burger_gunicorn_1 python3 ./manage.py createsuperuser
```

# Установка в Dev окружении
Сайт предполагает свою работу в связки с Nginx и Gunicorn. Ниже рассмотрим обязательные шаги
## Установите NGINX
При необходиости установите и настройте NGINX
Для установки веб сервера NGINX  используйте команду
```commandline
apt install nginx
```
Приме конфигурационного файла:
Создайте файл `/etc/nginx/sites-enabled/star-burger` вида
```commandline
server {
    listen 80;
    listen 443 ssl;
    server_name 80.249.147.35 antongoryniadev.ru;

    if ($scheme = 'http') {
        return 301 https://$host$request_uri;
    }

    ssl_certificate /etc/letsencrypt/live/antongoryniadev.ru/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/antongoryniadev.ru/privkey.pem; # managed by Certbot

    location /media/ {
        alias /opt/star-burger/media/;
    }

    location /static/ {
        alias /opt/star-burger/staticfiles/;
    }

    location / {
        include '/etc/nginx/proxy_params';
        proxy_pass http://127.0.0.1:8080/;
    }
}
```
При необходимости настройте SSL. Укажите пути для media и static папок.

## Установите Postgres
Рекомендуется использовать Postgres. Вы можете скачать его с официального [сайта](https://www.postgresql.org/download/)


## Заполните .env файлы
Файл `.env` в каталоге `backend/` вида:
```commandline
SECRET_KEY='12345asdv'
YANDEX_KEY='0000-1111-2222-3333-4444'
DEBUG='True'
DATABASE_URL='postgres://USER:PASSWORD@HOST:PORT/NAME'
ALLOWED_HOSTS=1.1.1.1,yourdomain.ru
```

Если используете сервис [rollbar](rollbar.com), то создайте `.env` файл в папке `stage` вида
```
ROLLBAR_KEY="aaaabbbbbbbbbcccccc"
```

- `SECRET_KEY` секретный ключ вашего проекта на django
Вы можете создать ключ выполнив команду
```commandline
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
- `YANDEX_KEY`. Переменная хранит ключ от [API яндекса](https://developer.tech.yandex.ru/) для работы с геокодером.
- `ROLLBAR_KEY`. (Опционально)Переменная хранит ключ для отправки исключений на внешний сервер https://rollbar.com. Для получения ключ зарегистрируйтесь на [Rollback](https://rollbar.com) и создайте новый проект. Установите значение перменной равной токену `post_server_item` в настройках проекта.
- `ENVIRONMENT` название окружения для сервиса ROLLBAR. Опционально.
- `DB_URL`. Указав URL для подключения к бд. Примеры можно посмотреть тут https://github.com/jazzband/dj-database-url#id13
- `DEBUG` Включение и отключение режима отладки. Поставьте `False`.
- `DATABASE_URL` URL для подключения к внешней БД Postgre
- `ALLOWED_HOSTS` — [см. документацию Django](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts)

Cоздайте файл `/etc/systemd/system/star-burger.service` вида
```sh
[Unit]
Description=gunicorn daemon
After=network.target
After=postgresql.service
Requires=postgresql.service

[Service]
WorkingDirectory=/opt/star-burger/star-burger
# Выберете один ExecStart параметр в зависимости от желаямого деплоя
ExecStart=docker run --network="host" -p 127.0.0.1:8080:8080  star-burger_gunicorn:v1.0  # Если используется Docker
ExecStart=gunicorn -w 3 -b 127.0.0.1:8080 star_burger.wsgi:application # Если запускается напрямую на хосте

Restart=always

[Install]
WantedBy=multi-user.target
```
Для запуска сайта на локальном IP адресе.
Укажите вашу WorkingDirectory.


# Установка докера
Установите [Docker](https://docs.docker.com/engine/install/ubuntu/)

Перейдите в каталог проекта и запустите скрипт деплоя:
```sh
cd star-burger/dev
./deploy_star_burger
```

