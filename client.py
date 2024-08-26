import multiprocessing as mp
import socketio

gen_var = mp.Value('i',0)
sio = socketio.Client()

sio.connect('http://192.168.68.136:8585')

def motor():
    global motor_data
    motor_data = '0'
    sio.emit('Event General','R')
    while True:
        i = 0
        mot = 0
        motor_data = str(motor_data)
        print('Motor_data',motor_data)
        while mot == 0:
            i += 1
            sio.emit('Event Motor',motor_data)
            sio.sleep(0.270)
            if i == 50:
                mot = 1
            print(motor_data,'--------------------------------',i)

        motor_data = int(motor_data)
        if motor_data < 8:
            motor_data += 1
            if motor_data == '2':
                gen_var.value = 1
            else:
                gen_var.value = 0
        else:
            motor_data = 0
       

def actuator():
    act_data = '0'
    while True:
        print("Act_data",act_data)
        sio.emit('Event Actuator',act_data)
        sio.sleep(5)
        if act_data == 'a':
            act_data = 'b'
        elif act_data == 'b':
            act_data = 'c'
        else:
            act_data = 'a'


def power():
    pow_data = 'b'
    while True:
        sio.emit('Event Power',pow_data)
        sio.sleep(20)


def general():
    gen_data = '0'
    while True:
        print("Gen_Data",gen_data)
        sio.emit('Event General',gen_data)
        sio.sleep(10)
        if gen_data == '0' and gen_var.value == 0:
            gen_data = 'a'
        else:
            gen_data = '0'


if __name__ == '__main__':

        mp.freeze_support()
        process1 = mp.Process(target=motor)
        process2 = mp.Process(target=power)
        process3 = mp.Process(target=general)
        process4 = mp.Process(target=actuator)

        process1.start()
        process2.start()
        process3.start()
        process4.start()

        process1.join()
        process2.join()
        process3.join()
        process4.join()
