# -*- coding: utf-8 -*-

"""
PythonMcu
=========
Mackie Host Controller written in Python
Copyright (c) 2011 Martin Zuther (http://www.mzuther.de/)
Copyright (c) 2021 Raphaël Doursenaud <rdoursenaud@free.fr>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Thank you for using free software!

"""
import time
import os
import sys

if __name__ == "__main__":
    # allow "PythonMcu" package imports when executing this module
    sys.path.append('../../../')

from PythonMcu.Hardware.MidiControllerTemplate import MidiControllerTemplate
#from PythonMcu.Midi.MidiConnection import MidiConnection
import rtmidi
from rtmidi.midiutil import open_midiinput


class NektarPanoramaTSeries(MidiControllerTemplate):
    FORMATTED_NAME = "Nektar Panorama T4/T6"

    # Nektar Technology Inc -- lookup here: https://www.midi.org/specifications/midi-reference-tables/manufacturer-sysex-id-numbers
    MIDI_MANUFACTURER_ID = [0x00, 0x01, 0x77]

    # MIDI device ID and initialisation of Novation ZeRO SL Mkii
    MIDI_DEVICE_ID = [0x03, 0x03, 0x12, 0x00, 0x04, 0x00]

    # MIDI channel of controller
    _MIDI_DEVICE_CHANNEL = 0

    _MIDI_CC_CLEAR_ALL_LEDS = 0x4E
    _MIDI_CC_ENCODER_LIGHTS = 0x70
    _MIDI_CC_ENCODER_MODE = 0x78
    _MIDI_CC_CONTROLLER_ROW_LIGHTS_LEFT = (0x51, 0x53, 0x54, 0x50, 0x52)
    _MIDI_CC_CONTROLLER_ROW_LIGHTS_RIGHT = (0x55, 0x56, 0x57)

    _MIDI_CC_BUTTONS_LEFT_TOP = 0x18
    _MIDI_CC_BUTTONS_LEFT_BOTTOM = 0x20
    _MIDI_CC_BUTTONS_RIGHT_TOP = 0x28
    _MIDI_CC_BUTTONS_RIGHT_BOTTOM = 0x30

    _MIDI_CC_FADERS = 0x10
    _MIDI_CC_ENCODERS = 0x38
    _MIDI_CC_KNOBS = 0x08
    _MIDI_CC_CONTROL_PEDAL = 0x40

    _MIDI_CC_BUTTON_BANK_UP = 0x58
    _MIDI_CC_BUTTON_BANK_DOWN = 0x59
    _MIDI_CC_BUTTON_REWIND = 0x48
    _MIDI_CC_BUTTON_FAST_FORWARD = 0x49
    _MIDI_CC_BUTTON_STOP = 0x4A
    _MIDI_CC_BUTTON_PLAY = 0x4B
    _MIDI_CC_BUTTON_RECORD = 0x4C
    _MIDI_CC_BUTTON_CYCLE = 0x4D
    _MIDI_CC_BUTTON_MODE_TRANSPORT = 0x4F

    _MIDI_CC_LED_AUTOMAP_LEARN = 0x48
    _MIDI_CC_LED_AUTOMAP_VIEW = 0x49
    _MIDI_CC_LED_AUTOMAP_USER = 0x4A
    _MIDI_CC_LED_AUTOMAP_FX = 0x4B
    _MIDI_CC_LED_AUTOMAP_MIXER = 0x4D

    _MODE_TRACK_OFF = 0
    _MODE_TRACK_MUTE_SOLO = 1
    _MODE_TRACK_RECORD_READY_FUNCTION = 2

    _MODE_EDIT_OFF = 0
    _MODE_EDIT_VSELECT_ASSIGNMENT = 1
    _MODE_EDIT_VSELECT_SELECT = 2

    _MODE_OTHER_OFF = 0
    _MODE_OTHER_TRANSPORT = 1
    _MODE_OTHER_BANK = 2
    _MODE_OTHER_AUTOMATION = 3
    _MODE_OTHER_GLOBAL_VIEW = 4
    _MODE_OTHER_UTILITY = 5

    def __init__(self, midi_input, midi_output, callback_log, patch, controller):
        super().__init__(midi_input, midi_output, callback_log)
        self.callback_log = callback_log
        self.controller = controller
        self.active_track = 1
        self.mode = "mixer"
        self.controls = {
            0: {"name": "Fader 1", "set": self.set_track_volume(0) },
            1: {"name": "Fader 2", "set": self.set_track_volume(1) },
            2: {"name": "Fader 3", "set": self.set_track_volume(2) },
            3: {"name": "Fader 4", "set": self.set_track_volume(3) },
            4: {"name": "Fader 5", "set": self.set_track_volume(4) },
            5: {"name": "Fader 6", "set": self.set_track_volume(5) },
            6: {"name": "Fader 7", "set": self.set_track_volume(6) },
            7: {"name": "Fader 8", "set": self.set_track_volume(7) },

            48: {"name": "Rotary 1", "set": self.set_rotary_value(0) },
            49: {"name": "Rotary 2", "set": self.set_rotary_value(1) },
            50: {"name": "Rotary 3", "set": self.set_rotary_value(2) },
            51: {"name": "Rotary 4", "set": self.set_rotary_value(3) },
            52: {"name": "Rotary 5", "set": self.set_rotary_value(4) },
            53: {"name": "Rotary 6", "set": self.set_rotary_value(5) },
            54: {"name": "Rotary 7", "set": self.set_rotary_value(6) },
            55: {"name": "Rotary 8", "set": self.set_rotary_value(7) },

            16: { "name": "Track 1 Button", "set": self.toggle_function(1) },
            17: { "name": "Track 2 Button", "set": self.toggle_function(2) },
            18: { "name": "Track 3 Button", "set": self.toggle_function(3) },
            19: { "name": "Track 4 Button", "set": self.toggle_function(4) },
            20: { "name": "Track 5 Button", "set": self.toggle_function(5) },
            21: { "name": "Track 6 Button", "set": self.toggle_function(6) },
            22: { "name": "Track 7 Button", "set": self.toggle_function(7) },
            23: { "name": "Track 8 Button", "set": self.toggle_function(8) },

            94: { "name": "Track Master Button", "set": self.panic },
            96: { "name": "Shift", "set": self.shift_mode },

            80: { "name": "Transport: Loop", "set": self.unmapped },
            81: { "name": "Transport: Reverse", "set": self.unmapped },
            82: { "name": "Transport: Forward", "set": self.unmapped },
            83: { "name": "Transport: Stop", "set": self.unmapped },
            84: { "name": "Transport: Play", "set": self.unmapped },
            85: { "name": "Transport: Record", "set": self.unmapped },

            91: {"name": "Track-",      "set": self.change_instrument(direction=-1) },
            92: {"name": "Track+",      "set": self.change_instrument(direction=1) },
            94: {"name": "Browser",     "set": self.patch_list },
            95: {"name": "View",        "set": self.toggle_view },
            99:  {"name": "Mixer",      "set": self.display_settings_page("Instrument 1") },
            100: {"name": "Instrument", "set": self.display_settings_page("Instrument 2") },
            101: {"name": "Multi",      "set": self.display_settings_page("Routing/Effects")},
            101: {"name": "Internal",   "set": self.display_settings_page("Routing/Effects")},
        }
        patches ={
            "moog": {
                "F0": {"name": "Osc1 Octave",      "group": "OSC",     "set": self.vtrack_setter(0),  "value": 91 },
                "F1": {"name": "Osc1 Shape",       "group": "OSC",     "set": self.vtrack_setter(1),  "value": 91 },
                "F2": {"name": "Osc2 Octave",      "group": "OSC",     "set": self.vtrack_setter(2),  "value": 91 },
                "F3": {"name": "Osc2 Fine",        "group": "OSC",     "set": self.vtrack_setter(3),  "value": 91 },
                "F4": {"name": "Osc2 Shape",       "group": "OSC",     "set": self.vtrack_setter(4),  "value": 91 },
                "F5": {"name": "Osc3 Octave",      "group": "OSC",     "set": self.vtrack_setter(5),  "value": 91 },
                "F6": {"name": "Osc3 Fine",        "group": "OSC",     "set": self.vtrack_setter(6),  "value": 91 },
                "F7": {"name": "Osc3 Shape",       "group": "OSC",     "set": self.vtrack_setter(7),  "value": 91 },
                "F8": {"name": "VCA  Attack",      "group": "ENV",     "set": self.vtrack_setter(8),  "value": 91 },
                "F9": {"name": "VCA  Decay",       "group": "ENV",     "set": self.vtrack_setter(9),  "value": 91 },
                "F10": {"name": "VCA  Sustain",    "group": "ENV",     "set": self.vtrack_setter(10), "value": 91 },
                "F11": {"name": "VCA  Release",    "group": "ENV",     "set": self.vtrack_setter(11), "value": 91 },
                "F12": {"name": "VCF  Attack",     "group": "ENV",     "set": self.vtrack_setter(12), "value": 91 },
                "F13": {"name": "VCF  Decay",      "group": "ENV",     "set": self.vtrack_setter(13), "value": 91 },
                "F14": {"name": "VCF  Sustain",    "group": "ENV",     "set": self.vtrack_setter(14), "value": 91 },
                "F15": {"name": "VCF  Release",    "group": "ENV",     "set": self.vtrack_setter(15), "value": 91 },
                "P0": {"name": "Cutoff",           "group": "FLT/MIX", "set": self.vpot_setter(0),    "value": 64 },
                "P1": {"name": "Resonance",        "group": "FLT/MIX", "set": self.vpot_setter(1),    "value": 64 },
                "P2": {"name": "Env Amount",       "group": "FLT/MIX", "set": self.vpot_setter(2),    "value": 64 },
                "P3": {"name": "Portamento",       "group": "FLT/MIX", "set": self.vpot_setter(3),    "value": 64 },
                "P4": {"name": "Noise Level",      "group": "FLT/MIX", "set": self.vpot_setter(4),    "value": 64 },
                "P5": {"name": "Osc1 Level",       "group": "FLT/MIX", "set": self.vpot_setter(5),    "value": 64 },
                "P6": {"name": "Osc2 Level",       "group": "FLT/MIX", "set": self.vpot_setter(6),    "value": 64 },
                "P7": {"name": "Osc3 Lvl/Mod Amt", "group": "FLT/MIX", "set": self.vpot_setter(7),    "value": 64 },
                "B0": {"name": "Oscillator Mod",   "group": "BUTTONS", "set": self.vbutton_setter(0), "value": 0 },
                "B1": {"name": "Filter Mod",       "group": "BUTTONS", "set": self.vbutton_setter(1), "value": 0 },
                "B2": {"name": "Keyboard->Osc1",   "group": "BUTTONS", "set": self.vbutton_setter(2), "value": 127 },
                "B3": {"name": "Keyboard->Osc2",   "group": "BUTTONS", "set": self.vbutton_setter(3), "value": 127 },
                "B4": {"name": "Keyboard->Osc3",   "group": "BUTTONS", "set": self.vbutton_setter(4), "value": 0 },
                "B5": {"name": "Noise Color",      "group": "BUTTONS", "set": self.vbutton_setter(5), "value": 0 },
                "B6": {"name": "A-440 Sync",       "group": "BUTTONS", "set": self.vbutton_setter(6), "value": 127 },
                "B7": {"name": "Main Output",      "group": "BUTTONS", "set": self.vbutton_setter(7), "value": 127 },
            },
            "ob-xd": {
                "OSC/FLT": {},
                "MOD": {},
                "FLT": {},
            },
            "hammond": {
                0: {"name": "Draw [16']",     "set": self.vtrack_setter(0, invert=True), "value": 91 },
                1: {"name": "Draw [5  1/3']", "set": self.vtrack_setter(1, invert=True), "value": 91 },
                2: {"name": "Draw [8']",      "set": self.vtrack_setter(2, invert=True), "value": 91 },
                3: {"name": "Draw [4']",      "set": self.vtrack_setter(3, invert=True), "value": 91 },
                4: {"name": "Draw [2  2/3']", "set": self.vtrack_setter(4, invert=True), "value": 91 },
                5: {"name": "Draw [2']",      "set": self.vtrack_setter(5, invert=True), "value": 91 },
                6: {"name": "Draw [1  3/5']", "set": self.vtrack_setter(6, invert=True), "value": 91 },
                7: {"name": "Draw [1  1/3']", "set": self.vtrack_setter(7, invert=True), "value": 91 },
            }
        } 
        self.faders = { name: fader for name, fader in patches[patch].items() if name.startswith("F") }
        self.rotaries = { name: rotary for name, rotary in patches[patch].items() if name.startswith("P") }
        self.buttons = { name: button for name, button in patches[patch].items() if name.startswith("B") }

        self.display_lcd_available = True
        self.automated_faders_available = False
        self.display_7seg_available = False
        self.display_timecode_available = False
        self.meter_bridge_available = False

        self._lcd_strings = ['', '']

        self._vpot_modes = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self._vpot_positions = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

        self._mode_track = self._MODE_TRACK_MUTE_SOLO
        self._mode_edit = self._MODE_EDIT_OFF
        self._mode_other = self._MODE_OTHER_OFF
        self._mode_automap = False

        self._is_connected = False
        self.standard_syx_header = [0xF0, 0x00, 0x01, 0x77, 0x7F, 0x01]

        self.midiout = rtmidi.MidiOut()
        self.port_list = self.midiout.get_ports()
        callback_log("Available ports: %s" % self.port_list, '')
        self.port_num = None
        for i in range(len(self.port_list)):
            port = self.port_list[i]
            if midi_output in port:
                self.port_num = i
                break
        print("the port number is %s" % self.port_num)
        if self.port_num is None:
            sys.exit("couldn't find appropriate port")
        self.midiout.open_port(self.port_num)

        self.midiin, self.port_name = open_midiinput(self.port_num)
        self.midiin.ignore_types(sysex=False)
        self.midiin.set_callback(self.receive_midi)

        for i in range(len(self.port_list)):
            port = self.port_list[i]
            if "PANORAMA T6 Internal" in port:
                notes_port_num = i
                break
        print("intternal port: #%s" % notes_port_num)
        self.notesin, self.notesin_port = open_midiinput(notes_port_num)
        self.notesin.set_callback(self.receive_midi)
        # original version. Commented with import above for reference.
        #self.midi = MidiConnection(callback_log, self.receive_midi)

    def toggle_function(self, num):
        pass

    def panic(self):
        pass

    def send_midi(self, message):
        self.callback_log("SEND: "+" ".join([hex(c).replace("0x", "").upper().zfill(2) for c in message]), "")
        self.midiout.send_message(message)
        time.sleep(0.005)
        
    def shift_mode(self, bool):
        if bool:
            self.pan_mode()
            self.set_display_area("focus_name", ["You Pressed"])
            self.set_display_area("focus_value", ["Shift!"])
            self.set_display_area("menu_name", ["OHHH", "DAMN!"])
            self.set_display_area("pan_names_1-4", ["A", "B", "C", "D",])
            self.set_display_area("pan_names_5-8", ["D", "E", "F", "G",])
            self.set_display_area("pan_values_1-4", ["A", "B", "C", "D",])
            self.set_display_area("pan_values_5-8", ["D", "E", "F", "G",])
            self.set_display_area("soft_buttons", ["OH", "NO", "YOU", "DIDN'T"])
        else:
            self.mixer_mode()
            self.set_display_area("focus_name", ["You Released"])
            self.set_display_area("focus_value", ["Shift!"])
            self.set_track_names([track['name'] for num, track in self.faders.items()])
            self.set_button_labels(['SOUND1', 'SOUND2', '', 'FX', ''])
            for key, track in self.faders.items():
                track['set'](track['value'], invert=False) # never invert the last value...


    def unmapped(self, *args, **kwargs):
        pass

    def patch_list(self, *args, **kwargs):
        pass

    def toggle_view(self, *args, **kwargs):
        pass

    def display_settings_page(self, *args, **kwargs):
        def func(*args, **kwargs):
            pass
        return func

    def set_rotary_value(self, track_number):
        def set(value):
            self.rotaries["P%s" % track_number]["set"](value)
        return set

    def set_track_volume(self, track_number):
        def set(value):
            self.faders["F%s" % track_number]["set"](value)
        return set

    def set_vtrack_value(self, fader_number, value):
        self.send_midi([0xB0, fader_number, value])
        #self.midi.send(0xB0, fader_number, value)

    def vtrack_setter(self, track_number, invert=False):
        def set(value, invert=invert):
            if invert:
                value = 127 - value
            self.faders["F%s" % track_number]["value"] = value
            self.set_vtrack_value(track_number, value)
        return set

    def set_vpot_value(self, track_number, value):
        offset = 48 # first pot control number
        self.send_midi([0xB0, offset + track_number, value])
    
    def vpot_setter(self, track_number, invert=False):
        def set(value, invert=invert):
            if value == 127:
                if invert:
                    value = -1
                else:
                    value = 1
            if value == 0:
                if invert:
                    value = 1
                else:
                    value = -1
            self.rotaries["F%s" % track_number]["value"] += value
            self.set_vpot_value(track_number, value)
        return set

    def set_vbutton_value(self, track_number, value):
        offset = 48 # first pot control number
        self.send_midi([0xB0, offset + track_number, value])
    
    def vbutton_setter(self, track_number, invert=False):
        def set(value, invert=invert):
            if invert:
                value = 0 if value == 127 else 127
            self.buttons["B%s" % track_number]["value"] = value
            self.set_vbutton_value(track_number, value)
        return set

    @staticmethod
    def get_usage_hint():
        return 'Connect the controller\'s USB port to your computer ' + \
               'and switch to preset #32 (Ableton Live Automap).'

    def _log(self, message, repaint=False):
        self.callback_log('[Nektar Panorama T6]  ' + message, repaint)

    def mixer_mode(self):
        self.mode = "mixer"
        data = [0x06, 0x02, 0x7F, 0x00, 0x00]
        self.send_midi(self.standard_syx_header + data + [0xF7])
        # wait a while. Don't overload buffer.
        #time.sleep(0.1)

        #return self.midi.send_sysex(self.standard_syx_header, data)

    def pan_mode(self):
        self.mode = "pan"
        data = [0x06, 0x10, 0x7F, 0x00, 0x00]
        return self.send_midi(self.standard_syx_header + data + [0xF7])
        #return self.midi.send_sysex(self.standard_syx_header, data)

    def initialize_controls(self):
        #F0 00 01 77 7F 01 09 06 00 00 01 36 39 F7
        #F0 00 01 77 7F 01 09 06 00 00 01 36 39 F7
        data = [0x09, 0x06, 0x00, 0x00, 0x01, 0x36, 0x39]
        self.send_midi(self.standard_syx_header + data + [0xF7])
        #time.sleep(0.1)
        #self.midi.send_sysex(self.standard_syx_header + header, data)
        # B0 63 7F
        # B0 63 7F
        self.send_midi([0xB0, 0x63, 0x7F])
        # F0 00 01 77 7F 01                      F7 (header)
        # F0 00 01 77 7F 01 0D 04 00 00 01 00 6D F7
        data = [0x0D, 0x04, 0x00, 0x00, 0x01, 0x00, 0x6D]
        self.send_midi(self.standard_syx_header + data + [0xF7])
        #self.midi.send_sysex(self.standard_syx_header, data)
        # F0 00 01 77 7F 01                F7 (header)
        # F0 00 01 77 7F 01 06 02 7F 00 00 F7
        self.mixer_mode()
        # B0 00 00

        group_1 = [i for i in range(0x00, 0x08)]
        group_2 = [i for i in range(0x30, 0x38)]
        group_3 = [i for i in range(0x10, 0x18)]
        group_4 = [i for i in range(0x38, 0x40)]
        faders = group_1 + group_2 + [0x6A,] + group_3 + group_4 

        for fader in faders:
            self.set_vtrack_value(fader, 0x00)
        # F0 00 01 77 7F 01                                  F7 (header)
        # F0 00 01 77 7F 01 06 00 01 01 00 00 02 00 00 03 00 F7
        self.set_display_area("unknown", ["", "", ""])

        # B0 19 01
        self.set_vtrack_value(0x19, 0x01)
        # F0 00 01 77 7F 01                      F7 (header)
        # F0 00 01 77 7F 01 0D 01 00 00 01 01 6F F7
        data = [0x0D, 0x01, 0x00, 0x00, 0x01, 0x01, 0x6F]
        self.send_midi(self.standard_syx_header + data + [0xF7])
        #self.midi.send_sysex(self.standard_syx_header, data)
        # F0 00 01 77 7F 01                F7 (header)
        # F0 00 01 77 7F 01 06 02 7F 00 00 F7
        self.mixer_mode()

        faders = group_1 + group_2 + [0x08] + group_3 + group_4
        for fader in faders:
            self.set_vtrack_value(fader, 0x00)
        # B0 19 01
        self.set_vtrack_value(0x19, 0x01)
        # we are fully in "MCU mode" at this point
        # so what does this do? color for something? lights? selection?
        # F0 00 01 77 7F 01                      F7 (header)
        # F0 00 01 77 7F 01 0F 06 01 01 01 00 67 F7
        data = [0x0F, 0x06, 0x01, 0x01, 0x01, 0x00, 0x67]
        self.send_midi(self.standard_syx_header + data + [0xF7])
        #self.midi.send_sysex(self.standard_syx_header, data)
        # F0 00 01 77 7F 01                                  F7 (header)
        # F0 00 01 77 7F 01 06 00 01 01 00 00 02 00 00 03 00 F7
        self.set_display_area('unknown', ['', '', ''])

        self.set_track_names([track['name'] for num, track in self.faders.items()])
        self.set_button_labels(['SOUND1', 'SOUND2', '', 'FX', ''])
        for key, track in self.faders.items():
            track['set'](track['value'])

        self.set_active_track(1)

        inst_name = self.controller.get_current_instrument_name()
        self.set_display_area("focus_name", ["Instrument:"])
        self.set_display_area("focus_value", [inst_name.decode("UTF-8")])


    def printable_hex(self, header, message):
        return (" ".join([hex(b).replace("0x", '').zfill(2) for b in self.compose_full_message(header+message)])).upper()

    def compose_full_message(self, message):
        return bytes([0xF0]) + bytes(message) + bytes([0xF7])

    def format_string_array(self, strings, offset=0x00):
        output = b''
        for i in range(0, len(strings)):
            output += bytes([offset + i+1])
            string = strings[i]
            output += self.format_string(string)
        if output[-1] == 0:
            return output[:-1]
        return output

    def format_string(self, string):
        output = string.encode("ascii")
        output = bytes([len(output)]) + output + bytes([0])
        return output

    def set_display_area(self, area, data):
        areas = { 
            "unknown": { 
                "header": bytes([ 0x06, 0x00, 0x01 ]), 
                "data_length": 3,
                "offset": 0x00,
            },
            "focus_name": { 
                "header": bytes([ 0x06, 0x00, 0x02 ]), 
                "data_length": 1,
                "offset": 0x00,
            },
            "focus_value": {
                "header": bytes([ 0x06, 0x00, 0x03 ]),
                "data_length": 1,
                "offset": 0x00,
            },
            "soft_buttons": {
                "header": bytes([ 0x06, 0x00, 0x04, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01, 0x00, ]),
                "data_length": 4,
                "offset": 0x00,
                "format": lambda l, offset: self.format_string_array([l[0], l[1], l[2], l[3], ""], offset=offset)
            }, # 4 strings (weird header)
            "menu_name": {
                "header": bytes([ 0x06, 0x00, 0x05]),
                "data_length": 2,
                "format": lambda l, offset: self.format_string_array([l[0], '', l[1]], offset=offset),
                "offset": 0x00,
            }, # 2 strings (second empty! second (third written) ignored in track mode)
            "track_names_1-4": {
                "header": bytes([0x06, 0x00, 0x06]),
                "data_length": 4,
                "offset": 0x08
            }, # 4 strings per group, sent twice.
            "track_names_5-8": {
                "header": bytes([0x06, 0x00, 0x06]),
                "data_length": 4,
                "offset": 0x0C
            }, # 4 strings per group, sent twice.
            "pan_names_1-4": {
                "header": bytes([0x06, 0x00, 0x06]),
                "data_length": 4,
                "offset": 0x00
            }, # 4 strings per group, sent twice.
            "pan_names_5-8": {
                "header": bytes([0x06, 0x00, 0x06]),
                "data_length": 4,
                "offset": 0x04
            }, # 4 strings per group, sent twice.
            "pan_values_1-4": {
                "header": bytes([0x06, 0x00, 0x07]),
                "data_length": 4,
                "offset": 0x00
            },
            "pan_values_5-8": {
                "header": bytes([0x06, 0x00, 0x07]),
                "data_length": 4,
                "offset": 0x04
            }
        }
        if area not in areas:
            raise Exception("Display area %s not found" % area)
        data_length = areas[area]['data_length']
        if len(data) != data_length:
            raise Exception("Wrong string count for area %s. You provided %s strings but %s are required")
        formatter = areas[area].get('format', self.format_string_array)
        header = areas[area]['header']
        offset = areas[area]['offset']
        message = header + formatter(data, offset=offset)
        return self.send_midi(self.standard_syx_header + [c for c in message] + [0xF7])


    # def sysex_layers(self):
    #     more_syx_header = [0x06, 0x00]
    #     layers = [
    #         0x01, # unknown. Has 3 parts: 01 00 00, 02 00 00, 03 00 F7
    #         #                                        len data                       term
    #         0x02, # Top Menu Name. Has 1 part:    01  09 46 49 52 53 54 20 56 6F 6C F7
    #         #                                        len data           term
    #         0x03, # Top Menu Value. Has 1 part:   01  05 2B 31 32 2E 30 F7
    #         0x04, # Soft button names. Has 4 parts: 1: 04 00 2: 04 00 00 00 3: 01 00 4: 01 (then strings)
    #         0x05, # Second Block (black area) Values. Has 4 parts: 1: 05 01  01 (string) 02 00 00 (empty string) 03 (string)
    #         0x06, # Track names 1. Has 4 parts: 1: 01 (string) 02 (string) 03 (string) 04 (string)
    #         0x06, # Track names 2. Has 4 parts: 1: 05 (string) 06 (string) 07 (string) 08 (string)
    #         0x07, # pan values 1. Has 4 parts: 1: 01 (string) 02 (string) 03 (string) 04 (string)
    #         0x07, # pan values 2. Has 4 parts: 1: 05 (string) 06 (string) 07 (string) 08 (string)
    #     ]

    #     for layer in layers:
    #         message = layer
    #         self.send_midi(self.standard_syx_header + data + [0xF7])
    #         self.midi.send_sysex(self.standard_syx_header + more_syx_header, )

    def set_button_labels(self, labels):
        # full packet
        # F0 00 01 77 7F 01 06 00 04 00 04 00 00 00 01 00 01 03 50 41 4E 00 02 05 53 45 4E 44 53 00 03 00 00 04 05 57 52 49 54 45 00 05 00 F7
        # F0 00 01 77 7F 01 (header)
        # 06 00 04 00 04 00 00 00 01 00  # unknown
        # 01 (first label)
        # 03 len(label1)
        # 50 41 4E 00 ("PAN\0")
        # 02 (second label)
        # 05 len(label2))
        # 53 45 4E 44 53 00 ("SENDS\0")
        # 03 (third label)
        # 00 (zero length)
        # 00 (empty string)
        # 04 (fourth label)
        # 05 57 52 49 54 45 00 
        # 05 (fifth label?)
        # 00 (zero length)
        # (no nul!)

        # need some error handling here: this list must have exactly 5 elements (last is empty string)
                   #T6?  PAD   L4BTN ?     ?     ?     ?     ?     ?     ? 
        message = [0x06, 0x00, 0x04, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01, 0x00]
        offset = 1
        for name in labels:
            button_num = 0x00 + offset
            message.append(button_num)
            name = name.upper().encode('ascii')
            length = len(name)
            message.append(length)
            message += [char for char in name]
            offset += 1
            if(offset <= len(labels)):
                message.append(0x00)

        self.send_midi(self.standard_syx_header + message + [0xF7])
        #self.midi.send_sysex(self.standard_syx_header, message)

    def set_track_names(self, track_names):
        self.set_display_area("track_names_1-4", track_names[0:4])
        self.set_display_area("track_names_5-8", track_names[4:8])


    def register_change_instrument(callable):
        self.instrument_change_callback = callable
        
    def change_instrument(self, direction):
        def change(data):
            if(data)!=127:
                return
            self.controller.change_instrument(direction)
            inst_name = self.controller.get_current_instrument_name()
            self.set_display_area("focus_name", ["Instrument:"])
            self.set_display_area("focus_value", [inst_name.decode("UTF-8")])
            #if self.active_track < 1:
            #    self.active_track = 8
            #if self.active_track > 8:
            #    self.active_track = 1
            #self.set_active_track(self.active_track)
        return change

    def set_active_track(self, track):
        self.active_track = track
        self.send_midi([0xB0, 0x19, track])

    # --- initialisation ---
    def connect(self):
        #MidiControllerTemplate.connect(self)
        self._is_connected = True

        #self.set_lcd_directly(0, 'Nektar Panorama T6:  initialising...')
        #self.set_lcd_directly(1, 'Mackie Host Control:    connecting...')

        self._enter_mcu_mode()

        # select "track" mode ("Mute" + "Solo")
        #self._mode_track = self._MODE_TRACK_MUTE_SOLO
        #self._restore_previous_mode()

       # self.set_lcd_directly(0, 'Nektar Panorama T6:  initialised.')

        self._log('Connected.', True)

    def disconnect(self):
        self._log('Disconnecting...', True)

        #self.withdraw_all_controls()

        #self.set_lcd_directly(0, 'Nektar Panorama T6:  disconnecting...')
        #self.set_lcd_directly(1, '')

        self._leave_mcu_mode()

        self._is_connected = False
        self.midiin.close_port()
        self.midiout.close_port()
        del self.midiin
        del self.midiout
        #MidiControllerTemplate.disconnect(self)

    def go_online(self):
        pass
        #MidiControllerTemplate.go_online(self)

        #self.set_lcd_directly(0, 'Nektar Panorama T6:  initialised.')
        #self.set_lcd_directly(1, 'Mackie Host Control:    online.')

    def go_offline(self):
        pass
        #MidiControllerTemplate.go_offline(self)

        #self.set_lcd_directly(0, 'Nektar Panorama T6:  initialised.')
        #self.set_lcd_directly(1, 'Mackie Host Control:    offline.')

    def send_handshake(self):
        # F0 7E 7F 06 01 F7

        header = [0xF0, 0x7E, 0x7F]
        data = [0x06, 0x01]

        self.send_midi(header + data + [0xF7])
        #self.midi.send_sysex(header, data)

    def send_disconnect(self):
        #F0 00 01 77 7F 01 09 00 00 00 01 00 75 F7
        header = [0xF0, 0x00, 0x01, 0x77, 0x7F, 0x01, 0x09] # XXX: probably
        data = [0x00, 0x00, 0x00, 0x01, 0x00, 0x75] # unknown
        
        self.send_midi(header + data + [0xF7])
        #self.midi.send_sysex(header, data)

    def _enter_mcu_mode(self):
        self._log('Entering "MCU" mode...', True)

        self.send_handshake()
        self.initialize_controls()

        # probably some other stuff to do here, but not this...
        # clear all LEDs and switch off "transport" mode
        #self.send_midi_control_change(cc_number=self._MIDI_CC_CLEAR_ALL_LEDS, cc_value=0x00)
        #self.send_midi_control_change(cc_number=self._MIDI_CC_BUTTON_MODE_TRANSPORT, cc_value=0x00)

    def _leave_mcu_mode(self):
        self._log('Leaving "MCU" mode...', True)

        self.send_disconnect()

        # probably some other stuff to do here, but not this...
        # clear all LEDs and switch off "transport" mode
        #self.send_midi_control_change(cc_number=self._MIDI_CC_CLEAR_ALL_LEDS, cc_value=0x00)
        #self.send_midi_control_change(cc_number=self._MIDI_CC_BUTTON_MODE_TRANSPORT, cc_value=0x00)

    def process_control(self, control, value):
        if control in self.controls:
            print("Mapped control [%s]: %s" % (control, value))
            self.controls[control]["set"](value)
        else:
            print("Unmapped Control [%s]: %s" % (control, value))
        pass

    def process_sysex(self, message):
        print("process_sysex", message)
        pass

    # --- MIDI processing ---
    def receive_midi(self, data, something):
        message, timestamp = data
        self.callback_log("RECV: %s" % (" ".join([hex(c).replace("0x", "").upper().zfill(2) for c in message]),), "")
        if message[0] == 0xF0 and message[-1] == 0xF7:
            self.process_sysex(message=message)
        else:
            self.controller.send_midi(message)
        if message[0] == 0xB0:
            self.process_control(control=message[1], value=message[2])
        pass
    #     if (message[0] == 0xF0) and (message[-1] == 0xF7):
    #         if (message[1:4] == self.MIDI_MANUFACTURER_ID) and (message[4:10] == self.MIDI_DEVICE_ID):
    #             sysex_message = message[10:-1]

    #             if sysex_message == [1, 0]:
    #                 self._leave_mcu_mode()

    #                 self._mode_automap = True
    #                 self._is_connected = False
    #             elif sysex_message == [1, 1]:
    #                 if self._mode_automap:
    #                     self._mode_automap = False
    #                     self._is_connected = True

    #                     self._enter_mcu_mode()

    #                     self._restore_previous_mode()
    #                     self._restore_vpots()

    #                     # force update of LCD
    #                     self._lcd_strings = ['', '']
    #                     self.update_lcd()

    #         # all MIDI SysEx messages handled (including invalid
    #         # ones), so quit processing here
    #         return

    #     if not self._is_connected:
    #         return

    #     cc_selector = {
    #         self._MIDI_CC_FADERS: 'self.interconnector.move_fader_7bit(0, %d)',
    #         self._MIDI_CC_FADERS + 1: 'self.interconnector.move_fader_7bit(1, %d)',
    #         self._MIDI_CC_FADERS + 2: 'self.interconnector.move_fader_7bit(2, %d)',
    #         self._MIDI_CC_FADERS + 3: 'self.interconnector.move_fader_7bit(3, %d)',
    #         self._MIDI_CC_FADERS + 4: 'self.interconnector.move_fader_7bit(4, %d)',
    #         self._MIDI_CC_FADERS + 5: 'self.interconnector.move_fader_7bit(5, %d)',
    #         self._MIDI_CC_FADERS + 6: 'self.interconnector.move_fader_7bit(6, %d)',
    #         self._MIDI_CC_FADERS + 7: 'self.interconnector.move_fader_7bit(7, %d)',
    #         self._MIDI_CC_ENCODERS: 'self.interconnector.move_vpot_raw(0, %d)',
    #         self._MIDI_CC_ENCODERS + 1: 'self.interconnector.move_vpot_raw(1, %d)',
    #         self._MIDI_CC_ENCODERS + 2: 'self.interconnector.move_vpot_raw(2, %d)',
    #         self._MIDI_CC_ENCODERS + 3: 'self.interconnector.move_vpot_raw(3, %d)',
    #         self._MIDI_CC_ENCODERS + 4: 'self.interconnector.move_vpot_raw(4, %d)',
    #         self._MIDI_CC_ENCODERS + 5: 'self.interconnector.move_vpot_raw(5, %d)',
    #         self._MIDI_CC_ENCODERS + 6: 'self.interconnector.move_vpot_raw(6, %d)',
    #         self._MIDI_CC_ENCODERS + 7: 'self.interconnector.move_vpot_raw(7, %d)',
    #         self._MIDI_CC_CONTROL_PEDAL: 'self.on_control_pedal(%d & 0x01)',
    #         self._MIDI_CC_BUTTON_BANK_UP: 'self._change_mode_edit(%d & 0x01)',
    #         self._MIDI_CC_BUTTON_BANK_DOWN: 'self._change_mode_track(%d & 0x01)',
    #         self._MIDI_CC_BUTTONS_RIGHT_BOTTOM: 'self._change_mode_bank(%d & 0x01)',
    #         self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 1: 'self._change_mode_automation(%d & 0x01)',
    #         self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 2: 'self._change_mode_global_view(%d & 0x01)',
    #         self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 3: 'self._change_mode_utility(%d & 0x01)',
    #         self._MIDI_CC_BUTTON_MODE_TRANSPORT: 'self._change_mode_transport(%d & 0x01)',
    #     }

    #     # make sure that no submenu disturbs toggling the "Global
    #     # View" mode
    #     if self._mode_other == self._MODE_OTHER_GLOBAL_VIEW:
    #         del cc_selector[self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 1]

    #     if status == (MidiConnection.CONTROL_CHANGE + self._MIDI_DEVICE_CHANNEL):
    #         cc_number = message[1]
    #         cc_value = message[2]

    #         if cc_number in cc_selector:
    #             eval(cc_selector[cc_number] % cc_value)
    #         elif cc_number == 0x6B:
    #             # this controller change message is sent on entering
    #             # and leaving "Automap" mode and can be probably
    #             # ignored
    #             pass
    #         else:
    #             internal_id = 'cc%d' % cc_number
    #             status = cc_value & 0x01
    #             key_processed = self.interconnector.keypress(internal_id, status)

    #             if not key_processed:
    #                 message_string = ['status %02X: ' % status]
    #                 for byte in message:
    #                     message_string.append('%02X' % byte)
    #                 self._log(' '.join(message_string))
    #     else:
    #         message_string = ['status %02X: ' % status]
    #         for byte in message:
    #             message_string.append('%02X' % byte)
    #         self._log(' '.join(message_string))

    #def send_midi_control_change(self, channel=None, cc_number=None, cc_value=None):
    #    if not self._is_connected:
    #        return

    #    if channel:
    #        raise ValueError("The channel is fixed for this device!")

    #    MidiControllerTemplate.send_midi_control_change(self, self._MIDI_DEVICE_CHANNEL, cc_number, cc_value)

    @staticmethod
    def get_preferred_midi_input():
        if os.name == 'nt':
            return 'ZeRO MkII: Port 2'

        return 'ZeRO MkII MIDI 2'

    @staticmethod
    def get_preferred_midi_output():
        if os.name == 'nt':
            return 'ZeRO MkII: Port 2'

        return 'ZeRO MkII MIDI 2'

    # --- registration of MIDI controls ---
    def register_control(self, mcu_command, midi_switch, midi_led=None):
        midi_switch_cc = 'cc%d' % midi_switch

        if midi_led:
            midi_led_cc = 'cc%d' % midi_led
        else:
            midi_led_cc = midi_switch_cc

        self.interconnector.register_control(mcu_command, midi_switch_cc, midi_led_cc)

    def withdraw_control(self, midi_switch):
        midi_switch_cc = 'cc%d' % midi_switch

        self.interconnector.withdraw_control(midi_switch_cc)

    #def set_display_7seg(self, position, character_code):
    #    MidiControllerTemplate.set_display_7seg(self, position, character_code)

    # --- handling of Mackie Control commands ---
    def set_lcd_directly(self, line, lcd_string):
        if len(lcd_string) != 72:
            lcd_string = lcd_string.ljust(72)[:72]

        lcd_characters = []
        for _, string in enumerate(lcd_string):
            lcd_characters.append(ord(string))

        self._update_lcd_raw(line, lcd_characters)

    def update_lcd(self):
        # convert string
        for line in range(2):
            new_string = ''.join(self.get_lcd_characters(line))
            if new_string != self._lcd_strings[line]:
                self._lcd_strings[line] = new_string
                hex_codes = []

                for index, string in enumerate(new_string):
                    hex_codes.append(ord(string))
                    if index % 7 == 6:
                        hex_codes.append(0x20)
                        hex_codes.append(0x20)

                self._update_lcd_raw(line, hex_codes)

    def _update_lcd_raw(self, line, hex_codes):
        """
        send hex codes of 72 bytes to controller LCD

        line 0: top row
        line 1: bottom row
        """
        if not self._is_connected:
            return

        assert len(hex_codes) == 72

        line %= 2
        if line == 0:
            display_line = 1
        else:
            display_line = 3
        sysex_data = [0x02, 0x01, 0x00, display_line, 0x04]

        # convert string
        for hex_code in hex_codes:
            # convert illegal characters to asterisk
            if (hex_code < 0x20) or (hex_code > 0x7F):
                hex_code = 0x2A
            sysex_data.append(hex_code)

        self.send_midi_sysex(sysex_data)

        # update second display page as well:
        # * 0x01  -->  top row (left controller block)
        # * 0x02  -->  top row (right controller block)
        # * 0x03  -->  bottom row (left controller block)
        # * 0x04  -->  bottom row (right controller block)
        sysex_data[3] += 1

        self.send_midi_sysex(sysex_data)

    #def set_led(self, internal_id, led_status):
    #    if not self._is_connected:
    #        return

    #    controller_type = internal_id[:2]
    #    controller_id = int(internal_id[2:])

    #    if controller_type == 'cc':
    #        MidiControllerTemplate.send_midi_control_change(self, self._MIDI_DEVICE_CHANNEL, controller_id, led_status)
    #    else:
    #        self._log('controller type "%s" unknown.' % controller_type)

    #def _set_led(self, led_id, led_status):
    #    if not self._is_connected:
    #        return

    #    MidiControllerTemplate.send_midi_control_change(self, self._MIDI_DEVICE_CHANNEL, led_id, led_status)

    def set_vpot_led_ring(self, vpot_id, vpot_center_led, vpot_mode, vpot_position):
        mode = None
        if vpot_mode == self.VPOT_MODE_WRAP:
            mode = 0x00
        elif vpot_mode == self.VPOT_MODE_BOOST_CUT:
            mode = 0x20
        elif vpot_mode == self.VPOT_MODE_SPREAD:
            mode = 0x30
        elif vpot_mode == self.VPOT_MODE_SINGLE_DOT:
            mode = 0x40

        self._vpot_modes[vpot_id] = mode
        self._vpot_positions[vpot_id] = vpot_position

        self._set_led(self._MIDI_CC_ENCODER_MODE + vpot_id, mode)
        self._set_led(self._MIDI_CC_ENCODER_LIGHTS + vpot_id, vpot_position)

    def all_leds_off(self):
        self.send_midi_control_change(cc_number=self._MIDI_CC_CLEAR_ALL_LEDS, cc_value=0x00)

    # --- pedal handling ---
    def on_control_pedal(self, status):
        if self.interconnector.is_playing():
            mcu_command = 'stop'
        else:
            mcu_command = 'play'

        self.interconnector.keypress_unregistered(mcu_command, status)

    # --- mode handling ---
    def _change_mode_track(self, status):
        self._mode_edit = self._MODE_EDIT_OFF
        self._mode_other = self._MODE_OTHER_OFF

        if status == 1:
            self._mode_track = self._MODE_TRACK_RECORD_READY_FUNCTION

            self.register_control('record_ready_channel_1', self._MIDI_CC_BUTTONS_LEFT_TOP)
            self.register_control('record_ready_channel_2', self._MIDI_CC_BUTTONS_LEFT_TOP + 1)
            self.register_control('record_ready_channel_3', self._MIDI_CC_BUTTONS_LEFT_TOP + 2)
            self.register_control('record_ready_channel_4', self._MIDI_CC_BUTTONS_LEFT_TOP + 3)
            self.register_control('record_ready_channel_5', self._MIDI_CC_BUTTONS_LEFT_TOP + 4)
            self.register_control('record_ready_channel_6', self._MIDI_CC_BUTTONS_LEFT_TOP + 5)
            self.register_control('record_ready_channel_7', self._MIDI_CC_BUTTONS_LEFT_TOP + 6)
            self.register_control('record_ready_channel_8', self._MIDI_CC_BUTTONS_LEFT_TOP + 7)

            self.register_control('function_channel_1', self._MIDI_CC_BUTTONS_LEFT_BOTTOM)
            self.register_control('function_channel_2', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 1)
            self.register_control('function_channel_3', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 2)
            self.register_control('function_channel_4', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 3)
            self.register_control('function_channel_5', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 4)
            self.register_control('function_channel_6', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 5)
            self.register_control('function_channel_7', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 6)
            self.register_control('function_channel_8', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 7)
        else:
            self._mode_track = self._MODE_TRACK_MUTE_SOLO

            self.register_control('mute_channel_1', self._MIDI_CC_BUTTONS_LEFT_TOP)
            self.register_control('mute_channel_2', self._MIDI_CC_BUTTONS_LEFT_TOP + 1)
            self.register_control('mute_channel_3', self._MIDI_CC_BUTTONS_LEFT_TOP + 2)
            self.register_control('mute_channel_4', self._MIDI_CC_BUTTONS_LEFT_TOP + 3)
            self.register_control('mute_channel_5', self._MIDI_CC_BUTTONS_LEFT_TOP + 4)
            self.register_control('mute_channel_6', self._MIDI_CC_BUTTONS_LEFT_TOP + 5)
            self.register_control('mute_channel_7', self._MIDI_CC_BUTTONS_LEFT_TOP + 6)
            self.register_control('mute_channel_8', self._MIDI_CC_BUTTONS_LEFT_TOP + 7)

            self.register_control('solo_channel_1', self._MIDI_CC_BUTTONS_LEFT_BOTTOM)
            self.register_control('solo_channel_2', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 1)
            self.register_control('solo_channel_3', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 2)
            self.register_control('solo_channel_4', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 3)
            self.register_control('solo_channel_5', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 4)
            self.register_control('solo_channel_6', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 5)
            self.register_control('solo_channel_7', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 6)
            self.register_control('solo_channel_8', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 7)

        self._set_led(self._MIDI_CC_BUTTON_BANK_DOWN, self._mode_track)
        self._set_led(self._MIDI_CC_BUTTON_BANK_UP, self._mode_edit)

    def _change_mode_edit(self, status):
        self._mode_track = self._MODE_TRACK_OFF
        self._mode_other = self._MODE_OTHER_OFF

        if status == 1:
            self._mode_edit = self._MODE_EDIT_VSELECT_SELECT

            menu_strings = (
                'Track', 'Send', 'Panning', 'EQ',
                'Plug-In', 'Instrum.', 'Switch A', 'Switch B'
            )
            self.show_menu(1, menu_strings)

            self.register_control('vselect_channel_1', self._MIDI_CC_BUTTONS_LEFT_TOP)
            self.register_control('vselect_channel_2', self._MIDI_CC_BUTTONS_LEFT_TOP + 1)
            self.register_control('vselect_channel_3', self._MIDI_CC_BUTTONS_LEFT_TOP + 2)
            self.register_control('vselect_channel_4', self._MIDI_CC_BUTTONS_LEFT_TOP + 3)
            self.register_control('vselect_channel_5', self._MIDI_CC_BUTTONS_LEFT_TOP + 4)
            self.register_control('vselect_channel_6', self._MIDI_CC_BUTTONS_LEFT_TOP + 5)
            self.register_control('vselect_channel_7', self._MIDI_CC_BUTTONS_LEFT_TOP + 6)
            self.register_control('vselect_channel_8', self._MIDI_CC_BUTTONS_LEFT_TOP + 7)

            self.register_control('select_channel_1', self._MIDI_CC_BUTTONS_LEFT_BOTTOM)
            self.register_control('select_channel_2', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 1)
            self.register_control('select_channel_3', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 2)
            self.register_control('select_channel_4', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 3)
            self.register_control('select_channel_5', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 4)
            self.register_control('select_channel_6', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 5)
            self.register_control('select_channel_7', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 6)
            self.register_control('select_channel_8', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 7)
        else:
            self._mode_edit = self._MODE_EDIT_VSELECT_ASSIGNMENT

            self.hide_menu(1)

            self.register_control('vselect_channel_1', self._MIDI_CC_BUTTONS_LEFT_TOP)
            self.register_control('vselect_channel_2', self._MIDI_CC_BUTTONS_LEFT_TOP + 1)
            self.register_control('vselect_channel_3', self._MIDI_CC_BUTTONS_LEFT_TOP + 2)
            self.register_control('vselect_channel_4', self._MIDI_CC_BUTTONS_LEFT_TOP + 3)
            self.register_control('vselect_channel_5', self._MIDI_CC_BUTTONS_LEFT_TOP + 4)
            self.register_control('vselect_channel_6', self._MIDI_CC_BUTTONS_LEFT_TOP + 5)
            self.register_control('vselect_channel_7', self._MIDI_CC_BUTTONS_LEFT_TOP + 6)
            self.register_control('vselect_channel_8', self._MIDI_CC_BUTTONS_LEFT_TOP + 7)

            self.register_control('assignment_track', self._MIDI_CC_BUTTONS_LEFT_BOTTOM)
            self.register_control('assignment_send', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 1)
            self.register_control('assignment_pan_surround', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 2)
            self.register_control('assignment_eq', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 3)
            self.register_control('assignment_plug_in', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 4)
            self.register_control('assignment_instrument', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 5)
            self.register_control('user_switch_1', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 6)
            self.register_control('user_switch_2', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 7)

        self._set_led(self._MIDI_CC_BUTTON_BANK_DOWN, self._mode_track)
        self._set_led(self._MIDI_CC_BUTTON_BANK_UP, self._mode_edit)

    def _change_mode_transport(self, status):
        # leave other modes as is in order to return to the old one!

        if status > 0:
            self._mode_other = self._MODE_OTHER_TRANSPORT

            menu_strings = (
                'Click', 'Solo', 'Marker', 'Nudge',
                'SMPTE/Bt', '', 'Drop', 'Replace'
            )
            self.show_menu(1, menu_strings)

            self.register_control('click', self._MIDI_CC_BUTTONS_LEFT_BOTTOM)
            self.register_control('solo', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 1)
            self.register_control('marker', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 2)
            self.register_control('nudge', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 3)
            self.register_control('smpte_beats', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 4)

            self.withdraw_control(self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 5)

            self.register_control('drop', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 6)
            self.register_control('replace', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 7)

            self.register_control('rewind', self._MIDI_CC_BUTTON_REWIND, self._MIDI_CC_BUTTONS_RIGHT_BOTTOM)
            self.register_control('fast_forward', self._MIDI_CC_BUTTON_FAST_FORWARD,
                                  self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 1)
            self.register_control('stop', self._MIDI_CC_BUTTON_STOP, self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 2)
            self.register_control('play', self._MIDI_CC_BUTTON_PLAY, self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 3)
            self.register_control('cycle', self._MIDI_CC_BUTTON_CYCLE, self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 4)
            self.register_control('record', self._MIDI_CC_BUTTON_RECORD, self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 5)
        else:
            self._mode_other = self._MODE_OTHER_OFF

            self.withdraw_control(self._MIDI_CC_BUTTON_REWIND)
            self.withdraw_control(self._MIDI_CC_BUTTON_FAST_FORWARD)
            self.withdraw_control(self._MIDI_CC_BUTTON_STOP)
            self.withdraw_control(self._MIDI_CC_BUTTON_PLAY)
            self.withdraw_control(self._MIDI_CC_BUTTON_CYCLE)
            self.withdraw_control(self._MIDI_CC_BUTTON_RECORD)

            self.hide_menu(1)
            self._restore_previous_mode()

    def _change_mode_bank(self, status):
        # leave other modes as is in order to return to the old one!

        if status == 1:
            if self._mode_other != self._MODE_OTHER_OFF:
                return

            self._mode_other = self._MODE_OTHER_BANK
            self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM, 1)

            menu_strings = (
                '<<', '<', '>', '>>',
                '', '', '', ''
            )
            self.show_menu(1, menu_strings)

            self.register_control(
                'fader_banks_bank_left', self._MIDI_CC_BUTTONS_LEFT_BOTTOM)
            self.register_control(
                'fader_banks_channel_left', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 1)
            self.register_control(
                'fader_banks_channel_right', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 2)
            self.register_control(
                'fader_banks_bank_right', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 3)

            self.withdraw_control(self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 4)
            self.withdraw_control(self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 5)
            self.withdraw_control(self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 6)
            self.withdraw_control(self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 7)
        else:
            if self._mode_other != self._MODE_OTHER_BANK:
                return

            self._mode_other = self._MODE_OTHER_OFF
            self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM, 0)

            self.hide_menu(1)
            self._restore_previous_mode()

    def _change_mode_automation(self, status):
        # leave other modes as is in order to return to the old one!

        if status == 1:
            if self._mode_other != self._MODE_OTHER_OFF:
                return

            self._mode_other = self._MODE_OTHER_AUTOMATION
            self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 1, 1)

            menu_strings = (
                'Read/Off', 'Write', 'Trim', 'Touch',
                'Latch', '', '', 'Group'
            )
            self.show_menu(1, menu_strings)

            self.register_control(
                'automation_read_off', self._MIDI_CC_BUTTONS_LEFT_BOTTOM)
            self.register_control(
                'automation_write', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 1)
            self.register_control(
                'automation_trim', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 2)
            self.register_control(
                'automation_touch', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 3)
            self.register_control(
                'automation_latch', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 4)

            self.withdraw_control(self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 5)
            self.withdraw_control(self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 6)

            self.register_control(
                'group', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 7)
        else:
            if self._mode_other != self._MODE_OTHER_AUTOMATION:
                return

            self._mode_other = self._MODE_OTHER_OFF
            self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 1, 0)

            self.hide_menu(1)
            self._restore_previous_mode()

    def _change_mode_global_view(self, status):
        # leave other modes as is in order to return to the old one!

        if status == 1:
            if self._mode_other != self._MODE_OTHER_OFF:
                return

            self._mode_other = self._MODE_OTHER_GLOBAL_VIEW
            self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 2, 1)

            menu_strings = (
                'MIDI', 'Inputs', 'AudioTr.', 'Instrum.',
                'AUX', 'Busses', 'Outputs', 'User'
            )
            self.show_menu(1, menu_strings)

            self.register_control(
                'global_view_midi_tracks', self._MIDI_CC_BUTTONS_LEFT_BOTTOM)
            self.register_control(
                'global_view_inputs', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 1)
            self.register_control(
                'global_view_audio_tracks', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 2)
            self.register_control(
                'global_view_audio_instruments', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 3)
            self.register_control(
                'global_view_aux', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 4)
            self.register_control(
                'global_view_busses', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 5)
            self.register_control(
                'global_view_outputs', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 6)
            self.register_control(
                'global_view_user', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 7)

            self.register_control(
                'global_view', self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 1, self._MIDI_CC_LED_AUTOMAP_LEARN)
        else:
            if self._mode_other != self._MODE_OTHER_GLOBAL_VIEW:
                return

            self._mode_other = self._MODE_OTHER_OFF
            self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 2, 0)

            self.withdraw_control(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 1)

            self.hide_menu(1)
            self._restore_previous_mode()

    def _change_mode_utility(self, status):
        # leave other modes as is in order to return to the old one!

        if status == 1:
            if self._mode_other != self._MODE_OTHER_OFF:
                return

            self._mode_other = self._MODE_OTHER_UTILITY
            self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 3, 1)

            menu_strings = (
                'Enter', 'Cancel', '', 'Undo',
                '', '', '', 'Save'
            )
            self.show_menu(1, menu_strings)

            self.register_control(
                'utilities_enter', self._MIDI_CC_BUTTONS_LEFT_BOTTOM)
            self.register_control(
                'utilities_cancel', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 1)

            self.withdraw_control(self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 2)

            self.register_control(
                'utilities_undo', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 3)

            self.withdraw_control(self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 4)
            self.withdraw_control(self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 5)
            self.withdraw_control(self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 6)

            self.register_control(
                'utilities_save', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 7)
        else:
            if self._mode_other != self._MODE_OTHER_UTILITY:
                return

            self._mode_other = self._MODE_OTHER_OFF
            self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 3, 0)

            self.hide_menu(1)
            self._restore_previous_mode()

    def _restore_previous_mode(self):
        if self._mode_track:
            if self._mode_track == self._MODE_TRACK_RECORD_READY_FUNCTION:
                self._change_mode_track(1)
            else:
                self._change_mode_track(2)
        else:
            if self._mode_edit == self._MODE_EDIT_VSELECT_SELECT:
                self._change_mode_edit(1)
            else:
                self._change_mode_edit(2)

        self.register_control(
            'shift', self._MIDI_CC_BUTTONS_RIGHT_TOP)
        self.register_control(
            'control', self._MIDI_CC_BUTTONS_RIGHT_TOP + 1)
        self.register_control(
            'command_alt', self._MIDI_CC_BUTTONS_RIGHT_TOP + 2)
        self.register_control(
            'option', self._MIDI_CC_BUTTONS_RIGHT_TOP + 3)
        self.register_control(
            'cursor_left', self._MIDI_CC_BUTTONS_RIGHT_TOP + 4)
        self.register_control(
            'cursor_right', self._MIDI_CC_BUTTONS_RIGHT_TOP + 5)
        self.register_control(
            'cursor_down', self._MIDI_CC_BUTTONS_RIGHT_TOP + 6)
        self.register_control(
            'cursor_up', self._MIDI_CC_BUTTONS_RIGHT_TOP + 7)

        self.register_control(
            'name_value', self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 4)
        self.register_control(
            'flip', self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 5)
        self.register_control(
            'scrub', self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 6)
        self.register_control(
            'zoom', self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 7)

        self.register_control(
            'global_view', self._MIDI_CC_LED_AUTOMAP_LEARN)
        self.register_control(
            'rude_solo', self._MIDI_CC_LED_AUTOMAP_VIEW)
        self.register_control(
            'relay_click', self._MIDI_CC_LED_AUTOMAP_USER)
        self.register_control(
            'beats', self._MIDI_CC_LED_AUTOMAP_FX)

    def _restore_vpots(self):
        for vpot_id in range(8):
            self._set_led(
                self._MIDI_CC_ENCODER_MODE + vpot_id, self._vpot_modes[vpot_id])
            self._set_led(
                self._MIDI_CC_ENCODER_LIGHTS + vpot_id, self._vpot_positions[vpot_id])
