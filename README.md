# praktikum_new_diplom
docker compose -f docker-compose.yml up -d --build
docker compose -f docker-compose.yml exec backend python manage.py makemigrations 
docker compose -f docker-compose.yml exec backend python manage.py migrate
docker compose -f docker-compose.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.yml exec backend python manage.py load_tags
docker compose -f docker-compose.yml exec backend python manage.py load_ingrs