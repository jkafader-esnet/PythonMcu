# -*- coding: utf-8 -*-

"""
PythonMcu
=========
Mackie Host Controller written in Python

Copyright (c) 2011 Martin Zuther (http://www.mzuther.de/)

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

import sys

if __name__ == "__main__":
    # allow "PythonMcu" package imports when executing this module
    sys.path.append('../../../')

from PythonMcu.Hardware.MidiControllerTemplate import MidiControllerTemplate
from PythonMcu.Hardware.Novation.ZeroSlMk2_Constants import *


class ZeroSlMk2(MidiControllerTemplate):
    # Novation Digital Music System
    MIDI_MANUFACTURER_ID = (0x00, 0x20, 0x29)

    # MIDI device ID and initialisation of Novation ZeRO SL Mkii
    MIDI_DEVICE_ID = (0x03, 0x03, 0x12, 0x00, 0x04, 0x00)

    # MIDI channel of controller
    _MIDI_DEVICE_CHANNEL = 0

    # number of available channels strips on controller
    _CHANNEL_STRIPS = 8

    # number of available LCD pages on controller
    _LCD_PAGES = 4

    # number of available LCD characters per channel strip
    _LCD_FIELD_LENGTH = 9

    def __init__(self, midi_input, midi_output):
        MidiControllerTemplate.__init__(self, midi_input, midi_output)

        self.display_available = True
        self.seg7_available = False
        self.meter_bridge_available = False


    def connect(self):
        MidiControllerTemplate.connect(self)

        self._log('Starting "Ableton" mode...')

        self._lcd_strings = []
        for page in range(self._LCD_PAGES):
            self._lcd_strings.append([])
            for channel in range(self._CHANNEL_STRIPS):
                self._lcd_strings[page].append('')

        self.update_lcd(1, ['Initialis', 'ing'], False, False)
        self.update_lcd(2, ['Initialis', 'ing'], False, False)
        self.update_lcd(3, ['controlle', 'r'], False, False)
        self.update_lcd(4, ['controlle', 'r'], False, False)

        self.send_midi_sysex([0x01, 0x01])

        self.send_midi_cc(MIDI_CC_CLEAR_ALL_LEDS, 0x00)

        self._log('Connected.')


    def disconnect(self):
        self._log('Disconnecting...')

        self._log('Stopping "Ableton" mode...')

        self.send_midi_cc(MIDI_CC_CLEAR_ALL_LEDS, 0x00)

        self.send_midi_sysex([0x02, 0x02, 0x05])
        self.send_midi_sysex([0x01, 0x00])

        MidiControllerTemplate.disconnect(self)


    def _log(self, message):
        print '[Novation ZeRO SL MkII]  ' + message


    def send_midi_cc(self, cc_number, cc_value):
        MidiControllerTemplate.send_midi_cc( \
            self, self._MIDI_DEVICE_CHANNEL, cc_number, cc_value)


    def update_encoder_light(self, position, value):
        if self._encoder_positions[position] == value:
            return
        else:
            self._encoder_positions[position] = value

            self.send_midi_cc(MIDI_CC_ENCODER_LIGHTS + position, value)


    def update_lcd_raw(self, position, hex_codes):
        """
        send hex codes of maximum 72 bytes to controller LCD

        position 1: top row (left controller block)
        position 2: top row (right controller block)
        position 3: bottom row (left controller block)
        position 4: bottom row (right controller block)
        """
        sysex_data = [0x02, 0x01, 0x00, position, 0x04]

        # convert string
        for hex_code in hex_codes:
            # convert illegal characters to asterisk
            if (hex_code < 0x20) or (hex_code > 0x7F):
                hex_code = 0x2A
            sysex_data.append(hex_code)

        self.send_midi_sysex(sysex_data)


    def update_lcd(self, position, strings, preserve_space, shorten):
        """
        send string of maximum 72 bytes to controller LCD

        position 1: top row (left controller block)
        position 2: top row (right controller block)
        position 3: bottom row (left controller block)
        position 4: bottom row (right controller block)
        """
        assert(len(strings) <= self._CHANNEL_STRIPS)
        has_changed = False
        output = ''

        for channel in range(self._CHANNEL_STRIPS):
            if len(strings) <= channel:
                strings.append('')

            if self._lcd_strings[position - 1][channel] != strings[channel]:
                self._lcd_strings[position - 1][channel] = strings[channel]
                has_changed = True

        if not has_changed:
            return
        else:
            if preserve_space:
                field_length = self._LCD_FIELD_LENGTH - 1
            else:
                field_length = self._LCD_FIELD_LENGTH

        for channel in range(self._CHANNEL_STRIPS):
            output += strings[channel].ljust(field_length)[0:field_length]
            if preserve_space:
                output += ' '

        # convert string
        hex_codes = []
        for character in output:
            hex_codes.append(ord(character))

        self.update_lcd_raw(position, hex_codes)


if __name__ == "__main__":
    port_midi_input = 'ZeRO MkII: Port 1'
    port_midi_output = 'ZeRO MkII: Port 1'

    controller = ZeroSlMk2(port_midi_input, port_midi_output)
    controller.connect()

    import time
    time.sleep(3)

    controller.disconnect()
