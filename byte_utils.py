import serial
from time import sleep


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


def send_bytes(to_send, to_receive = 0):
    #print("SENDING....")
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
        #print response
        serialPort.close()
    except IOError:
        print ("Failed at", "", "\n")

    return response