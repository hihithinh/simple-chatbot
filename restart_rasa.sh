#!/bin/bash

# Kill any running Rasa processes
pkill -f 'rasa run'

# Wait for processes to terminate
sleep 2

# Change to the Rasa directory
cd /Users/linoedge/study/study-projects/chatbot/rasa

# Set environment variables
export RASA_ACTION_SERVER="http://localhost:5055"

# Activate the virtual environment and start Rasa
source ../.venv/bin/activate && python -m rasa run --enable-api --cors '*'
