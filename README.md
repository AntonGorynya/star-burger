# Сайт доставки еды Star Burger

Это сайт сети ресторанов Star Burger. Здесь можно заказать превосходные бургеры с доставкой на дом. Демо версия сайта доступна по ссылке https://antongoryniadev.ru/ 

![скриншот сайта](https://dvmn.org/filer/canonical/1594651635/686/)


Сеть Star Burger объединяет несколько ресторанов, действующих под единой франшизой. У всех ресторанов одинаковое меню и одинаковые цены. Просто выберите блюдо из меню на сайте и укажите место доставки. Мы сами найдём ближайший к вам ресторан, всё приготовим и привезём.

На сайте есть три независимых интерфейса. Первый — это публичная часть, где можно выбрать блюда из меню, и быстро оформить заказ без регистрации и SMS.

Второй интерфейс предназначен для менеджера. Здесь происходит обработка заказов. Менеджер видит поступившие новые заказы и первым делом созванивается с клиентом, чтобы подтвердить заказ. После оператор выбирает ближайший ресторан и передаёт туда заказ на исполнение. Там всё приготовят и сами доставят еду клиенту.

Третий интерфейс — это админка. Преимущественно им пользуются программисты при разработке сайта. Также сюда заходит менеджер, чтобы обновить меню ресторанов Star Burger.

# Подготовка

Сайт предполагает свою работу в связки с Nginx и Gunicorn. Ниже рассмотрим обязательные шаги

### Установите Python
[Установите Python](https://www.python.org/), если этого ещё не сделали.

Проверьте, что `python` установлен и корректно настроен. Запустите его в командной строке:
```sh
python --version
```
**Важно!** Версия Python должна быть не ниже 3.6.

Возможно, вместо команды `python` здесь и в остальных инструкциях этого README придётся использовать `python3`. Зависит это от операционной системы и от того, установлен ли у вас Python старой второй версии.

### Скачайте код:
```sh
git clone https://github.com/devmanorg/star-burger.git
```

### Установите Gunicorn

```commandline
pip install gunicorn
```

Cоздайте файл `/etc/systemd/system/star-burger.service` вида
```sh
[Unit]
Description=gunicorn daemon
After=network.target
After=postgresql.service
Requires=postgresql.service



[Service]
WorkingDirectory=/opt/star-burger/star-burger
ExecStart=gunicorn -w 3 -b 127.0.0.1:8080 star_burger.wsgi:application
Restart=always


[Install]
WantedBy=multi-user.target
```
Для запуска сайта на локальном IP адресе.
Укажите вашу WorkingDirectory.

### Установите NGINX

```commandline
apt install nginx
```
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
        alias /opt/star-burger/star-burger/media/;
    }

    location /static/ {
        alias /opt/star-burger/star-burger/staticfiles/;
    }

    location / {
        include '/etc/nginx/proxy_params';
        proxy_pass http://127.0.0.1:8080/;
    }
}
```
При необходимости настройте SSL. Укажите пути для media и static папок.

### Установите Postgres
Рекомендуется использовать Postgres при деплое проекта. Вы можете скачать его с официального [сайта](https://www.postgresql.org/download/)


### Заполните .env
Файл `.env` в каталоге `star_burger/` вида:
```commandline
SECRET_KEY='12345asdv'
YANDEX_KEY='0000-1111-2222-3333-4444'
DEBUG='False'
DB_URL='postgres://USER:PASSWORD@HOST:PORT/NAME'
ROLLBAR_KEY='12345abc'
```

- `SECRET_KEY` секретный ключ вашего проекта на django
Вы можете создать ключ  выполнив команду
```commandline
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
-  `YANDEX_KEY`. Переменная хранит ключ от [API яндекса](https://developer.tech.yandex.ru/) для работы с геокодером.
-  `ROLLBAR_KEY`. Переменная хранит ключ для отправки исключений на внешний сервер https://rollbar.com. Для получения ключ зарегистрируйтесь на [Rollback](https://rollbar.com) и создайте новый проект. Установите значение перменной равной токену `post_server_item` в настройках проекта.
-  `ENVIRONMENT` название окружения для сервиса ROLLBAR. Опционально.
-  `DB_URL`. Указав URL для подключения к бд. Примеры можно посмотреть тут https://github.com/jazzband/dj-database-url#id13
- `DEBUG` Включение и отключение режима отладки. Поставьте `False`.
- `ALLOWED_HOSTS` — [см. документацию Django](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts)

# Запуск сайта

## Автоматическое развертывание

Перейдите в каталог проекта и запустите скрипт деплоя:
```sh
cd star-burger
./deploy_star_burger
```

## Ручное развертывание
### Cоздайте виртуальное окружение
В каталоге проекта создайте виртуальное окружение:
```sh
python -m venv venv
```
Активируйте его. На разных операционных системах это делается разными командами:

- Windows: `.\venv\Scripts\activate`
- MacOS/Linux: `source venv/bin/activate`

Установите зависимости в виртуальное окружение:
```sh
pip install -r requirements.txt
```


### Создайте БД
Создайте файл базы данных и отмигрируйте её следующей командой:

```sh
python manage.py makemigrations
python manage.py migrate
```

## Как запустить dev-версию сайта

Для запуска сайта нужно запустить **одновременно** бэкенд и фронтенд, в двух терминалах.

### Как запустить бэкенд


Запустите сервер:

```sh
python manage.py runserver
```

Откройте сайт в браузере по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Если вы увидели пустую белую страницу, то не пугайтесь, выдохните. Просто фронтенд пока ещё не собран. Переходите к следующему разделу README.

### Собрать фронтенд

**Откройте новый терминал**. Для работы сайта в dev-режиме необходима одновременная работа сразу двух программ `runserver` и `parcel`. Каждая требует себе отдельного терминала. Чтобы не выключать `runserver` откройте для фронтенда новый терминал и все нижеследующие инструкции выполняйте там.

[Установите Node.js](https://nodejs.org/en/), если у вас его ещё нет.

Проверьте, что Node.js и его пакетный менеджер корректно установлены. Если всё исправно, то терминал выведет их версии:

```sh
nodejs --version
# v16.16.0
# Если ошибка, попробуйте node:
node --version
# v16.16.0

npm --version
# 8.11.0
```

Версия `nodejs` должна быть не младше `10.0` и не старше `16.16`. Лучше ставьте `16.16.0`, её мы тестировали. Версия `npm` не важна. Как обновить Node.js читайте в статье: [How to Update Node.js](https://phoenixnap.com/kb/update-node-js-version).

Перейдите в каталог проекта и установите пакеты Node.js:

```sh
cd star-burger
npm ci --dev
```

Команда `npm ci` создаст каталог `node_modules` и установит туда пакеты Node.js. Получится аналог виртуального окружения как для Python, но для Node.js.

Помимо прочего будет установлен [Parcel](https://parceljs.org/) — это упаковщик веб-приложений, похожий на [Webpack](https://webpack.js.org/). В отличии от Webpack он прост в использовании и совсем не требует настроек.

Теперь запустите сборку фронтенда и не выключайте. Parcel будет работать в фоне и следить за изменениями в JS-коде:

```sh
./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
```

Если вы на Windows, то вам нужна та же команда, только с другими слешами в путях:

```sh
.\node_modules\.bin\parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
```

Дождитесь завершения первичной сборки. Это вполне может занять 10 и более секунд. О готовности вы узнаете по сообщению в консоли:

```
✨  Built in 10.89s
```

Parcel будет следить за файлами в каталоге `bundles-src`. Сначала он прочитает содержимое `index.js` и узнает какие другие файлы он импортирует. Затем Parcel перейдёт в каждый из этих подключенных файлов и узнает что импортируют они. И так далее, пока не закончатся файлы. В итоге Parcel получит полный список зависимостей. Дальше он соберёт все эти сотни мелких файлов в большие бандлы `bundles/index.js` и `bundles/index.css`. Они полностью самодостаточны, и потому пригодны для запуска в браузере. Именно эти бандлы сервер отправит клиенту.

Теперь если зайти на страницу  [http://127.0.0.1:8000/](http://127.0.0.1:8000/), то вместо пустой страницы вы увидите:

![](https://dvmn.org/filer/canonical/1594651900/687/)

Каталог `bundles` в репозитории особенный — туда Parcel складывает результаты своей работы. Эта директория предназначена исключительно для результатов сборки фронтенда и потому исключёна из репозитория с помощью `.gitignore`.

**Сбросьте кэш браузера <kbd>Ctrl-F5</kbd>.** Браузер при любой возможности старается кэшировать файлы статики: CSS, картинки и js-код. Порой это приводит к странному поведению сайта, когда код уже давно изменился, но браузер этого не замечает и продолжает использовать старую закэшированную версию. В норме Parcel решает эту проблему самостоятельно. Он следит за пересборкой фронтенда и предупреждает JS-код в браузере о необходимости подтянуть свежий код. Но если вдруг что-то у вас идёт не так, то начните ремонт со сброса браузерного кэша, жмите <kbd>Ctrl-F5</kbd>.


## Как запустить prod-версию сайта

Собрать фронтенд:

```sh
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
```

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org). За основу был взят код проекта [FoodCart](https://github.com/Saibharath79/FoodCart).

Где используется репозиторий:

- Второй и третий урок [учебного курса Django](https://dvmn.org/modules/django/)
