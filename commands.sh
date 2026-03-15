#!/bin/bash

# Start nginx
sudo systemctl start nginx

# Activate environment
source ~/lab-website/venv/bin/activate

# Run paper 1
cd ~/lab-website/app/paper-1/ || exit
nohup streamlit run app.py \
  --server.port 8080 \
  --server.baseUrlPath paper1 \
  > paper1.log 2>&1 &

# Run paper 2
cd ~/lab-website/app/paper-2/ || exit
nohup streamlit run app.py \
  --server.port 8081 \
  --server.baseUrlPath paper2 \
  > paper2.log 2>&1 &

# Restart nginx
sudo systemctl restart nginx