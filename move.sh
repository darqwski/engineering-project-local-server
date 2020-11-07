PASSWORD=$1

sshpass -p PASSWORD scp /Users/generalautomatic/Desktop/EP-Raspberry/Python/main.py pi@192.168.0.128:/home/pi/SW/main.py
sshpass -p PASSWORD scp /Users/generalautomatic/Desktop/EP-Raspberry/Python/constants.py pi@192.168.0.128:/home/pi/SW/constants.py
sshpass -p PASSWORD scp /Users/generalautomatic/Desktop/EP-Raspberry/Python/byte_utils.py pi@192.168.0.128:/home/pi/SW/byte_utils.py
sshpass -p PASSWORD scp /Users/generalautomatic/Desktop/EP-Raspberry/Python/iot_utils.py pi@192.168.0.128:/home/pi/SW/iot_utils.py
sshpass -p PASSWORD scp /Users/generalautomatic/Desktop/EP-Raspberry/Python/app_requests.py pi@192.168.0.128:/home/pi/SW/app_requests.py