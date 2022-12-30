from PythonMcu.Hardware import NektarPanoramaTSeries
import logging
import time

logger = logging.getLogger("PythonMcu")
def log_wrapper(message, discard):
    logger.warning(message)

patch = b"B3 Organ"

INSTRUMENTS = [
    b"Pianoteq",
    b"B3 Organ",
    b"Minimoog",
    b"Oberheim",
    b"Wurlitzer",
    b"Solina",
]

class DummyController(object):
    def __init__(self):
        self.inst_ptr = 0
    def get_current_instrument_name(*args, **kwargs):
        return b"B3 Organ"
    def change_instrument(self, increment):
        self.inst_ptr += increment
        if self.inst_ptr >= len(INSTRUMENTS):
            self.inst_ptr = 0
        if self.inst_ptr < 0:
            self.inst_ptr = len(INSTRUMENTS) - 1
    def get_current_instrument_name(self):
        return INSTRUMENTS[self.inst_ptr]
    def send_midi(self, message):
        pass
        #logger.warning("[DUMMY] send midi: %s" % (" ".join([hex(c).replace("0x", "").upper().zfill(2) for c in message]) ) )

controller = DummyController()

hardware = NektarPanoramaTSeries("PANORAMA T6 Mixer", "PANORAMA T6 Mixer", log_wrapper, patch, controller)

hardware.connect()
logger.warning("Check for connection...")

try:
    # setup event loop
    while True:
        time.sleep(1)
        pass
except Exception as exc:
    print('{}: {}'.format(type(exc).__name__, exc))
finally:
    hardware.disconnect()
