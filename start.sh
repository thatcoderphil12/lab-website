#!/usr/bin/env bash

set -e

URL="https://localhost"

echo "Detected OS: $OSTYPE"

start_nginx() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl start nginx
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start nginx 2>/dev/null || nginx
    elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* ]]; then
        echo "Skipping nginx start on Windows (assumed external)."
    else
        echo "Unknown OS for nginx start"
    fi
}

restart_nginx() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl restart nginx
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew services restart nginx 2>/dev/null || nginx -s reload
    elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* ]]; then
        echo "Skipping nginx restart on Windows."
    fi
}

open_browser() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "$URL"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        open "$URL"
    elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* ]]; then
        cmd.exe /c start "$URL"
    else
        echo "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

echo "Starting nginx..."
start_nginx

echo "Activating environment..."
source ~/lab-website/venv/bin/activate

echo "Starting paper1..."
(
cd ~/lab-website/app/paper-1/ || exit
nohup streamlit run app.py \
  --server.port 8080 \
  --server.baseUrlPath paper1 \
  > paper1.log 2>&1 &
)

echo "Starting paper2..."
(
cd ~/lab-website/app/paper-2/ || exit
nohup streamlit run app.py \
  --server.port 8081 \
  --server.baseUrlPath paper2 \
  > paper2.log 2>&1 &
)

echo "Restarting nginx..."
restart_nginx

echo "Opening browser..."
open_browser

echo "Done."