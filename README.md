# group-portal_26_08

Командний навчальний проєкт «Портал групи» на Django.


## Інструкція Як працювати з Git (GitFlow)

1. Перейти на `main` та оновити його:

   ```bash
   git checkout main
   git pull origin main
   ```

2. Подивитися свій таск у Trello.
   Назва гілки = ID таска, наприклад: `FOR-2`, `GL-3`, `AUTH-1` тощо.

3. Створити гілку від `main`:

   ```bash
   git checkout -b FOR-2
   ```

4. Зробити зміни в коді, запустити проєкт і перевірити, що все працює.

5. Додати файли та зробити коміт:

   ```bash
   git add .
   git commit -m "FOR-2 — коротко-що-робиш"
   ```

6. Відправити гілку на GitHub:

   ```bash
   git push origin FOR-2
   ```


## Правила: де що лежить

**Шаблони свого модуля — лише у своїй апці, у вкладеній папці з назвою апки.**

```
forum/
└── templates/
    └── forum/                  ← обов'язково вкладена папка з назвою апки!
        ├── thread_list.html
        └── thread_detail.html
```

Повний шлях: `forum/templates/forum/thread_list.html`, у в'юшці —
`template_name = "forum/thread_list.html"`.

| Що                             | Куди                                              |
|--------------------------------|---------------------------------------------------|
| Сторінки мого модуля           | `<апка>/templates/<апка>/*.html`                  |
| Мої стилі / скрипти            | `static/css/<апка>.css`, `static/js/<апка>.js`    |
| Мій пункт меню                 | розкоментувати в `templates/includes/navbar.html` |
| Завантажені користувачем файли | `media/` (у git не потрапляє)                     |

**Спільні файли — не змінювати без погодження з ментором:**

| Файл                             | Хто змінює                                   |
|----------------------------------|----------------------------------------------|
| `templates/base.html`            | лише за погодженням з ментором               |
| `templates/includes/footer.html` | лише за погодженням з ментором               |
| `static/css/style.css`           | лише за погодженням з ментором               |
| `templates/includes/navbar.html` | кожен лише розкоментовує **свій** пункт меню |
| `templates/home.html`            | видаляє автор модуля `core`                  |

**Свої стилі та скрипти підключати у своєму шаблоні, а не в `base.html`:**

```html
{% extends "base.html" %}
{% load static %}

{% block extra_css %}
  <link rel="stylesheet" href="{% static 'css/forum.css' %}">
{% endblock %}

{% block extra_js %}
  <script src="{% static 'js/forum.js' %}"></script>
{% endblock %}
```

## Структура проєкту

```
group-portal_26_08/
├── config/                # Налаштування Django-проєкту
│   ├── __init__.py
│   ├── asgi.py            # ASGI-конфігурація
│   ├── settings.py        # Основні налаштування проєкту
│   ├── urls.py            # Головний маршрутизатор URL
│   └── wsgi.py            # WSGI-конфігурація
├── forum/                 # Приклад модуля (у кожного учня свій)
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       └── forum/         # шаблони модуля — лише тут!
│           └── thread_list.html
├── templates/             # Спільні HTML-шаблони
│   ├── base.html          # Базовий шаблон (від нього наслідуються всі сторінки)
│   └── includes/          # Частини сторінки: navbar.html, footer.html
├── static/                # Спільні CSS / JS / картинки
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
├── media/                 # Файли, які завантажують користувачі (у git не потрапляють)
├── .venv/                 # Віртуальне середовище (у git не потрапляє)
├── .gitignore
├── manage.py              # Утиліта управління Django
├── requirements.txt       # Залежності проєкту
└── README.md
```

## Команди для учнів

### 1. Запуск проєкту (робиться один раз при клонуванні)

```bash
git clone <посилання-на-репозиторій>
cd group-portal_26_08

# створити віртуальне середовище
python3 -m venv .venv

# активувати його
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# встановити залежності
pip install -r requirements.txt

# створити базу даних
python manage.py migrate

# створити адміністратора (логін/пошта/пароль)
python manage.py createsuperuser

# запустити сервер
python manage.py runserver
```

Сайт: http://127.0.0.1:8000/ — адмінка: http://127.0.0.1:8000/admin/

### 2. Щоденна робота

```bash
source .venv/bin/activate        # завжди активуй venv перед роботою
python manage.py runserver
```

Зупинити сервер: `Ctrl + C`.

### 3. Створення свого модуля

```bash
python manage.py startapp forum          # замість forum — назва твого модуля
```

Далі:

1. У `config/settings.py` розкоментувати свій додаток у `INSTALLED_APPS`.
2. Створити файл `forum/urls.py` (приклад є в коментарях у `config/urls.py`).
3. У `config/urls.py` розкоментувати рядок свого модуля.
4. У `templates/includes/navbar.html` розкоментувати свій пункт меню.
5. Шаблони класти в `forum/templates/forum/`, наслідувати від `base.html`:

   ```html
   {% extends "base.html" %}

   {% block title %}Форум{% endblock %}

   {% block content %}
     <h1 class="page-title">Форум</h1>
   {% endblock %}
   ```

### 4. Робота з базою даних

```bash
python manage.py makemigrations          # створити міграції після зміни models.py
python manage.py migrate                 # застосувати міграції
python manage.py showmigrations          # подивитися стан міграцій
```

### 5. Перевірка перед комітом

```bash
python manage.py check                   # перевірити проєкт на помилки
python manage.py test                    # запустити тести
```

### 6. Якщо додав нову бібліотеку

```bash
pip install <бібліотека>
pip freeze > requirements.txt
```

## Модулі проєкту

| Модуль          | Додаток         | Префікс таска |
|-----------------|-----------------|---------------|
| Головна сторінка| `core`          | HOME          |
| Автентифікація  | `accounts`      | AUTH          |
| Форум           | `forum`         | FOR           |
| Щоденник        | `diary`         | DIA           |
| Події, календар | `events`        | EVE           |
| Опитування      | `polls`         | POL           |
| Голосування     | `voting`        | VOT           |
| Оголошення      | `announcements` | ANN           |
| Матеріали       | `materials`     | MAT           |
| Портфоліо       | `portfolio`     | POR           |
| Галерея         | `gallery`       | GAL           |
