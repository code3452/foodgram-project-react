# praktikum_diplom
# Проект Foodgram  
```
ссылка на проект https://foodgram-show.ddns.net/

log_admin = msi
password_admin = msi 
```

# Установка:

* Cоздайте .env файл и впишите:
    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>

    DB_HOST=<db>
    DB_PORT=<5432>

    SECRET_KEY=<секретный ключ проекта django>
    ```
* Для работы с workflow добавьте в secrets  переменные :
    ```
    DB_HOST=<db>
    DB_PORT=<5432>
    
    DOCKER_PASSWORD=<пароль от DockerHub>
    DOCKER_USERNAME=<имя пользователя>

    USER=<username для подключения к серверу>
    HOST=<IP сервера>
    SSH_PASSPHRASE=<пароль для сервера, если он установлен>
    SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

    TELEGRAM_TO=<ID чата, в который придет сообщение>
    TELEGRAM_TOKEN=<токен вашего бота>
    ```
    Workflow состоит из трёх шагов:
     - Проверка кода на соответствие PEP8
     - Сборка и публикация образа бекенда на DockerHub.
     - Автоматический деплой на удаленный сервер.
     - Отправка уведомления в телеграм-чат.  
  
## Запуск

Клонировать проект. Cоздать и активировать виртуальное окружение:
```bash
python -m venv venv
```
```bash
Linux: source venv/bin/activate
Windows: source venv/Scripts/activate
```
Установить зависимости из файла requirements.txt:
```bash
python -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

Собрать образы для фронтенда и бэкенда.  
Из папки "./infra/" выполнить команду:
```bash
sudo docker compose -f docker-compose.production.yml up -d

```

После успешного запуска контейнеров выполнить миграции в другом терминале
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

Создать суперюзера (Администратора):
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

Собрать статику:
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```

## Заполнение базы данных

С проектом поставляются данные об ингредиентах. Заполнить базу данных ингредиентами можно выполнив следующую команду:
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py ingredient
```

Также необходимо заполнить базу данных тегами .  
Для этого требуется войти в админку
проекта под логином и паролем администратора (пользователя, созданного командой createsuperuser).

---
прописать теги в админке