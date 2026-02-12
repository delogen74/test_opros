# survey_app monorepo

Production-ready mobile survey app with Django + DRF + PostgreSQL + React + TypeScript + Vite.

## Структура

- `backend/` — Django API, admin, migrations, seed command
- `frontend/` — React SPA для прохождения опроса
- `docker-compose.yml` — локальный запуск всего стека

## Запуск через Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/v1
- Django admin: http://localhost:8000/admin

> После первого запуска создайте суперпользователя:

```bash
docker compose exec backend python manage.py createsuperuser
```

## Локальный запуск без Docker

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_initial_data
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API

- `GET /api/v1/public/health/`
- `GET /api/v1/public/surveys/<token>/`
- `POST /api/v1/public/surveys/<token>/submit/`

Submit payload:

```json
{
  "answers": [
    {"question_id": 1, "answer": 5},
    {"question_id": 2, "answer": true},
    {"question_id": 3, "answer": "Комментарий"}
  ]
}
```

## Сидер

```bash
python manage.py seed_initial_data
```

Создает 2 точки и набор дефолтных вопросов по категориям `pickup`, `tire_service`, `common`.

## Качество кода

- pre-commit: black, isort, ruff

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```
