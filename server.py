import asyncio
import socketio
import eventlet

sio = socketio.Server(async_mode='eventlet', ping_timeout=60)

app = socketio.WSGIApp(sio)

@sio.on('Event Motor')
def handle_event_motor(sid, data):
    print('[INFO(Control Server) -> Event Motor | Data -> {}'.format(data))

@sio.on('Event Actuator')
def handle_event_actuator(sid, data):
    print('[INFO(Control Server) -> Event Actuator | Data -> {}'.format(data))

@sio.on('Event Power')
def handle_event_power(sid, data):
    print('[INFO(Control Server) -> Event Power | Data -> {}'.format(data))

@sio.on('Event General')
def handle_event_general(sid, data):
    print('[INFO(Control Server) -> Event General | Page ID: Control] : Data -> {}'.format(data))

@sio.on('Latency')
def handle_latency(sid, data):
    print(f'[INFO(Control Server) -> Latency] : {data}')
    sio.emit('Latency', data)

@sio.on('Response Time')
def handle_response_time(sid, data):
    print(f'[INFO(Control Server) -> Response Time] : {data}')
    sio.emit('Response Time', data)

@sio.event
def connect(sid, environ, auth):
    print("[INFO(Control Server) -> Connect] : SID -> {}".format(sid))


@sio.event
def connect_error(sid, environ):
    print('[INFO(Control Server) -> Connection Error] : SID -> {} | Data -> {}'.format(sid, environ))


@sio.event
def disconnect(sid):
    print("[INFO(Control Server) -> Dis-Connect] : SID -> {}".format(sid))


async def control(ip_System, portServer):
    try:
        await eventlet.wsgi.server(eventlet.listen((ip_System, portServer)), app)
    except Exception as e:
        print('[INFO -> Control Server Error | Page ID: Control] :  Error -> {}'.format(e))


def main(ip_system, portServer):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(control(ip_system, portServer))


main('192.168.68.136', 8585)