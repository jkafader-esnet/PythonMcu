from PythonMcu.Hardware import NektarPanoramaTSeries
from PythonMcu.configuration.patches import control_mapping
from PythonMcu.configuration.midi_states import MIDI_CONNECTING, MIDI_DISCONNECTING, MIDI_DISCONNECTED, MIDI_CONNECTED
import liblo

import sys
import rtmidi
from rtmidi.midiutil import open_midiinput
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

UNRESOLVED = 0
PART_RESOLVED = 1
ALL_RESOLVED = 2

COMMAND_REVERSE = { v: k for k, v in COMMANDS.items() }

logger = logging.getLogger("MCU Controller")
logging.basicConfig(level=logging.DEBUG)

class TimeoutException(Exception):
    pass

class APIClient(object):
    def __init__(self):
        # states for state machine control
        self.query_state = UNRESOLVED
        self.midi_state = MIDI_DISCONNECTED

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
        self.logger = logger

    def midi_connect(self):
        self.midi_state = MIDI_CONNECTING
        self.midiout = rtmidi.MidiOut()
        self.port_list = self.midiout.get_ports()
        self.logger.info("Available ports: %s", self.port_list)
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
        self.logger.info("connected to port %s", self.port_name)
        self.midi_state = MIDI_CONNECTED

    def midi_disconnect(self):
        if self.midi_state == MIDI_DISCONNECTED:
            return
        self.midi_state = MIDI_DISCONNECTING
        self.midiin.close_port()
        self.midiout.close_port()
        del self.midiin
        del self.midiout
        self.midi_state = MIDI_DISCONNECTED

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
        if self.txn_id > 127:
            self.txn_id = 0
        self.seq_id += 1
        if self.seq_id > 127:
            self.seq_id = 0

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

    def wait_on(self, command, timeout=1):
        total = 0
        wait = 0.005
        while not self.populated[command] and total < timeout:
            total += wait
            time.sleep(wait)
        if total >= timeout:
            raise TimeoutException("query %s timed out")

    def wait_on_item(self, command, timeout=1, item=None):
        total = 0
        wait = 0.005
        while item not in self.populated[command] and total < timeout:
            total += wait
            time.sleep(wait)
        if total >= timeout:
            raise TimeoutException("query %s timed out")

    def send_HANDSHAKE(self):
        command = COMMANDS['HANDSHAKE']
        self.send([command, self.client_id, self.txn_id, self.seq_id])

    def receive_HANDSHAKE(self, message):
        self.logger.debug("receive_HANDSHAKE %s", message)
        self.populated['HANDSHAKE'] = True

    def do_HANDSHAKE(self):
        self.send_HANDSHAKE()
        self.wait_on('HANDSHAKE')
        return self.populated['HANDSHAKE']

    def send_QUERY_NUM_CHAINS(self):
        command = COMMANDS['QUERY_NUM_CHAINS']
        self.send([command, self.client_id, self.txn_id, self.seq_id])

    def receive_QUERY_NUM_CHAINS(self, message):
        self.logger.warning("receive_QUERY_NUM_CHAINS %s", message)
        self.count_chains = message[4]
        self.logger.debug("there are currently %s total root chains" % self.count_chains)
        if self.count_chains:
            self.populated['QUERY_NUM_CHAINS'] = True

    def do_QUERY_NUM_CHAINS(self):
        self.send_QUERY_NUM_CHAINS()
        self.wait_on('QUERY_NUM_CHAINS')
        return self.count_chains

    def send_QUERY_CHAIN_CONTROLS(self, channel):
        command = COMMANDS['QUERY_CHAIN_CONTROLS']
        self.send([command, self.client_id, self.txn_id, self.seq_id, channel])

    def receive_QUERY_CHAIN_CONTROLS(self, message):
        self.logger.debug("receive_QUERY_CHAIN_CONTROLS %s", message)
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
        self.logger.info("chain controls %s" % self.chain_controls.keys())
        if self.chain_controls[chain_channel]:
            curr_val = self.populated.get('QUERY_CHAIN_CONTROLS', [])
            curr_val.append(chain_channel)
            self.populated['QUERY_CHAIN_CONTROLS'] = curr_val
            if self.populated['QUERY_CHAIN_CHANNELS']:
                if sorted(list(self.chain_controls.keys())) == sorted(self.chain_channels):
                    self.populated['QUERY_CHAIN_CONTROLS_ALL'] = True

    def do_QUERY_CHAIN_CONTROLS(self, channel):
        self.send_QUERY_CHAIN_CONTROLS(channel)
        self.wait_on_item("QUERY_CHAIN_CONTROLS", item=channel)
        return self.chain_controls[channel]

    def do_QUERY_CHAIN_CONTROLS_ALL(self):
        if self.populated['QUERY_CHAIN_CHANNELS']:
            for channel in self.chain_channels:
                self.do_QUERY_CHAIN_CONTROLS(channel)

    def send_QUERY_CHAIN_CHANNELS(self):
        command = COMMANDS['QUERY_CHAIN_CHANNELS']
        self.send([command, self.client_id, self.txn_id, self.seq_id])

    def receive_QUERY_CHAIN_CHANNELS(self, message):
        self.logger.debug("receive_QUERY_CHAIN_CHANNELS %s", message)
        self.chain_channels = message[4:]
        print("chains are on channels %s" % self.chain_channels)
        if self.chain_channels:
            self.populated['QUERY_CHAIN_CHANNELS'] = True

    def do_QUERY_CHAIN_CHANNELS(self):
        self.send_QUERY_CHAIN_CHANNELS()
        self.wait_on("QUERY_CHAIN_CHANNELS")
        return self.chain_channels

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
        self.logger.debug("receive_QUERY_CHAIN_ENGINES: %s", message)
        self.chain_engines = self.bytes_to_dict(message[4:])
        self.logger.info("chain engines: %s" % self.chain_engines)
        if self.chain_engines:
            self.populated['QUERY_CHAIN_ENGINES'] = True

    def do_QUERY_CHAIN_ENGINES(self):
        self.send_QUERY_CHAIN_ENGINES()
        self.wait_on("QUERY_CHAIN_ENGINES")
        return self.chain_engines
            
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
        self.logger = logger
        logging.basicConfig(level=logging.DEBUG)

        patch = 'Pianoteq'
        self.client = None
        
        self.addr=liblo.Address('osc.udp://localhost:1370')
        self.curr_instrument = 0

        self.midiout = rtmidi.MidiOut()
        self.port_list = self.midiout.get_ports()
        self.logger.info("Available ports: %s", self.port_list)
        self.port_num = None
        for i in range(len(self.port_list)):
            port = self.port_list[i]
            if "Midi Through Port" in port:
                self.port_num = i
                break
        if self.port_num is None:
            sys.exit("couldn't find appropriate port")
        self.midiout.open_port(self.port_num)
        self.hardware = NektarPanoramaTSeries("PANORAMA T6 Mixer", patch, controller=self)

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
            self.logger.warning("no control mapping found for control_name '%s' for engine %s" % (control_name, self.get_current_instrument_name()))
            return
        try:
            cc = self.client.chain_controls[self.get_current_instrument_channel()][zyn_control_name]["cc"]
        except Exception as e:
            self.logger.error("Failed to map control '%s' to zynthian control '%s', Exception: %s %s" % (control_name, zyn_control_name, type(e).__name__, e))
            return
        self.midiout.send_message([0xB1, cc, value]) # currently, always channel 2. Channel 1 is ignored by configuration

    def send_midi_panic(self):
        self.send_midi([0xBF, 0x78, 0x00])
        self.send_midi([0xBF, 0x7B, 0x00])

    def get_current_instrument_channel(self):
        return self.client.chain_channels[self.curr_instrument]
    
    def get_current_instrument_name(self):
        curr_instrument_channel = self.get_current_instrument_channel()
        chain_name = self.client.chain_engines[curr_instrument_channel]
        chain_name = chain_name.decode("UTF-8")
        return PRETTY_LOOKUP.get(chain_name, chain_name)

    def get_mapped_instrument_controls(self):
        if not self.client:
            return {}
        curr_inst = 'Pianoteq'
        curr_chan = 0
        zyn_controls = {}
        if self.client.populated['QUERY_CHAIN_CONTROLS_ALL']:
            curr_inst = self.get_current_instrument_name()
            curr_chan = self.get_current_instrument_channel()
            zyn_controls = self.client.chain_controls[curr_chan]
        output = {}
        for local_control, zyn_control in control_mapping.get(curr_inst, {}).items():
            output[local_control] = zyn_controls.get(zyn_control, {"cc": None, "min": 0, "max": 0, "cur": 0 })
        return output

    def run_forever(self):
        client_methods = [
            'do_HANDSHAKE',
            'do_QUERY_NUM_CHAINS',
            'do_QUERY_CHAIN_CHANNELS',
            'do_QUERY_CHAIN_ENGINES',
            'do_QUERY_CHAIN_CONTROLS_ALL',
        ]
        client_queries_to_resolve = [
            'HANDSHAKE',
            'QUERY_NUM_CHAINS',
            'QUERY_CHAIN_CHANNELS',
            'QUERY_CHAIN_ENGINES',
            'QUERY_CHAIN_CONTROLS_ALL',
        ]
        try:
            while True:
                if self.hardware.midi_state == MIDI_DISCONNECTED:
                    self.logger.info("Our hardware is not connected. Doing MIDI connect...")
                    self.hardware.midi_connect()
                if self.hardware.midi_state == MIDI_CONNECTED:
                    self.logger.info("Our hardware is not MCU connected. Doing MCU connect...")
                    self.hardware.mcu_connect()
                if not self.client:
                    self.client = APIClient()
                if not self.client.query_state == ALL_RESOLVED:
                    if self.client.midi_state == MIDI_DISCONNECTED:
                        self.logger.info("Our client is not resolved and not connected. Doing MIDI connect...")
                        self.client.midi_connect()
                    if self.client.midi_state == MIDI_CONNECTED:
                        self.logger.info("Our client is connected but not resolved. Doing queries...")
                        if all([self.client.populated.get(key) for key in client_queries_to_resolve]):
                            self.logger.info("All queries appear to be resolved...")
                            self.client.query_state = ALL_RESOLVED
                        for method in client_methods:
                            self.logger.info("Doing %s...", method)
                            getattr(self.client, method)()
                if self.client.query_state == ALL_RESOLVED:
                    if self.client.midi_state != MIDI_DISCONNECTED:
                        self.logger.info("Our client is fully resolved. Closing MIDI connection...")
                        self.client.midi_disconnect() # don't tie up the connection
                time.sleep(0.5)
                self.logger.debug('looping...')
        except KeyboardInterrupt:
            print("Interrupted!")
        except Exception as e:
            print("%s %s" % (type(e).__name__, e))
            raise e
        finally:
            print("Exiting...")
            try:
                self.hardware.disconnect()
            finally:
                sys.exit()

controller = ZynMCUController()
controller.run_forever()
