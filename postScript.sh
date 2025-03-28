#!/bin/bash

# Navigate to the deployment directory
cd /home/ec2-user/deploy

# Activate virtual environment (if applicable)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Start Streamlit frontend
nohup streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0 &

# Confirm that the servers are running
ps aux | grep uvicorn
ps aux | grep streamlit

echo "FastAPI and Streamlit started successfully!"
