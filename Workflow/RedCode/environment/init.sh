#!/bin/bash

# apt-get update
# apt-get install xxd
# apt-get install wget
# apt-get install -y curl

# pip install flask
# pip install requests
# pip install pyyaml
# pip install jsonpickle
# pip install psutil
# pip install pyperclip
# pip install pillow
# pip install watchdog
# chmod +x start_processes.sh
./start_processes.sh &
python index1-server.py &
python index10-server.py &

bash