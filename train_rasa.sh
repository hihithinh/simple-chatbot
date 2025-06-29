#!/bin/bash

# Change to the Rasa directory
cd /Users/linoedge/study/study-projects/chatbot/rasa

# Set environment variables
export RASA_ACTION_SERVER="http://localhost:5055"

# Activate the virtual environment and train Rasa
source ../.venv/bin/activate && python -m rasa train
