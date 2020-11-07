import requests
from iot_utils import *
from app_requests import *
from constants import *


inputs = {
    'is_raining': False,
    'temperature': 30.5,
    'window': 'closed',
    'blinds': 'closed',
    'AC': 0,
    'furnace': 'off'
}
app_state = {
    'counter': 0,
    'furnace_turn_on': None,
    'furnace_going': False,
    'blinds_address': 10,
    'blinds_timer': None,
    'blinds_working': False,
    'blinds_state': None,
    'window_address': 20,
    'window_timer': None,
    'window_working': False,
    'window_state': None,
    'ac_address': 30,
    'ac_state': None
}


server_data = {}


login_data = {'login':'root','password':'root'}
host="http://192.168.0.31"
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
    session.post(host+"/API/status/",data=data)


def smart_program():
    print 'Na zewnatrz jest '
    print inputs['temperature']

    if inputs['temperature']<150:
        set_ac(0)
        if app_state['furnace_turn_on'] is None:
            furnace_going()
            app_state['furnace_turn_on']=app_state['counter']
        elif app_state['counter']-app_state['furnace_turn_on'] > 2 and app_state['furnace_going']==False:
            app_state['furnace_going']=True
            furnace_on()
        print 'Jest zimno, wlacz piec'
    else:
        app_state['furnace_going']=False
        app_state['furnace_turn_on']=None
        furnace_off()

    if 150 <= inputs['temperature'] < 200:
        set_ac(0)
        close_device('blinds')
        if not inputs['is_raining']:
            open_device('window')
        else:
            close_device('window')
        print 'Jest spoko, jak nie pada otworz okno'
    elif 200 <= inputs['temperature'] < 300:
        set_ac(0)
        if not inputs['is_raining']:
            open_device('blinds')
        else:
            close_device('blinds')
        print 'Jest cieplo, jak swieci to odslon rolety'
    elif inputs['temperature']>=300:
        close_device('blinds')
        close_device('window')
        set_ac(1)

    return True


def app_timers():
    print app_state
    app_state['counter']=app_state['counter']+1


def close_device(name):
    if app_state[name + '_state'] is True or app_state[name+'_state'] is None:
        app_state[name+'_timer']=app_state['counter']
        app_state[name+'_state']=False
        set_module_closing(app_state[name+'_address'])
    if not app_state[name + '_state']:
        if app_state[name+'_timer'] is not None:
            if app_state['counter']-app_state[name + '_timer'] == 1:
                app_state[name+'_timer']=None
                set_module_closed(app_state[name+'_address'])


def open_device(name):
    print 'open device'
    if app_state[name + '_state'] is False or app_state[name+'_state'] is None:
        app_state[name+'_timer']=app_state['counter']
        app_state[name+'_state']=True
        print 'start opening'
        set_module_opening(app_state[name+'_address'])
    if app_state[name + '_state']:
        if app_state[name+'_timer'] is not None:
            if app_state['counter']-app_state[name + '_timer'] == 1:
                print 'device opened'
                app_state[name+'_timer']=None
                set_module_opened(app_state[name+'_address'])


def set_ac(value):
    if app_state['ac_state'] is not value:
        app_state['ac_state']=value
        for i in range(value):
            print 'switching on ', i
            switch_on_light(app_state['ac_address']+i)
            sleep(1)
        for i in range(3-value):
            print 'switching off ', 2-i
            switch_off_light(app_state['ac_address'] + 2 - i)
            sleep(1)


def gather_inputs():
    data=get_input_registers()
    temperature = [data[3],data[4]]
    rain = [data[5],data[6]]

    inputs['temperature']=hex_to_int(temperature[0][0],temperature[0][1],temperature[1][0],temperature[1][1])
    inputs['temperature']=((inputs['temperature']*400/4096))
    #TEMPERATURE FROM 0 TO 40
    if rain[0]=='ff' and rain[1]=='ff':
        inputs['is_raining']=True
    else:
        inputs['is_raining']=False


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

print 'Reseting all devices'
for address in ADDRESS_ALL_LIGHTS:
    switch_off_light(address)
furnace_off()


while True:
    print 'GATHERING INPUTS'
    gather_inputs()
    print 'GATHERING DEVICES'
    get_devices()
    print 'UPDATING BUILDING STATUS'
    update_building_status()
    smart_program()
    sleep(1)
    app_timers()
    print 'CURRENT BUILDING STATUS'
    print inputs, app_state