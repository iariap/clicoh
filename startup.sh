
mkdir staticfiles
mkdir static
./manage.py collectstatic

./manage.py makemigrations && ./manage.py migrate

echo "
from django.contrib.auth.models import User; 
if not User.objects.filter(username='admin').exists(): 
    User.objects.create_superuser('admin', 'admin@example.com', 'pass')
else:
    print('El usuario admin ya estaba creado.')
" | ./manage.py shell


./manage.py runserver 0.0.0.0:8000