from byte_utils import *


def switch_off_light(address):
    send_bytes([10, 6, 0, address, 0, 0], 4)
    return True


def switch_blink_light(address):
    send_bytes([10, 6, 0, address, 0, 255], 4)
    return True


def switch_on_light(address):
    send_bytes([10, 6, 0, address, 255, 255], 4)
    return True


def set_module_closed(address):
    send_bytes([10, 16, 0, address, 0, 2, 4,  0, 0, 0, 0])


def set_module_closing(address):
    send_bytes([10, 16, 0, address, 0, 2, 4,  255, 255, 0, 255])


def set_module_opened(address):
    send_bytes([10, 16, 0, address, 0, 2, 4,  255,255,255,255])


def set_module_opening(address):
    send_bytes([10, 16, 0, address, 0, 2, 4,  0, 255, 255, 255])



def set_furnace(value1, value2):
    resp = send_bytes([10, 16, 0, 1, 0, 2, 4,  0, value1, 0, value2], 4)
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