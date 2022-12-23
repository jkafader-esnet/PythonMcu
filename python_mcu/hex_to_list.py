import sys

if len(sys.argv) < 2:
    raise Exception("this program takes a number of arguments: hex bytes to form into a list")

print("data = [0x" + ", 0x".join(item for item in sys.argv[1:]) + "]")
print("self.midi.send_sysex(self.standard_syx_header, data)")