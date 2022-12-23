from PythonMcu.Hardware import NektarPanoramaTSeries
import logging
import time
from PySide2.QtCore import QTimer, Qt

logger = logging.getLogger("PythonMcu")
def log_wrapper(message, discard):
    logger.warning(message)

patch = "hammond"

hardware = NektarPanoramaTSeries("PANORAMA T6 Mixer", "PANORAMA T6 Mixer", log_wrapper, patch)

hardware.connect()
logger.warning("Check for connection...")


try:
    # setup event loop
    while True:
        latency = 0.001
        time.sleep(latency)
        hardware.process_midi_input()
except Exception as exc:
    print('{}: {}'.format(type(exc).__name__, exc))
finally:
    hardware.disconnect()
#time.sleep(30)
#logger.warning(hardware)
#logger.warning("Disconnecting...")
#hardware.disconnect()
