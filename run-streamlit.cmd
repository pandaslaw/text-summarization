@echo off

call venv\Scripts\activate.bat

set PYTHONPATH=%PYTHONPATH%;.\src

python -m streamlit run ./src/run_streamlit.py -- --data_source_file_name sample.json