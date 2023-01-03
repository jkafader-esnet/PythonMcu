from PythonMcu.Hardware import NektarPanoramaTSeries
from PythonMcu.configuration.patches import control_mapping
import liblo

import sys
import rtmidi
from rtmidi.midiutil import open_midiinput
import sys
import logging
import time

COMMANDS = {
    'HANDSHAKE': 0x2F,
    'QUERY_NUM_CHAINS': 0x0A,
    'QUERY_CHAIN_ENGINES': 0x0B,
    'QUERY_CHAIN_PATCHES': 0x0C,
    'QUERY_CHAIN_PATCH': 0x0D,
    'QUERY_CHAIN_CONTROLS': 0x0E,
    'QUERY_CHAIN_CHANNELS': 0x0F,
    
    'SAVE_CHAIN_PATCH': 0x70,
    'SET_CHAIN_PATCH': 0x71,
}

COMMAND_REVERSE = { v: k for k, v in COMMANDS.items() }

class APIClient(object):
    def __init__(self):
        self.syx = 0xF0
        self.txn_id = 0
        self.seq_id = 0
        mfg = [0x01, 0x31, 0x70]
        dev = 0x3F
        self.is_request = 0x12
        self.is_response = 0x13
        self.request_header = [self.syx, mfg[0], mfg[1], mfg[2], dev, self.is_request]
        self.response_header = [self.syx, mfg[0], mfg[1], mfg[2], dev, self.is_response]
        self.footer = [0xF7]
        self.client_id = 0x3F

        self.populated = { command: False for command in COMMANDS }
        self.populated['QUERY_CHAIN_CONTROLS'] = []
        self.populated['QUERY_CHAIN_CONTROLS_ALL'] = False
        
        self.chain_controls = {}
        self.logger = logging.getLogger("Midi IN")
        logging.basicConfig(level=logging.DEBUG)
        self.midiout = rtmidi.MidiOut()
        self.port_list = self.midiout.get_ports()
        self.logger.warning("Available ports: %s", self.port_list)
        self.port_num = None
        for i in range(len(self.port_list)):
            port = self.port_list[i]
            if "Sysex API" in port:
                self.port_num = i
                break
        if self.port_num is None:
            sys.exit("couldn't find appropriate port")
        self.midiout.open_port(self.port_num)
        self.midiin, self.port_name = open_midiinput(self.port_num)
        self.midiin.ignore_types(sysex=False)
        self.midiin.set_callback(self.receive)
        self.logger.warning("connected to port %s", self.port_name)

    def receive(self, event, data):
        message, deltatime = event
        if message[0] == self.syx:
            message = self.strip_response(message)
            if message[0] == self.client_id and message[1] in COMMAND_REVERSE:
                command = COMMAND_REVERSE[message[1]]
                if hasattr(self, "receive_%s" % command):
                    getattr(self, "receive_%s" % command)(message)
                else:
                    self.logger.warning("malformed sysex response %s" % message)

    def send(self, message):
        message = self.format_query(message)
        print(self.format_hex(message, h=True))
        self.midiout.send_message(message)
        self.txn_id += 1
        self.seq_id += 1

    def send_midi(self, message):
        self.midiout.send_message(message)
        
    def format_hex(self, message, h=True):
        if h:
            return " ".join([hex(num).replace("0x", "") for num in message])
        else:
            return " ".join([str(num) for num in message])

    def format_query(self, message):
        return self.request_header + message + self.footer

    def strip_response(self, message):
        for b in self.response_header:
            if message[0] == b:
                message.pop(0)
        for b in self.footer:
            if message[-1] == b:
                message.pop(-1)
        return message

    def send_HANDSHAKE(self):
        command = COMMANDS['HANDSHAKE']
        self.send([command, self.client_id, self.txn_id, self.seq_id])

    def receive_HANDSHAKE(self, message):
        self.logger.warning("receive_QUERY_NUM_CHAINS %s", message)
        self.populated['HANDSHAKE'] = True

    def send_QUERY_NUM_CHAINS(self):
        command = COMMANDS['QUERY_NUM_CHAINS']
        self.send([command, self.client_id, self.txn_id, self.seq_id])

    def receive_QUERY_NUM_CHAINS(self, message):
        self.logger.warning("receive_QUERY_NUM_CHAINS %s", message)
        self.count_chains = message[4]
        print("there are currently %s total root chains" % self.count_chains)
        if self.count_chains:
            self.populated['QUERY_NUM_CHAINS'] = True

    def send_QUERY_CHAIN_CONTROLS(self, channel):
        command = COMMANDS['QUERY_CHAIN_CONTROLS']
        self.send([command, self.client_id, self.txn_id, self.seq_id, channel])

    def receive_QUERY_CHAIN_CONTROLS(self, message):
        self.logger.warning("receive_QUERY_CHAIN_CONTROLS %s", message)
        chain_channel = message[4]
        chain_controls_response = self.bytes_to_dict(message[5:])
        self.chain_controls[chain_channel] = {}
        for k, v in chain_controls_response.items():
            curval, minval, maxval, name = v.split(b":")
            name = name.decode("UTF-8")
            curval = int(curval)
            minval = int(minval)
            maxval = int(maxval)
            self.chain_controls[chain_channel][name] = {
                "cc": k,
                "cur": curval,
                "min": minval,
                "max": maxval,
            }
        self.logger.warning("chain controls %s" % self.chain_controls.keys())
        self.logger.warning("chain controls %s" % self.chain_controls)
        if self.chain_controls[chain_channel]:
            curr_val = self.populated.get('QUERY_CHAIN_CONTROLS', [])
            curr_val.append(chain_channel)
            self.populated['QUERY_CHAIN_CONTROLS'] = curr_val
            if self.populated['QUERY_CHAIN_CHANNELS']:
                if sorted(list(self.chain_controls.keys())) == sorted(self.chain_channels):
                    self.populated['QUERY_CHAIN_CONTROLS_ALL'] = True

    def send_QUERY_CHAIN_CHANNELS(self):
        command = COMMANDS['QUERY_CHAIN_CHANNELS']
        self.send([command, self.client_id, self.txn_id, self.seq_id])

    def receive_QUERY_CHAIN_CHANNELS(self, message):
        self.logger.warning("receive_QUERY_CHAIN_CHANNELS %s", message)
        self.chain_channels = message[4:]
        print("chains are on channels %s" % self.chain_channels)
        if self.chain_channels:
            self.populated['QUERY_CHAIN_CHANNELS'] = True

    def send_QUERY_CHAIN_ENGINES(self):
        command = COMMANDS['QUERY_CHAIN_ENGINES']
        self.send([command, self.client_id, self.txn_id, self.seq_id])

    def bytes_to_dict(self, bytestring):
        out = {}
        while bytestring:
            chan = bytestring[0]
            bytestring = bytestring[1:]
            name = bytestring[1:bytestring[0]+1]
            bytestring = bytestring[bytestring[0]+2:]
            out[chan] = bytes(name)
        return out
    
    def receive_QUERY_CHAIN_ENGINES(self, message):
        self.logger.warning("receive_QUERY_CHAIN_ENGINES: %s", message)
        self.chain_engines = self.bytes_to_dict(message[4:])
        self.logger.warning("chain engines: %s" % self.chain_engines)
        if self.chain_engines:
            self.populated['QUERY_CHAIN_ENGINES'] = True
            
    def close(self):
        self.midiin.close_port()
        self.midiout.close_port()
        del self.midiin
        del self.midiout

