import RPi.GPIO as GPIO
from time import sleep
import serial
import requests
import json


ADDRESS_FURNACE=1
ADDRESS_FURNACE_DETAILS=2
#GREEN
ADDRESS_LIGHTS_BLIND_ON=10
ADDRESS_LIGHTS_BLIND_OFF=11
#BLUE
ADDRESS_LIGHTS_WINDOW_ON=20
ADDRESS_LIGHTS_WINDOW_OFF=21

#BLUE
ADDRESS_LIGHTS_1=30
ADDRESS_LIGHTS_2=31
ADDRESS_LIGHTS_3=32

#INPUTS
ADDRESS_TEMPERATURE=0
ADDRESS_RAIN=1

ADDRESS_ALL_LIGHTS = [
    ADDRESS_LIGHTS_BLIND_ON, ADDRESS_LIGHTS_BLIND_OFF, ADDRESS_LIGHTS_WINDOW_ON, ADDRESS_LIGHTS_WINDOW_OFF, ADDRESS_LIGHTS_1, ADDRESS_LIGHTS_2, ADDRESS_LIGHTS_3
]
inputs = {
    'is_raining': False,
    'temperature': 30.5,
    'window': 'closed',
    'blinds': 'closed',
    'AC': 0,
    'furnace': 'off'
}

def char_to_int(char):
    if char == '0' :
        return 0
    if char == '1' :
        return 1
    if char == '2' :
        return 2
    if char == '3' :
        return 3
    if char == '4' :
        return 4
    if char == '5' :
        return 5
    if char == '6' :
        return 6
    if char == '7' :
        return 7
    if char == '8' :
        return 8
    if char == '9' :
        return 9
    if char == 'a' :
        return 10
    if char == 'b' :
        return 11
    if char == 'c' :
        return 12
    if char == 'd' :
        return 13
    if char == 'e' :
        return 14
    if char == 'f' :
        return 15


def hex_to_int(char1, char2, char3, char4):
    return char_to_int(char1)*16*16*16+char_to_int(char2)*16*16+char_to_int(char3)*16+char_to_int(char4)


def switch_off_light(address):
    send_bytes([10, 6, 0, address, 0, 0], 4)
    return True


def switch_blink_light(address):
    send_bytes([10, 6, 0, address, 0, 255], 4)
    return True


def switch_on_light(address):
    send_bytes([10, 6, 0, address, 255, 255], 4)
    return True




def set_furnace(value1, value2):
    resp = send_bytes([10, 16, 0, 1, 0, 2, 4,  0, value1, 0, value2], 4)
    print resp
    sleep(1)
    #resp = send_bytes([10, 6, 0, 2, 0, value2], 6)
    #print resp
    #sleep(1)
    return True
def furnace_off():
    set_furnace(0,0)
def furnace_on():
    set_furnace(1,0)
def furnace_going():
    set_furnace(2,0)
#amount = 1,2,5
def furnace_add(amount = 1):
    set_furnace(3,amount)

def get_input_register(address):
    send_bytes([10, 4, 0, address, 255, 255], 4)
    return True


def get_input_registers():
    return send_bytes([10, 4, 0, 0, 0, 2], 8)

def gather_inputs():
    data=get_input_registers()
    temperature = [data[3],data[4]]
    rain = [data[5],data[6]]

    inputs['temperature']=hex_to_int(temperature[0][0],temperature[0][1],temperature[1][0],temperature[1][1])
    inputs['temperature']=((inputs['temperature']*300/4096))
    #TEMPERATURE FROM 0 TO 30
    if rain[0]=='ff' and rain[1]=='ff':
        inputs['is_raining']=True
    else:
        inputs['is_raining']=False

def read_double_bytes(byte_a_1, byte_a_2,byte_b_1, byte_b_2):
    open_status=0
    close_status=0
    if byte_a_1=='ff' and byte_a_2=='ff':
        open_status='on'
    if byte_a_1=='ff' and byte_a_2!='ff':
        open_status='working'
    if byte_a_1!='ff' and byte_a_2!='ff':
        open_status='off'
    if byte_b_1=='ff' and byte_b_2=='ff':
        close_status='on'
    if byte_b_1=='ff' and byte_b_2!='ff':
        close_status='working'
    if byte_b_1!='ff' and byte_b_2!='ff':
        close_status='off'

    if close_status=='off' and open_status=='off':
        return 'closed'
    if close_status=='on' and open_status=='on':
        return 'opened'
    if close_status=='on' and open_status=='working':
        return 'opening'
    if close_status=='working' and open_status=='on':
        return 'closing'

    return 'error'


