# devops-status-dashboard

Simple web app for testing devops tools.

## ENV FILES
Expecting the following env files to build docker containers for prod:
1. devops-status-dashboard/services/web/docker/exclude/prod/.env.prod
```
FLASK_APP=project/__init__.py
FLASK_DEBUG=0
DATABASE_URL=postgresql://{user}:{pass}@db:5432/{db_name}
SQL_HOST=db
SQL_PORT=5432
DATABASE=postgres
```
2. devops-status-dashboard/services/web/docker/exclude/prod/.env.prod.db
```
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
```