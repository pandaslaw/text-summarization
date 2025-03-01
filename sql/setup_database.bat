@echo off
echo Setting up database and tables...

REM Try to load from .env file if it exists
if exist ..\.env (
    for /f "tokens=1,2 delims==" %%G in (..\.env) do (
        set %%G=%%H
    )
)

REM Set PostgreSQL connection details from environment variables or prompt
if not defined DB_USER (
    set /p DB_USER="Enter PostgreSQL username (default: postgres): " || set "DB_USER=postgres"
)
if not defined DB_PASSWORD (
    set /p DB_PASSWORD="Enter PostgreSQL password: "
)
if not defined DB_HOST (
    set /p DB_HOST="Enter PostgreSQL host (default: localhost): " || set "DB_HOST=localhost"
)
if not defined DB_PORT (
    set /p DB_PORT="Enter PostgreSQL port (default: 5432): " || set "DB_PORT=5432"
)

REM Set PostgreSQL environment variables
set PGUSER=%DB_USER%
set PGPASSWORD=%DB_PASSWORD%
set PGHOST=%DB_HOST%
set PGPORT=%DB_PORT%

REM Check if database exists
echo Checking database...
psql -lqt | findstr /B /C:"llm_reports" >nul
if errorlevel 1 (
    echo Creating database...
    createdb llm_reports
) else (
    echo Database already exists.
)

REM Create tables
echo Creating tables...
psql -d llm_reports -f 02_create_tables.sql

REM Clear sensitive environment variables
set PGPASSWORD=
set DB_PASSWORD=

echo Database setup completed!
