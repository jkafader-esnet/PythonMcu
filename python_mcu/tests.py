from PythonMcu.Hardware import NektarPanoramaTSeries
import logging

logger = logging.getLogger("PythonMcu")
def log_wrapper(message, discard):
    logger.debug(message)

patch = "hammond"

hardware = NektarPanoramaTSeries("PANORAMA T6 Mixer", "PANORAMA T6 Mixer", log_wrapper, patch)

# mock this for testing -- now it returns a nicely formatted string instead of directing to port
hardware.midi.send_sysex = hardware.printable_hex

##################
# mixer mode
##################

output = hardware.mixer_mode()
assert(output == "F0 00 01 77 7F 01 06 02 7F 00 00 F7")
print(".", end=" ")


##################
# mixer mode
##################

output = hardware.pan_mode()
assert(output == "F0 00 01 77 7F 01 06 10 7F 00 00 F7")
print(".", end=" ")

##################
# soft buttons
##################

output = hardware.set_display_area("soft_buttons", ["PAN", "SENDS", "", "WRITE"])
assert(output == "F0 00 01 77 7F 01 06 00 04 00 04 00 00 00 01 00 01 03 50 41 4E 00 02 05 53 45 4E 44 53 00 03 00 00 04 05 57 52 49 54 45 00 05 00 F7")
print(".", end=" ")

##################
# set track names
##################

output = hardware.set_display_area("track_names_1-4", ["1", "2", "3", "4"])
assert(output == "F0 00 01 77 7F 01 06 00 06 09 01 31 00 0A 01 32 00 0B 01 33 00 0C 01 34 F7")
print(".", end=" ")

output = hardware.set_display_area("track_names_5-8", ["5", "6", "7", "8"])
assert(output == "F0 00 01 77 7F 01 06 00 06 0D 01 35 00 0E 01 36 00 0F 01 37 00 10 01 38 F7")
print(".", end=" ")

output = hardware.set_display_area("pan_values_1-4", ["", "", "", ""])
assert(output == "F0 00 01 77 7F 01 06 00 07 01 00 00 02 00 00 03 00 00 04 00 F7")
print(".", end=" ")

output = hardware.set_display_area("pan_values_5-8", ["", "", "", ""])
assert(output == "F0 00 01 77 7F 01 06 00 07 05 00 00 06 00 00 07 00 00 08 00 F7")
print(".", end=" ")

#####################
# set pan switches
#####################

output = hardware.set_display_area("pan_names_1-4", ["1", "2", "3", "4"])
assert(output == "F0 00 01 77 7F 01 06 00 06 01 01 31 00 02 01 32 00 03 01 33 00 04 01 34 F7")
print(".", end=" ")

output = hardware.set_display_area("pan_names_5-8", ["5", "6", "7", "8"])
assert(output == "F0 00 01 77 7F 01 06 00 06 05 01 35 00 06 01 36 00 07 01 37 00 08 01 38 F7")
print(".", end=" ")

output = hardware.set_display_area("pan_values_1-4", ["-C-", "-C-", "-C-", "-C-"])
assert(output == "F0 00 01 77 7F 01 06 00 07 01 03 2D 43 2D 00 02 03 2D 43 2D 00 03 03 2D 43 2D 00 04 03 2D 43 2D F7")
print(".", end=" ")

output = hardware.set_display_area("pan_values_5-8", ["-C-", "-C-", "-C-", "-C-"])
assert(output == "F0 00 01 77 7F 01 06 00 07 05 03 2D 43 2D 00 06 03 2D 43 2D 00 07 03 2D 43 2D 00 08 03 2D 43 2D F7")
print(".", end=" ")

##################
# test empty string
##################

output = hardware.set_display_area("unknown", ["", "", ""])
assert(output == "F0 00 01 77 7F 01 06 00 01 01 00 00 02 00 00 03 00 F7")
print(".", end=" ")


print()