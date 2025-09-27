@echo off

@REM Install Python package
pip install -r requirements.txt
cls

@REM Run migrate
alembic upgrade head

@REM Run server
uvicorn main:app --reload
