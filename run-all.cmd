@echo off

python -m venv venv
call venv\Scripts\activate.bat

pip install -r requirements.txt

python -m src.database

python -m src.main

streamlit run ./src/run_streamlit.py
