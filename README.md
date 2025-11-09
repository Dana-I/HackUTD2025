# HackUTD2025

Clone repo and run following command:
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

pip freeze > requirements.txt

To run programs:
1. Start FastAPI (uvicorn app:app --reload)
2. Start USB reader (python3 usb_reader.py)
3. Start Streamlit dashboard (streamlit run app.py)
