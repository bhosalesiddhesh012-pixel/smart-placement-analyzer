#!/bin/bash
echo "Stopping old servers on ports 5001-5005..."
kill -9 $(lsof -t -i:5001 -i:5002 -i:5003 -i:5004 -i:5005 2>/dev/null) 2>/dev/null
sleep 1
echo "Starting fresh application server..."
python3 start.py
