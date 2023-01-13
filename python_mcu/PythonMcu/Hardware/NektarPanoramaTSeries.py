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
from PythonMcu.configuration.midi_states import MIDI_CONNECTING, MIDI_DISCONNECTING, MIDI_DISCONNECTED, MIDI_CONNECTED, MCU_CONNECTING, MCU_DISCONNECTING, MCU_CONNECTED
import rtmidi
from rtmidi.midiutil import open_midiinput
import threading

LOADING = 0
READY = 1

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCU Controller")

class NektarPanoramaTSeries(MidiControllerTemplate):
    FORMATTED_NAME = "Nektar Panorama T4/T6"

    # Nektar Technology Inc -- lookup here: https://www.midi.org/specifications/midi-reference-tables/manufacturer-sysex-id-numbers
    MIDI_MANUFACTURER_ID = [0x00, 0x01, 0x77]

    def __init__(self, midi_port, patch, controller):
        super().__init__(midi_port, midi_port)
        self.controller = controller
        self.active_track = 1
        self.mode = "mixer"
        self.shift_mode = False
        self.timer = None
        self.locked = False
        self.controls = {
            14: {"name": "MASTER Fader", "set": self.master_fader_value },
            97: {"name": "MASTER Button", "set": self.toggle_master_button },

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

            96: { "name": "Shift", "set": self.set_shift_mode },

            80: { "name": "Transport: Loop", "set": self.unmapped(80) },
            81: { "name": "Transport: Reverse", "set": self.unmapped(81) },
            82: { "name": "Transport: Forward", "set": self.unmapped(82) },
            83: { "name": "Transport: Stop", "set": self.unmapped(83) },
            84: { "name": "Transport: Play", "set": self.unmapped(84) },
            85: { "name": "Transport: Record", "set": self.unmapped(85) },

            91: {"name": "Track-",      "set": self.change_instrument(direction=-1) },
            92: {"name": "Track+",      "set": self.change_instrument(direction=1) },
            94: {"name": "Browser",     "set": self.patch_list },
            95: {"name": "View",        "set": self.toggle_view },

            99:  {"name": "Mixer",      "set": self.soft_button(0) },
            100: {"name": "Instrument", "set": self.soft_button(1) },
            101: {"name": "Multi",      "set": self.soft_button(2) },
            101: {"name": "Internal",   "set": self.soft_button(3) },

            106: {"name": "Soft Button 0", "set": self.soft_button(0) },
            107: {"name": "Soft Button 1", "set": self.soft_button(1) },
            108: {"name": "Soft Button 2", "set": self.soft_button(2) },
            109: {"name": "Soft Button 3", "set": self.soft_button(3) },
        }
        self.current_instrument = patch
        self.setup_mappings()

        self.midi_state = MIDI_DISCONNECTED
        self.data_state = LOADING
        self.standard_syx_header = [0xF0, 0x00, 0x01, 0x77, 0x7F, 0x01]
        self.midi_port = midi_port
        self._exact_port_name = ''
        self.midi_connect()

    def try_connection(self):
        try:
            self.midi_connect()
        except Exception as e:
            self._log("Received exception trying connect: %s" % e)

    def check_midi_connection(self):
        if not self.midiout:
            self.disconnect()
            return
        if self._exact_port_name not in self.midiout.get_ports():
            self.disconnect()
            return
        
    def midi_connect(self):
        self.midi_state = MIDI_CONNECTING
        if not hasattr(self, "midiout"):
            self.midiout = rtmidi.MidiOut()
        self.port_list = self.midiout.get_ports()
        self.port_num = None
        for i in range(len(self.port_list)):
            port = self.port_list[i]
            if self.midi_port in port and 'RtMidi' not in port:
                self._exact_port_name = port
                self.port_num = i
                break
        if self.port_num is None:
            self.midi_state = MIDI_DISCONNECTED
            return
        self.midiout.open_port(self.port_num)

        self.midiin, self.port_name = open_midiinput(self.port_num)
        self.midiin.ignore_types(sysex=False)
        self.midiin.set_callback(self.receive_midi)
        self.midi_state = MIDI_CONNECTED

    def setup_mappings(self):
        mapped_controls = self.controller.get_mapped_instrument_controls()
        vcontrols = {}
        for name, ctrl in patches[self.current_instrument].items():
            if name not in ["groups", "shift"]:
                vcontrols[name] = ctrl
                if mapped_controls.get(ctrl['name'], {}).get('cc') is None: # cc of None indicates "no mapping." Log.
                    self._log("No mapping found for control %s" % ctrl['name'])
                else:
                    curval = mapped_controls[ctrl['name']]["cur"]
                    if vcontrols[name].get("param", {}).get("invert"):
                        curval = 127 - curval
                    if curval <= 0:
                        curval = 0
                    if curval >= 127:
                        curval = 127
                    vcontrols[name]["value"] = curval
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

    def master_fader_value(self, value):
        self.controller.send_control_change("Volume", value)

    def toggle_master_button(self, value):
        if value == 127 and not self.shift_mode:
            self._log("sending normal panic")
            self.controller.send_midi_panic()
        if value == 127 and self.shift_mode:
            self.shift_mode = False
            self._log("doing full panic")
            self.disconnect()
            self.controller.do_full_panic()

    def send_midi(self, message):
        while self.locked:
            time.sleep(0.005)
        self.locked = True
        try:
            self.midiout.send_message(message)
        except Exception as e:
            self.midi_state = MIDI_DISCONNECTED
        self.locked = False
        if message[0] == 0xF0:
            time.sleep(0.004)
        
    def set_shift_mode(self, mode):
        self.shift_mode = bool(mode)
        self.render_display()

    def unmapped(self, *args, **kwargs):
        self._log("Control %s unmapped" % args[0])
        pass

    def patch_list(self, *args, **kwargs):
        pass

    def toggle_view(self, value):
        if value == 127:
            self.view_mode = True
            self.visible_controls = {}
            for k, button in self.visible_buttons.items():
                button['current_screen_position'] = button.get('current_button_position', 0)
                self.visible_controls[k.replace("B", "F")] = button
            self.set_mixer_mode()
            if hasattr(self, "timer"):
                self.timer.cancel()
            button_names = []
            i = 0
            for name, button in self.visible_buttons.items():
                i += 1
                self.set_display_area("focus_name", ["Button View",])
                self.set_display_area("focus_value", ["",])
                button_names.append("B%s: %s" % (i, button['name']))
                setter = self.resolve_track_setter('vtrack_setter') # not button['set'] -- we're setting the mixer track values rather than button lights.
                set_track = setter(**button['param'])
                set_track(button['value'], invert=False, changed=False)
            self.set_track_names(button_names)
            self.countdown_to_instrument()
        else:
            self.view_mode = False
            self.render_display()
        pass

    def display_settings_page(self, *args, **kwargs):
        def func(*args, **kwargs):
            pass
        return func

    def countdown_to_track_mode(self, seconds=4):
        if hasattr(self, "timer"):
            self.timer.cancel()
        def back_to_last_group():
            if hasattr(self, "last_group") and self.selected_group != self.last_group:
                self.selected_group = self.last_group
                self.render_display()
            self.countdown_to_instrument()
        self.timer = threading.Timer(seconds, back_to_last_group)
        self.timer.start()
        
    def set_rotary_value(self, track_number):
        def set(value):
            if self.selected_group != 3:
                self.last_group = self.selected_group
                self.selected_group = 3
                self.render_display()
                self.countdown_to_track_mode()
            keys = [k for k in self.visible_controls.keys()]
            if track_number >= len(keys):
                return
            track_name = keys[track_number]
            func_name = self.vcontrols[track_name]["set"]
            parameters = self.vcontrols[track_name]["param"]
            getattr(self, func_name)(**parameters)(value)
        return set

    def toggle_button_value(self, track_number):
        def setter(value):
            keys = [k for k in self.visible_buttons.keys()]
            if track_number >= len(keys):
                return
            control_key = keys[track_number]
            func_name = self.visible_buttons[control_key]["set"]
            parameters = self.visible_buttons[control_key]["param"]
            if(value): # if this is button _press_ rather than _release_
                # toggle the value
                curval = self.visible_buttons[control_key]["value"]
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

    def vtrack_setter(self, track, invert=False, exclusive_with=[]):
        # exclusive_with can be ignored here. Introduced for completeness with button params
        def set(value, invert=invert, changed=True):
            if invert:
                value = 127 - value
            track_name = "F%s" % track
            control = self.visible_controls[track_name]
            screen_position = control["current_screen_position"]
            if control.get("has_latched") or not changed:
                control["value"] = value
                self.set_vtrack_value(screen_position, value)

            focus_name = control.get("long_name", control.get("name", ""))
            if changed:
                self.set_display_area("focus_name", [focus_name,])
                if not control.get("has_latched"):
                    if(value < control.get("value") - 1):
                        self.set_display_area("focus_value", ["- DOWN -"] if invert else ["- UP -"])
                    if(value > control.get("value") + 1):
                        self.set_display_area("focus_value", ["- UP -"] if invert else ["- DOWN -"])
                    if(value <= control.get("value") + 1 and value >= control.get("value") - 1):
                        control["has_latched"] = True
                if control.get("has_latched"):
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
            # correct the values for CC 1 and 2 while we're at it -- they get weird
            control_keys = [k for k in self.visible_controls.keys()][0:2]
            for key in control_keys:
                value = self.visible_controls[key]["value"]
                setter = self.resolve_track_setter(self.visible_controls[key]['set'])
                set_track = setter(**self.visible_controls[key]["param"])
                set_track(value, invert=False, changed=False)
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
                if hasattr(self, "view_mode") and self.view_mode:
                    self.toggle_view(127)
        return setter

    @staticmethod
    def get_usage_hint():
        return 'Connect the controller\'s USB port to your computer ' + \
               'and switch to preset #32 (Ableton Live Automap).'

    def _log(self, message, *args):
        logger.warning(message, *args)

    def set_mixer_mode(self):
        self.mode = "mixer"
        data = [0x06, 0x02, 0x7F, 0x00, 0x00]
        self.send_midi(self.standard_syx_header + data + [0xF7])

    def set_mode_numbered_tracks(self):
        self.mode = "numbered_tracks"
        data = [0x06, 0x06, 0x7F, 0x00, 0x00]
        return self.send_midi(self.standard_syx_header + data + [0xF7])
        
    def set_mode_function_screen(self):
        self.mode = "function_screen"
        data = [0x06, 0x11, 0x7F, 0x00, 0x00]
        return self.send_midi(self.standard_syx_header + data + [0xF7])

    def set_mode_grid_screen(self):
        self.mode = "grid_screen"
        data = [0x06, 0x15, 0x7F, 0x00, 0x00]
        return self.send_midi(self.standard_syx_header + data + [0xF7])

    def set_mode_list_screen(self):
        self.mode = "list_screen"
        data = [0x06, 0x1A, 0x7F, 0x00, 0x00]
        return self.send_midi(self.standard_syx_header + data + [0xF7])

    def set_pan_mode(self):
        self.mode = "pan"
        data = [0x06, 0x10, 0x7F, 0x00, 0x00]
        return self.send_midi(self.standard_syx_header + data + [0xF7])

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

    def set_display_area(self, area, data, offset_override=None):
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
            "raw_list_items": {
                "header": bytes([0x06, 0x00, 0x08]),
                "data_length": 4,
                "offset": 0x00
            },
        }
        if area == "raw_list_items":
            self.mode = "raw"
        if area not in areas:
            raise Exception("Display area %s not found" % area)
        data_length = areas[area]['data_length']
        if len(data) != data_length:
            raise Exception("Wrong string count for area %s. You provided %s strings but %s are required" % (area, len(data), areas[area]['data_length']))
        formatter = areas[area].get('format', self.format_string_array)
        header = areas[area]['header']
        offset = offset_override if offset_override is not None else areas[area]['offset']
        message = header + formatter(data, offset=offset)
        return self.send_midi(self.standard_syx_header + [c for c in message] + [0xF7])

    def set_track_names(self, track_names):
        if len(track_names) > 8:
            track_names = track_names[:8]
        if len(track_names) < 8:
            track_names += [''] * (8 - len(track_names))
        self.set_display_area("track_names_1-4", track_names[0:4])
        self.set_display_area("track_names_5-8", track_names[4:8])

    def set_pan_names(self, track_names):
        if len(track_names) > 8:
            track_names = track_names[:8]
        if len(track_names) < 8:
            track_names += [''] * (8 - len(track_names))
        self.set_display_area("pan_names_1-4", track_names[0:4])
        self.set_display_area("pan_names_5-8", track_names[4:8])
    

    def set_list_items(self, track_names):
        if len(track_names) > 8:
            track_names = track_names[:8]
        if len(track_names) < 8:
            track_names += [''] * (8 - len(track_names))
        base_offset = 8
        while base_offset <= 127:
            self.set_display_area("list_items_1-4", track_names[0:4], offset_override=base_offset)
            self.set_display_area("list_items_5-8", track_names[4:8], offset_override=base_offset+4)
            base_offset += 8
            print("base offset is %s" % base_offset)
            time.sleep(0.5)
    
    def resolve_track_setter(self, func_name):
        return getattr(self, func_name)

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

    def countdown_to_ready(self, seconds=1):
        if hasattr(self.timer, "cancel"):
            self.timer.cancel()
        def disconnect_when_ready():
            if self.data_state == READY:
                self.disconnect()
            else:
                self.countdown_to_ready(seconds=seconds)
        self.timer = threading.Timer(seconds, disconnect_when_ready)
        self.timer.start()

    def render_loading_screen(self):
        #self.set_display_area("focus_name", ["Loading"])
        #self.set_display_area("focus_value", ["Please Wait"])
        #self.set_mode_list_screen()
        #self.set_display_area("menu_name", ["please", "wait"])
        #self.set_list_items(["Loading", "Please Wait"])
        #self.set_mode_numbered_tracks()
        data = [0x09, 0x06, 0x00, 0x00, 0x01, 0x36, 0x39]
        self.send_midi(self.standard_syx_header + data + [0xF7])
        self.send_midi([0xB0, 0x63, 0x7F])
        data = [0x0D, 0x04, 0x00, 0x00, 0x01, 0x00, 0x6D]
        self.send_midi(self.standard_syx_header + data + [0xF7])
        self.set_display_area("raw_list_items", ["Sound Engine", "Loading", "", "Please Wait.."])
        self.countdown_to_ready()
        #active_track = 0
        #while active_track < 8:
        #    active_track += 1
        #    self.set_active_track(active_track)
        #    time.sleep(0.5)
        
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
                self.visible_controls[name]['has_latched'] = False
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
        return change

    def set_active_track(self, track):
        self.active_track = track
        self.send_midi([0xB0, 0x19, track])

    # --- initialisation ---
    def mcu_connect(self):
        self._enter_mcu_mode()

    def disconnect(self):
        if self.midi_state == MCU_CONNECTED:
            self.midi_state == MCU_DISCONNECTING
        if self.midi_state == MIDI_CONNECTED:
            self.midi_state == MIDI_DISCONNECTING
        self._log('Disconnecting...')

        self._leave_mcu_mode()
        self._log('MCU Disconnected.')
        self.midi_state = MIDI_DISCONNECTING

        self.midiin.close_port()
        self.midiout.close_port()
        self.is_midi_connected = False
        if hasattr(self.timer, "cancel"):
            self.timer.cancel()
        del self.midiin
        del self.midiout
        self.midi_state = MIDI_DISCONNECTED
        self._log('MIDI Disconnected.')

    def send_handshake(self):
        # F0 7E 7F 06 01 F7
        header = [0xF0, 0x7E, 0x7F]
        data = [0x06, 0x01]

        self.send_midi(header + data + [0xF7])

    def send_disconnect(self):
        #F0 00 01 77 7F 01 09 00 00 00 01 00 75 F7
        header = [0xF0, 0x00, 0x01, 0x77, 0x7F, 0x01, 0x09] # XXX: probably
        data = [0x00, 0x00, 0x00, 0x01, 0x00, 0x75] # unknown
        
        self.send_midi(header + data + [0xF7])
        #self.midi.send_sysex(header, data)

    def _enter_mcu_mode(self):
        self.midi_state = MCU_CONNECTING
        self._log('Entering "MCU" mode...')

        self.send_handshake()

    def _leave_mcu_mode(self):
        if self.midi_state == MCU_CONNECTED:
            self.midi_state = MCU_DISCONNECTING
        self._log('Leaving "MCU" mode...')

        self.send_disconnect()

    def process_control(self, control, value):
        if control in self.controls:
            self.controls[control]["set"](value)
        else:
            print("Unmapped Control [%s]: %s" % (control, value))
        pass

    def process_sysex(self, message):
        if self.midi_state == MCU_CONNECTING: # if we are in this state and we've received sysex, we're awaiting handshake. Handshake data below.
            if message ==  [240, 126, 127, 6, 2, 0, 1, 119, 103, 72, 66, 64, 48, 49, 48, 54, 247]:
                self.midi_state = MCU_CONNECTED
                self._log('MCU Connected.')
                if self.data_state == READY:
                    self.initialize_controls()
                if self.data_state == LOADING:
                    self.render_loading_screen()
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

