### Как запустить проект api_yamdb для проекта по сбору отзывов на произведения:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:misvictor/api_yamdb.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

Ссылка на документацию:
```
http://127.0.0.1:8000/redoc/
```

Авторы:
```
Варвара Иванова, Эдуард Казачков, Алексей  Смирнов.
```