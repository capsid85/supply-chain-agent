#!/bin/bash
# Start FastAPI backend
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit frontend
streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0 &

# Wait for any process to exit
wait -n

# Exit with the status of the process that exited first
exit $?
