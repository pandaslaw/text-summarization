# News Summarizer

A dynamic app that summarizes essential news pieces related to cryptocurrencies and delivers updates to users either continuously or at specified intervals. Next to news and reports, it integrates insights from on-chain data and technical analysis.

## Project Setup

Install postgres  

Log in to postgres interactive terminal open command line and type:
> psql -U postgres   

To create a new database type in terminal:
> create database test;

To show list of databases:
> \l

1. Create .env file. Sample configs are in .env.sample file.
2. To run the application in project directory run  

> ./run-all.cmd  

## Database Setup

The project uses PostgreSQL as its database. To set up the database and tables:

1. Make sure PostgreSQL is installed and running
2. Navigate to the `sql` directory
3. Run `setup_database.bat`

The setup script will:
- Try to read database credentials from your `.env` file
- If not found, prompt you for the necessary information
- Create the database and all required tables
- Set up proper indexes and permissions

You can set the following environment variables before running the script to avoid prompts:
- `DB_USER`: PostgreSQL username (default: postgres)
- `DB_PASSWORD`: PostgreSQL password
- `DB_HOST`: PostgreSQL host (default: localhost)
- `DB_PORT`: PostgreSQL port (default: 5432)

Alternatively, ensure these values are set in your `.env` file.

### Docker
To run web app using Docker:
> docker build -t python-docker-image .  
> docker run python-docker-image
