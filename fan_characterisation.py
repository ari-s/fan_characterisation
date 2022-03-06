'''PWM fan characterisation: ramp through PWM duty cycle and log speed

Defaults are for Raspberry Pis with enabled PWM outputs,
but this should work on all linux computers with PWM and GPIO
Make sure the pins are not used otherwise!
'''

from periphery import PWM, GPIO
import time
from itertools import chain
from tap import Tap
from numbers import Real
from typing import Optional
from pathlib import Path


class _FanCharacterisationArgs(Tap):
    __doc__ = f'''{__doc__}\nresults are written to stdout as list:
    $duty: $frequency rpm'''
    gpioChip: Path = '/dev/gpiochip0'   # Path to GPIO chip
    tachopin: int = 6                   # Pin Nr
    pwmchip_nr: int = 0                 # chip nr, as in /sys/class/pwm/pwmchip{pwmchip_nr}
    pwmchannel_nr: int = 0              # channel nr as in /sys/class/pwm/pwmchip0/pwm{pwmchannel_nr}
    step_length: float = 1.             # hold every step for this amount of seconds
    step_height: int = 1                # increase PWM duty cycle by `step` percent
    repititions: int = 1                # ramp up and down this amount of times


def fan_characterisation(
    gpioChip: Path = '/dev/gpiochip0',  # Path to GPIO chip
    tachopin: int = 6,                  # Pin Nr
    pwmchip_nr: int = 0,                # chip nr, as in /sys/class/pwm/pwmchip{pwmchip_nr}
    pwmchannel_nr: int = 0,             # channel nr as in /sys/class/pwm/pwmchip0/pwm{pwmchannel_nr}
    step_length: float = 1.0,           # hold every step for this amount of seconds
    step_height: int = 1,               # increase PWM duty cycle by `step` percent
    repititions: int = 1,               # ramp up and down this amount of times
    pwm_freq: float = 25e3,             # PWM frequency, 25 kHz is standard for fans
    print_results: bool = False         # whether to print results. This is for CLI-mode
    ) -> Optional[list]:
    readspeed = GPIO(str(gpioChip), tachopin, 'in')
    readspeed.edge = 'rising'

    control = PWM(pwmchip_nr, pwmchannel_nr)
    control.frequency = pwm_freq
    control.duty_cycle = 0
    control.enable()

    speedevents = []
    dutyiters = []
    for i in range(repititions):
        dutyiters.extend((
            range(0, 101, step_height),  # want to include the end
            range(100, -1, -step_height)  # same
        ))

    if print_results:
        print('duty  frequency')

    for duty in chain(*dutyiters):
        duty/=100
        # seems like it's only effective to change the duty cycle when the pwm is disabled?
        control.disable()
        control.duty_cycle = duty
        control.enable()

        startcycle = time.time()
        readspeed.poll(timeout=1)
        dutysevents = []
        while (eventtime := time.time()) < startcycle + step_length:
            # .poll() is supposed to return on an edge event,
            # but it is necessary to .read_event(),
            # otherwise .poll() will not wait until the next event.
            if readedge := readspeed.poll(timeout=1):
                dutysevents.append(readspeed.read_event().timestamp)

        td = [(t1-t0)/1e9 for t1, t0 in zip(dutysevents[1:], dutysevents[:-1])]
        if len(td) == 0:
            freq = 0
        else:
            freq = len(td) / sum(td)
        if print_results:
            print(f'{duty:.2f}: {freq * 60/2:.0f} rpm')

        speedevents.append((duty, td))
    return speedevents


if __name__ == '__main__':
    argparse = _FanCharacterisationArgs()
    argparse.description = _FanCharacterisationArgs.__doc__
    args = argparse.parse_args().as_dict()
    fan_characterisation(**args, print_results=True)

