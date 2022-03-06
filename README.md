# Fan_characterisation

Measure a PWM fan's rotation frequency (RPM) as a function of PWM duty cycle

## Installation

The usual installation options apply:

- TBD: `pip install fan_characterisation`
- `pip install git+https://github.com/ari-s/fan_characterisation`
- `git clone https://github.com/ari-s/fan_characterisation`
  you need to have python-periphery and typed-argument-parser installed

## Usage

This can be used both as a CLI program as well as within python.
In python, you'll get a list of all tachometer readings, not just frequency

### CLI

See `python -m fan_characterisation --help

### python

See `import fan_characterisation; help(fan_characterisation)`
