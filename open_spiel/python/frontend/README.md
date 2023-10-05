# django setup

mkdir django-todo-react
cd django-todo-react
pip3 install pipenv

pipenv shell
pipenv install django
django-admin startproject backend
cd backend
python3 manage.py startapp todo
python3 manage.py migrate

python3 manage.py runserver 0.0.0.0:8000

# register todo application

Add 'todo' to INSTALLED_APPS in the settings

Edit todo/models.py adding Todo class

python3 manage.py makemigrations todo

python3 manage.py migrate todo

edit todo/admin.py adding TodoAdmin class

# create a super user

python3 manage.py createsuperuser

python3 manage.py runserver 0.0.0.0:8000

You should be able to add todos and edit them

# setting up the APIs

pipenv install djangorestframework django-cors-headers

Add to INSTALLED_APPS and MIDDLEWARE to backend/settings.py

add CORS_ORIGIN_WHITELIST to backend/settings.py

Create todo/serializers.py

Create todo/views.py

Modify backend/urls.py to register the url

python3 manage.py runserver 0.0.0.0:8000

Test the CRUD operations
