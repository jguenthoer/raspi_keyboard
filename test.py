import time
import RPi.GPIO as GPIO

clock = 10
data = 16
GPIO.setmode(GPIO.BOARD)
GPIO.setup(clock, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(data, GPIO.OUT)
shift = 0x0
counter = 0
t_global = time.time()

def callback_send(clock):
    global shift
    global counter
    global t_global
    tx = shift&0x80 # only send highest bit
    GPIO.output(data, tx) # write bit to bus on falling edge
    end = time.time() - t_global
    t_global = time.time()
    print('tx', tx, end)
    shift = shift<<1
    counter += counter
    

def send(command):
    GPIO.setup(data, GPIO.OUT)
    global shift
    global counter
    GPIO.add_event_detect(clock, GPIO.FALLING, callback = callback_send)
    # check clock via callback, bits are writen in callback
    shift = command
    t_end = time.time()+30
    GPIO.output(data, 0) # data line low -> start signal for kb
    while counter < 8:
        time.sleep(0.01)
        if time.time() > t_end:
            print('send timeout')
            break

    GPIO.remove_event_detect(clock)
    # all bits received, stop interrupt

    counter = 0
    return
##    shift = command #shift register for sending the command
##    for bit in range(8):
##        tx = shift&0x80 # only send highest bit
##        start = time.clock()
##        GPIO.wait_for_edge(clock, GPIO.FALLING)
##        GPIO.output(data, tx) # write bit to bus on falling edge
##        end = time.clock() - start
##        print('tx', tx, end)
##        shift = shift<<1

def receive():
    GPIO.setup(data, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    shift = 0 # init shift register
    for bit in range(8):
        shift = shift<<1
        GPIO.wait_for_edge(clock, GPIO.RISING)
        rx = GPIO.input(data)
        shift = shift|rx
        print('rec', shift)

    return(shift)
    
# init and modelnumber checking for test
GPIO.output(data, 128)
channel = GPIO.wait_for_edge(clock, GPIO.FALLING, timeout=5000)
time.sleep(3)
    

send(0x14) # send model number cmd for init
time.sleep(0.01)
GPIO.output(data, 1) # set data high -> ready to receive
GPIO.wait_for_edge(clock, GPIO.FALLING) # wait for kb to transmit
model = receive()
print(model)
GPIO.cleanup()

