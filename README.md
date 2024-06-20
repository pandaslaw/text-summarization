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

### Docker
To run web app using Docker:
> docker build -t python-docker-image .  
> docker run python-docker-image

