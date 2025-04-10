# Timesheet Backend
Timesheet Backend Application API codebase [Python + FastAPI]

## Pre-requisites

### Database Connection
Set your database connection configuration on configs/database.py file.

### Install Virtual Environment
```
python -m venv env
```
OR
```
python3 -m venv env
```

### Activate Virtual Environment
```
./env/Scripts/activate
```

### Install Packages

```
pip install -r requirements.txt
```
OR

```
pip install fastapi pydantic
pip install uvicorn[standard]
pip install sqlalchemy psycopg2-binary sqlalchemy_utils
```

### Database Fields Creation (Run Outside of Virtual Environment)
```
python .\init_db.py
```

### Run Project (venv Command)
```
uvicorn main:app --reload
```
