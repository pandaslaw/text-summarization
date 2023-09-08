@echo off

call venv\Scripts\activate.bat

set PYTHONPATH=%PYTHONPATH%;.\src

streamlit run ./src/run_streamlit_one_article.py
