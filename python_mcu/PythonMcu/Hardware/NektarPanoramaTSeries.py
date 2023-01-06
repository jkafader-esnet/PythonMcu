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
from PythonMcu.configuration.patches import patches
#from PythonMcu.Midi.MidiConnection import MidiConnection
import rtmidi
from rtmidi.midiutil import open_midiinput
import threading


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
        self.shift_mode = False
        self.timer = None
        self.locked = False
        self.controls = {
            0: {"name": "Fader 1", "set": self.set_track_value(0) },
            1: {"name": "Fader 2", "set": self.set_track_value(1) },
            2: {"name": "Fader 3", "set": self.set_track_value(2) },
            3: {"name": "Fader 4", "set": self.set_track_value(3) },
            4: {"name": "Fader 5", "set": self.set_track_value(4) },
            5: {"name": "Fader 6", "set": self.set_track_value(5) },
            6: {"name": "Fader 7", "set": self.set_track_value(6) },
            7: {"name": "Fader 8", "set": self.set_track_value(7) },

            48: {"name": "Rotary 1", "set": self.set_rotary_value(0) },
            49: {"name": "Rotary 2", "set": self.set_rotary_value(1) },
            50: {"name": "Rotary 3", "set": self.set_rotary_value(2) },
            51: {"name": "Rotary 4", "set": self.set_rotary_value(3) },
            52: {"name": "Rotary 5", "set": self.set_rotary_value(4) },
            53: {"name": "Rotary 6", "set": self.set_rotary_value(5) },
            54: {"name": "Rotary 7", "set": self.set_rotary_value(6) },
            55: {"name": "Rotary 8", "set": self.set_rotary_value(7) },

            16: { "name": "Track 1 Button", "set": self.toggle_button_value(0) },
            17: { "name": "Track 2 Button", "set": self.toggle_button_value(1) },
            18: { "name": "Track 3 Button", "set": self.toggle_button_value(2) },
            19: { "name": "Track 4 Button", "set": self.toggle_button_value(3) },
            20: { "name": "Track 5 Button", "set": self.toggle_button_value(4) },
            21: { "name": "Track 6 Button", "set": self.toggle_button_value(5) },
            22: { "name": "Track 7 Button", "set": self.toggle_button_value(6) },
            23: { "name": "Track 8 Button", "set": self.toggle_button_value(7) },

            94: { "name": "Track Master Button", "set": self.panic },
            96: { "name": "Shift", "set": self.set_shift_mode },

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

            106: {"name": "Soft Button 0", "set": self.soft_button(0) },
            107: {"name": "Soft Button 1", "set": self.soft_button(1) },
            108: {"name": "Soft Button 2", "set": self.soft_button(2) },
            109: {"name": "Soft Button 3", "set": self.soft_button(3) },
        }
        self.current_instrument = patch
        self.setup_mappings()

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

    def setup_mappings(self):
        mapped_controls = self.controller.get_mapped_instrument_controls()
        vcontrols = {}
        for name, ctrl in patches[self.current_instrument].items():
            if name in not in ["groups", "shift"]:
                vcontrols[name] = ctrl
                if mapped_controls[name]['cc'] is None: # cc of None indicates "no mapping." Log.
                    self._log("No mapping found for control %s" % name)
                else:
                    vcontrols[name]["value"] = mapped_controls["name"]["value"]
        self.vcontrols = vcontrols
        self.groups = patches[self.current_instrument]["groups"]
        self.shift = patches[self.current_instrument]["shift"]
        self.selected_group = 0

    def highlight_soft_button(self, num):
        offset = 106
        self.send_midi([0xB0, offset+num, 127])

    def soft_button(self, num):
        def setter(value):
            if value == 127:
                self.selected_group = num
                self.render_display()
        return setter

    def panic(self):
        pass

    def send_midi(self, message):
        while self.locked:
            time.sleep(0.005)
        self.midiout.send_message(message)
        if message[0] == 0xF0:
            time.sleep(0.004)
        
    def set_shift_mode(self, mode):
        self.shift_mode = bool(mode)
        self.render_display()

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
            func_name = self.vcontrols["P%s" % track_number]["set"]
            parameters = self.vcontrols["P%s" % track_number]["param"]
            getattr(self, func_name)(**parameters)(value)
        return set

    def toggle_button_value(self, track_number):
        def setter(value):
            func_name = self.vcontrols["B%s" % track_number]["set"]
            parameters = self.vcontrols["B%s" % track_number]["param"]
            if(value): # if this is button _press_ rather than _release_
                # toggle the value
                curval = self.vcontrols["B%s" % track_number]["value"]
                newval = 0 if curval == 127 else 127
                getattr(self, func_name)(**parameters)(newval)
        return setter

    def set_track_value(self, track_number):
        def set(value):
            keys = [k for k in self.visible_controls.keys()]
            if track_number >= len(keys):
                return
            track_name = keys[track_number]
            func_name = self.visible_controls[track_name]["set"]
            parameters = self.visible_controls[track_name]["param"]
            getattr(self, func_name)(**parameters)(value)
        return set

    def set_vtrack_value(self, fader_number, value):
        self.send_midi([0xB0, fader_number, value])

    def vtrack_setter(self, track, invert=False):
        def set(value, invert=invert, changed=True):
            if invert:
                value = 127 - value
            track_name = "F%s" % track
            control = self.visible_controls[track_name]
            control["value"] = value
            screen_position = control["current_screen_position"]
            self.set_vtrack_value(screen_position, value)

            focus_name = control.get("long_name", control.get("name", ""))
            if changed:
                self.set_display_area("focus_name", [focus_name,])
                self.set_display_area("focus_value", ["%s" % control['value']])
                self.controller.send_control_change(control.get("name"), 127 - control.get("value") if invert else control.get("value"))
        return set

    def set_vpot_value(self, track_number, value):
        offset = 48 # first pot control number
        self.send_midi([0xB0, offset + track_number, value])

    def countdown_to_instrument(self, seconds=3):
        if hasattr(self.timer, "cancel"):
            self.timer.cancel()
        def display_instrument():
            self.set_display_area("focus_name", ["Instrument:"])
            self.set_display_area("focus_value", [self.current_instrument])
            self.countdown_to_instrument(seconds=seconds)
        self.timer = threading.Timer(seconds, display_instrument)
        self.timer.start()
    
    def vpot_setter(self, track, invert=False):
        def set(value, invert=invert, changed=True):
            control_name = "P%s" % track
            control = self.visible_controls[control_name]
            delta = value
            if value == 127:
                delta = -1
            if value == 124:
                delta = -4
            if value == 122:
                delta = -6
            if invert:
                delta = -1 * delta
            if delta not in [6, 4, 1, -1, -4, -6]:
                delta = 0
            self._log("Delta = %s" % delta)
            if changed:
                control["value"] += delta
                if control["value"] <= 0:
                    control["value"] = 0
                if control["value"] >= 127:
                    control["value"] = 127
                focus_name = control.get("long_name", control.get("name", ""))
                self.set_display_area("focus_name", [focus_name,])
                self.set_display_area("focus_value", ["%s" % control['value']])
                self.controller.send_control_change(control.get("name"), 127 - control.get("value") if invert else control.get("value"))
            screen_position = control["current_screen_position"]
            self.set_vpot_value(screen_position, control["value"])
        return set

    def set_vbutton_value(self, track_number, value):
        offset = 16 # first button control number
        self.send_midi([0xB0, offset + track_number, value])
    
    def vbutton_setter(self, track, invert=False, exclusive_with=[]):
        def setter(value, invert=invert, changed=True, force=True):
            control_name = "B%s" % track
            control = self.visible_buttons[control_name]
            if value == 127 and changed: # value = 127 represents "button down"
                value = 0 if control["value"] == 127 else 127 # if the button has been pressed, toggle the value
            if changed or force:
                control["value"] = value
            button_position = control["current_button_position"]
            self.set_vbutton_value(button_position, control['value'])
            if changed:
                for ctrl in exclusive_with:
                    other_control_name = "B%s" % ctrl
                    other_control = self.visible_buttons[other_control_name]
                    setter = self.resolve_track_setter(other_control['set'])
                    set_track = setter(**other_control['param'])
                    set_track(0, invert=False, changed=False, force=True)
                focus_name = control.get("long_name", control.get("name", ""))
                self.set_display_area("focus_name", [focus_name,])
                self.set_display_area("focus_value", ["%s" % control['value']])
                self.controller.send_control_change(control.get("name"), 127 - control.get("value") if invert else control.get("value"))
        return setter

    @staticmethod
    def get_usage_hint():
        return 'Connect the controller\'s USB port to your computer ' + \
               'and switch to preset #32 (Ableton Live Automap).'

    def _log(self, message, repaint=False):
        self.callback_log('[Nektar Panorama T6]  ' + message, repaint)

    def set_mixer_mode(self):
        self.mode = "mixer"
        data = [0x06, 0x02, 0x7F, 0x00, 0x00]
        self.send_midi(self.standard_syx_header + data + [0xF7])
        # wait a while. Don't overload buffer.
        #time.sleep(0.1)

        #return self.midi.send_sysex(self.standard_syx_header, data)

    def set_pan_mode(self):
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
        self.set_mixer_mode()
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
        self.set_mixer_mode()

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
        self.countdown_to_instrument(seconds=3)
        self.render_display()

    def printable_hex(self, message):
        return (" ".join([hex(b).replace("0x", '').zfill(2) for b in message])).upper()

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
        unimplemented = []
        if(area in unimplemented):
            self._log("XXX: area %s is unimplemented" % area)
            return
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
            },
        }
        if area not in areas:
            raise Exception("Display area %s not found" % area)
        data_length = areas[area]['data_length']
        if len(data) != data_length:
            raise Exception("Wrong string count for area %s. You provided %s strings but %s are required" % (area, len(data), areas[area]['data_length']))
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
        if len(track_names) > 8:
            self._log("Too many track names. Truncating to 8")
            track_names = track_names[:8]
        if len(track_names) < 8:
            self._log("Not enough track names. Padding with empty strings to 8")
            track_names += [''] * (8 - len(track_names))
        self.set_display_area("track_names_1-4", track_names[0:4])
        self.set_display_area("track_names_5-8", track_names[4:8])

    def set_pan_names(self, track_names):
        if len(track_names) > 8:
            self._log("Too many track names. Truncating to 8")
            track_names = track_names[:8]
        if len(track_names) < 8:
            self._log("Not enough track names. Padding with empty strings to 8")
            track_names += [''] * (8 - len(track_names))
        self.set_display_area("pan_names_1-4", track_names[0:4])
        self.set_display_area("pan_names_5-8", track_names[4:8])


    def register_change_instrument(callable):
        self.instrument_change_callback = callable
    
    def resolve_track_setter(self, func_name):
        return getattr(self, func_name)

    def render_display(self):
        if self.shift_mode:
            group_data = self.shift[self.selected_group]
        else:
            group_data = self.groups[self.selected_group]
        if group_data["layout"] == "track":
            self.set_mixer_mode()
        if group_data["layout"] == "pan":
            self.set_pan_mode()
        if group_data["layout"] == "blank":
            self.set_mixer_mode()
        self.set_display_area("focus_name", ["Instrument:"])
        self.set_display_area("focus_value", [self.current_instrument])
        if not self.shift_mode:
            self.set_button_labels([group["name"] for group in self.groups])
            selected_group_name = self.groups[self.selected_group]["name"]
        if self.shift_mode:
            self.set_button_labels([group["name"] for group in self.shift])
            selected_group_name = self.shift[self.selected_group]["name"]
        track_names = []
        self.visible_controls = {}
        self.visible_buttons = {}
        current_position = 0
        button_position = 0
        selector = "F"
        if group_data["layout"] == "pan":
            selector = "P"
        for name, track in self.vcontrols.items():
            if selected_group_name in track["groups"] and name[0] == selector:
                track_names.append(track["name"])
                self.visible_controls[name] = track
                self.visible_controls[name]["current_screen_position"] = current_position
                current_position += 1
            if selected_group_name in track["groups"] and name[0] == "B":
                self.visible_buttons[name] = track
                self.visible_buttons[name]["current_button_position"] = button_position
                button_position += 1
        if group_data["layout"] in ["track", "blank"]:
            self.set_track_names(track_names)
        if group_data["layout"] in ["pan",]:
            self.set_pan_names(track_names)
        self.set_active_track(1)
        self.highlight_soft_button(self.selected_group)
        for name, track in self.visible_controls.items():
            setter = self.resolve_track_setter(track['set'])
            set_track = setter(**track['param'])
            set_track(track['value'], invert=False, changed=False)
        for i in range(len(self.visible_controls),8):
            if selector == "P":
                self.set_vpot_value(i, 0)
            else:
                self.set_vtrack_value(i, 0)
        for name, button in self.visible_buttons.items():
            setter = self.resolve_track_setter(button['set'])
            set_track = setter(**button['param'])
            set_track(button['value'], invert=False, changed=False)
        for i in range(len(self.visible_buttons),8):
            self.set_vbutton_value(i, 0)

    def change_instrument(self, direction):
        def change(data):
            if(data)!=127:
                return
            self.controller.change_instrument(direction)
            self.current_instrument = self.controller.get_current_instrument_name()
            self.selected_group = 0
            self.setup_mappings()
            self.render_display()
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
        if hasattr(self.timer, "cancel"):
            self.timer.cancel()
        del self.midiin
        del self.midiout

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
        if message[0] == 0xF0 and message[-1] == 0xF7:
            self.process_sysex(message=message)
        elif message[0] == 0xB0:
            self.process_control(control=message[1], value=message[2])
        # if it's not sysex, and not a control, discard.
	pass

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