PRETTY_LOOKUP = {
    "PT": "Pianoteq",
    "BF": "B3 Organ",
    "LS": "Wurlitzer",
    "JV/String machine": "Solina",
    "JV/Obxd": "Oberheim",
    "JV/Raffo Synth": "Minimoog",
}
        
class ZynMCUController(object):
    def __init__(self):
        self.logger = logging.getLogger("ZynMCUController")
        logging.basicConfig(level=logging.DEBUG)

        self.client = APIClient()
        patch = b'Pianoteq'
        self.hardware = NektarPanoramaTSeries("PANORAMA T6 Mixer", "PANORAMA T6 Mixer", self.log_wrapper, patch, controller=self)
        
        self.addr=liblo.Address('osc.udp://localhost:1370')
        self.curr_instrument = 0

        self.midiout = rtmidi.MidiOut()
        self.port_list = self.midiout.get_ports()
        self.logger.warning("Available ports: %s", self.port_list)
        self.port_num = None
        for i in range(len(self.port_list)):
            port = self.port_list[i]
            if "Midi Through Port" in port:
                self.port_num = i
                break
        if self.port_num is None:
            sys.exit("couldn't find appropriate port")
        self.midiout.open_port(self.port_num)

    def send_midi(self, message):
        self.midiout.send_message(message)
        
    def change_instrument(self, increment):
        self.curr_instrument += increment
        if self.curr_instrument >= len(self.client.chain_channels):
            self.curr_instrument = 0
        if self.curr_instrument < 0:
            self.curr_instrument = len(self.client.chain_channels) - 1
        msg=liblo.Message('/CUIA/LAYER_CONTROL', self.client.chain_channels[self.curr_instrument] + 1)
        liblo.send(self.addr, msg)

    def send_control_change(self, control_name, value):
        zyn_control_name = control_mapping.get(self.get_current_instrument_name(), {}).get(control_name)
        if not zyn_control_name:
            self.logger.warning("no control mapping found for control_name '%s' for engine %s" % control_name, self.get_current_instrument_name())
            return
        try:
            cc = self.client.chain_controls[2][zyn_control_name]["cc"]
        except Exception as e:
            self.logger.error("Failed to map control '%s' to zynthian control '%s'" % (control_name, zyn_control_name))
            return
        self.midiout.send_message([0xB0, cc, value])

    def get_current_instrument_channel(self):
        return self.client.chain_channels[self.curr_instrument]
    
    def get_current_instrument_name(self):
        curr_instrument_channel = self.get_current_instrument_channel()
        chain_name = self.client.chain_engines[curr_instrument_channel]
        chain_name = chain_name.decode("UTF-8")
        return PRETTY_LOOKUP.get(chain_name, chain_name)
        
    def log_wrapper(self, message, discard):
        self.logger.warning(message)
        
    def poll_until_ready(self):
        while not self.client.populated['HANDSHAKE'] or \
              not self.client.populated['QUERY_NUM_CHAINS'] or \
              not self.client.populated['QUERY_CHAIN_CHANNELS'] or \
              not self.client.populated['QUERY_CHAIN_ENGINES'] or \
              not self.client.populated['QUERY_CHAIN_CONTROLS_ALL']:
            self.client.send_HANDSHAKE()
            self.client.send_QUERY_NUM_CHAINS()
            self.client.send_QUERY_CHAIN_CHANNELS()
            self.client.send_QUERY_CHAIN_ENGINES()
            if self.client.populated['QUERY_CHAIN_CHANNELS']:
                for channel in self.client.chain_channels:
                    self.client.send_QUERY_CHAIN_CONTROLS(channel)
            time.sleep(0.1)
        self.client.close()
        # now we're ready, do ready.
        self.ready()

    def ready(self):
        print('looks like we are ready...')
        self.hardware.connect()
        
    def disconnect(self):
        self.hardware.disconnect()
        
controller = ZynMCUController()    
controller.poll_until_ready()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("")
finally:
    controller.disconnect()
    print("Exiting...")
    sys.exit()

