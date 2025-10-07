@echo off

REM Set up environment variables for server
cd ./.docs
if not exist ".env" (
    echo Copying .env.example to .env...
    copy .env.example .env
)
cd ..

@REM Install Python package
pip install -r .\.docs\requirements.txt
cls

@REM Run migrate
alembic -c ./.migrations/alembic.ini upgrade head

@REM Run server
uvicorn main:app --reload
