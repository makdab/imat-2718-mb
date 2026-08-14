# College Course Portal — IMAT2718 Integrated Project (prototype)

A Django + SQLite prototype for a college course-management system: browse courses
and modules, sign up / log in, and register (enrol) on courses.

## Requirements

- Python 3.11+
- The dependencies in `requirements.txt` (Django 5.1)

## Setup

From the project root (the folder containing `manage.py`):

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the database schema
python manage.py migrate

# 4. Load demo courses, modules and staff
python manage.py seed_demo

# 5. (Optional) create an admin account for the /admin/ site
python manage.py createsuperuser

# 6. Run the development server
python manage.py runserver
```

Then open http://127.0.0.1:8000/ (admin site at http://127.0.0.1:8000/admin/).

Seeded teaching-staff accounts log in with the password `demopass123`
(usernames: `a.shargabi`, `j.smith`, `p.patel`, `l.chen`).

## Running the tests

```bash
python manage.py test
```

## Project structure

```
cem/         Django project config (settings, root urls)
accounts/    Custom User (is_teacher flag) + sign up / login / logout
courses/     Course, Module, Enrollment models, browse + enrol views,
             and the seed_demo management command
templates/   Shared base template
static/      CSS
```

## Notes

- `venv/` and `db.sqlite3` are intentionally **not** included — recreate them with the
  steps above. `requirements.txt` + `seed_demo` reproduce the exact environment and data.
- `SECRET_KEY` in `cem/settings.py` is a development key; replace it before any real deployment.
```
