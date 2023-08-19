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

### Установка проекта на локальный компьютер из репозитория 
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
```
 - находясь в директории /foodgram-project-react/ последовательно выполнить следующие дейсвтия:
 ```
docker compose -f docker-compose.yml up -d --build
docker compose -f docker-compose.yml exec backend python manage.py makemigrations 
docker compose -f docker-compose.yml exec backend python manage.py migrate
docker compose -f docker-compose.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.yml exec backend python manage.py load_tags
docker compose -f docker-compose.yml exec backend python manage.py load_ingrs
```
### Автор
Дмитрий Уткин