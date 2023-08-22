# Foodgram

### Описание
Foodgram - продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на любимых авторов.

### Технологии
- Python 3.x
- PostgreSQL
- Frontend: React
- Backend: Django
- Nginx
- Docker-compose

### Установка проекта на локальный компьютер из репозитория и деплой на сервер
 - Клонировать репозиторий `git clone <адрес вашего репозитория>`
 - перейти в директорию с клонированным репозиторием
 - установить виртуальное окружение `python3 -m venv venv`
 - установить зависимости `pip install -r requirements.txt`
 - в директории /foodgram-project-react/ создать файл .env
 - в файле .env прописать:
 ```
POSTGRES_DB             # название БД
DOCKER_PASSWORD         # пароль пользователя БД
POSTGRES_USER           # имя пользователя БД
DB_HOST                 # адрес, по которому Django будет соединяться с БД
DB_PORT                 # порт, по которому Django будет обращаться к БД (5432 порт по умолчанию)
DEBUG                   # включение/отключение режима отладки
SECRET_KEY              # секретный ключ приложения
```
 -  Запустите docker compose в режиме демона:
```
sudo docker compose -f docker-compose.production.yml up -d
```
 -  Последовательно выполните следующие команды:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py makemigrations 
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_tags
sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_ingrs
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser

```

### Пример работы проекта можно проверить по адресу [https://veter2901.hopto.org/](https://veter2901.hopto.org/)

### Автор
Дмитрий Уткин