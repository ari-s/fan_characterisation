'''PWM fan characterisation: ramp through PWM duty cycle and log speed'''
gpiopath = '/dev/gpiochip0'  # periphery uses the chardev for GPIO
speed_pin = 6 #  'GPIO6'

chip = 0  # but the sysfs chip # for PWM
pwm_channel = 0
pwm_freq = 25e3

step_length = 2  # hold PWM for this amount of time
repititions = 3  # PWM is ramped up and down this amount of times

from periphery import PWM, GPIO
import time
from itertools import chain

readspeed = GPIO(gpiopath, speed_pin, 'in')
readspeed.edge = 'rising'
control = PWM(chip, pwm_channel)
control.frequency = pwm_freq
control.duty_cycle = 0
control.enable()

dutyiters = []
for i in range(repititions):
    dutyiters.extend((
        range(0, 101),  # want to include the end
        range(100, -1, -1)  # same
    ))

speedevents = []

for duty in chain(*dutyiters):
    duty/=100
    # seems like it's only effective to change the duty cycle when the pwm is disabled?
    control.disable()
    control.duty_cycle = duty
    control.enable()
    
    startcycle = time.time()
    readspeed.poll()
    dutysevents = []
    while (eventtime := time.time()) < startcycle + step_length:
        readspeed.poll()  # returns on edge event
        dutysevents.append(readspeed.read_event().timestamp)
    td = [(t1-t0)/1e9 for t1, t0 in zip(dutysevents[1:], dutysevents[:-1])]
    speedevents.append((duty, td))
    freq = len(td) / sum(td)
    print(f'{duty:.2f}: {freq * 60/2:.0f} rpm')
        
    
    
