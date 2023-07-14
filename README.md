# praktikum_new_diplom
# Проект Foodgram  

Доступ к админке:
```
Login: msi
Password: msi
```


## Подготовка и запуск проекта
### Склонировать репозиторий на локальную машину:
```
git clone https://github.com/code3452/foodgram-project-react.git
```

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

Загрузить в базу данных ингридиенты 
python manage.py load_ingredient
```
```bash
Создаем супер пользователя
python manage.py createsuperuser
```
```bash
Запускаем сервер 
python manage.py runserver
```
```bash