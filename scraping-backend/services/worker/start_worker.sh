#!/bin/bash

# Basic Worker Startup Script
# This script activates the virtual environment and starts the worker

echo "Starting Basic Web Scraping Worker..."

# Navigate to the scraping-backend directory
cd "$(dirname "$0")/../.."

# Check if virtual environment exists
if [ -d "../../venv" ]; then
    echo "Activating virtual environment..."
    source ../../venv/bin/activate
elif [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Warning: Virtual environment not found. Make sure you have the required packages installed."
fi

# No additional dependencies needed for JSON display mode

# Start the worker
echo "Starting worker process..."
python services/worker/run_worker.py "$@"