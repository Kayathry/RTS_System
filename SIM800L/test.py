import time
from sim800l import SIM800L
import logging
import serial
logging.getLogger().setLevel(5)

sim800l = SIM800L(port='/dev/serial0', 
                  baudrate=115200, 
                  timeout=3.0)

sim800l.setup()

print(sim800l.check_sim())
print("Unit Name:", sim800l.get_unit_name())