def read_furnace(byte_a_1, byte_a_2,byte_b_1, byte_b_2):
    print [byte_a_1, byte_a_2,byte_b_1, byte_b_2]
    if byte_a_2=='01':
        return 'on'
    if byte_a_2=='02':
        return 'running'
    if byte_a_2=='03' and byte_b_2 == '01':
        return 'added 1kg'
    if byte_a_2=='03' and byte_b_2 == '02':
        return 'added 2kg'
    if byte_a_2=='03' and byte_b_2 == '05':
        return 'added 5kg'

    return 'error'


def get_devices():
    ac=send_bytes([10, 3, 0, 30, 0, 3], 10)
    ac_booleans=[ac[3]=='ff', ac[5]=='ff', ac[7]=='ff']
    ac_value=0
    for single_value in ac_booleans:
        if single_value:
            ac_value=ac_value+1
    inputs['AC']=ac_value
    window=send_bytes([10, 3, 0, 20, 0, 2], 8)
    blinds=send_bytes([10, 3, 0, 10, 0, 2], 8)
    furnace=send_bytes([10, 3, 0, 1, 0, 2], 8)
    inputs['window']= read_double_bytes(window[3],window[4], window[5],window[6])
    inputs['blinds']= read_double_bytes(blinds[3],blinds[4], blinds[5],blinds[6])
    inputs['furnace']= read_furnace(furnace[3],furnace[4], furnace[5],furnace[6])


def send_bytes(to_send, to_receive = 0):
    print("SENDING....")
    try:
        serialPort = serial.Serial(
            port = "/dev/ttyACM0",
            timeout = 2,
            parity = serial.PARITY_NONE,
            baudrate = 9600,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE
        )
        serialPort.write(to_send)
        sleep(1)
        response = []
        while True:
            c = serialPort.read()
            if len(c) == 0:
                break

            response.append(c.encode('hex'))
        print response
        serialPort.close()
    except IOError:
        print ("Failed at", "", "\n")

    return response


server_data = {}

login_data = {'login':'root','password':'root'}
host="http://192.168.0.31";
#host="https://dariuszcabala.pl/engineering";
def get_data_from_server():
    session = requests.Session()
    session.post(host+'/API/login/',data = login_data)
    get_request = session.get(host+"/API/program/")
    server_data = get_request.text
    print(server_data)
def update_building_status():
    session = requests.Session()
    session.post(host+'/API/login/',data = login_data)
    data={'inputs':json.dumps(inputs)}
    response = session.post(host+"/API/status/",data=data)
    print response.text


for address in ADDRESS_ALL_LIGHTS:
    #switch_on_light(address)
    print("SWITCHING ON", address)
    #sleep(1)
#furnace_on()
while(True):
   # furnace=send_bytes([10, 3, 0, 1, 0, 2], 8)
   # print 'furnace, ', furnace
   # furnace=send_bytes([10, 3, 0, 1, 0, 2], 8)
    furnace=send_bytes([10, 3, 0, 1, 0, 2], 8)
    print 'furnace, ', furnace
    furnace=send_bytes([10, 3, 0, 1, 0, 2], 8)
    print 'furnace, ', furnace
    furnace_off()
    sleep(2)
    continue
    # furnace_on()
    # sleep(2)
    # get_devices()
    # print inputs
    #continue

    gather_inputs()
    get_devices()
    update_building_status()
    print json.dumps(inputs)
    sleep(1)
    continue
    #BLINK LIST
    for address in ADDRESS_ALL_LIGHTS:
        switch_off_light(address)
        print("SWITCHING OFF", address)
        sleep(1)
    for address in ADDRESS_ALL_LIGHTS:
        switch_on_light(address)
        print("SWITCHING ON", address)
        sleep(1)
    continue
    switch_blink_light(ADDRESS_LIGHTS_WINDOW_OFF)
    sleep(1)
    switch_off_light(ADDRESS_LIGHTS_WINDOW_ON)
    sleep(2)
    switch_blink_light(ADDRESS_LIGHTS_WINDOW_ON)
    sleep(1)
    switch_off_light(ADDRESS_LIGHTS_WINDOW_OFF)
    sleep(2)
    switch_on_light(ADDRESS_LIGHTS_WINDOW_ON)
    sleep(1)
    switch_on_light(ADDRESS_LIGHTS_WINDOW_OFF)
    sleep(1)