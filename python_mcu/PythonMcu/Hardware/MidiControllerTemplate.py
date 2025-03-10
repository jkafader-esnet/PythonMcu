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

import sys

if __name__ == "__main__":
    # allow "PythonMcu" package imports when executing this module
    sys.path.append('../../../')

#from PythonMcu.Midi.MidiConnection import MidiConnection

import logging
logger = logging.getLogger("MCU Controller")
logging.basicConfig(level=logging.DEBUG)

class MidiControllerTemplate:
    MIDI_MANUFACTURER_ID = None
    MIDI_DEVICE_ID = None

    VPOT_MODE_SINGLE_DOT = 0x00
    VPOT_MODE_BOOST_CUT = 0x01
    VPOT_MODE_WRAP = 0x02
    VPOT_MODE_SPREAD = 0x03

    _LED_STATUS = {
        0x00: 'off',
        0x01: 'flashing',
        0x7F: 'on'
    }

    def __init__(self, midi_input_name, midi_output_name):
        self.callback_log = logger.debug

        # LCD has 2 rows with 56 characters each, fill with spaces
        self._lcd_characters = [' '] * 2
        self._lcd_overlay_characters = [' '] * 2

        for line in range(2):
            # noinspection PyTypeChecker
            self._lcd_characters[line] = [' '] * 56
            # noinspection PyTypeChecker
            self._lcd_overlay_characters[line] = [' '] * 56

        self._show_overlay = [False, False]

        self._log('Initialising MIDI ports...')
        self._midi_input_name = midi_input_name
        self._midi_output_name = midi_output_name
        self.midi = {}
        #self.midi = MidiConnection(self.callback_log, self.receive_midi)

        # Initialized by set_interconnector()
        self.interconnector = None

        self.display_lcd_available = True
        self.automated_faders_available = True
        self.display_7seg_available = True
        self.display_timecode_available = True
        self.meter_bridge_available = True

        self.display_7seg_characters = []
        for _ in range(4):
            self.display_7seg_characters.append(' ')

        self.display_timecode_characters = []
        for _ in range(20):
            self.display_timecode_characters.append(' ')

    @staticmethod
    def get_usage_hint():
        return ''

    def _log(self, message, repaint=False):
        self.callback_log('[Controller Template]  ' + message)

    # --- initialisation ---
    def set_interconnector(self, host):
        self.interconnector = host

    def unset_interconnector(self):
        self.interconnector = None

    def connect(self):
        self._log('Opening MIDI ports...')
        self.midi.connect(self._midi_input_name, self._midi_output_name)

    def disconnect(self):
        self._log('Closing MIDI ports...')
        self.midi.disconnect()
        self._log('Disconnected.')

    def go_online(self):
        self._log('Mackie Host Control went online...')

    def go_offline(self):
        self._log('Mackie Host Control went offline...')

    # --- abilities of hardware controller ---
    def has_display_7seg(self):
        return self.display_7seg_available

    def has_display_lcd(self):
        return self.display_lcd_available

    def has_display_timecode(self):
        return self.display_timecode_available

    def has_automated_faders(self):
        return self.automated_faders_available

    def has_meter_bridge(self):
        return self.meter_bridge_available

    # --- MIDI processing ---
    def process_midi_input(self):
        self.midi.process_input_buffer()

    def receive_midi(self, status, message):
        print(status, message)
        message_string = ['status %02X: ' % status]
        for byte in message:
            message_string.append('%02X' % byte)
        self._log(' '.join(message_string))

    def send_midi_control_change(self, channel, cc_number, cc_value):
        self.midi.send_control_change(channel, cc_number, cc_value)

    def send_midi_sysex(self, data):
        assert isinstance(data, list)

        header = []
        header.extend(self.MIDI_MANUFACTURER_ID)
        header.extend(self.MIDI_DEVICE_ID)

        self.midi.send_sysex(header, data)

    @staticmethod
    def get_preferred_midi_input():
        return ''

    @staticmethod
    def get_preferred_midi_output():
        return ''

    # --- registration of MIDI controls ---
    def register_control(self, mcu_command, midi_switch, midi_led=None):
        if midi_led:
            self.interconnector.register_control(mcu_command, midi_switch, midi_led)
        else:
            self.interconnector.register_control(mcu_command, midi_switch, midi_switch)

    def withdraw_control(self, midi_switch):
        self.interconnector.withdraw_control(midi_switch)

    def withdraw_all_controls(self):
        self.interconnector.withdraw_all_controls()

    # --- handling of Mackie Control commands ---
    def set_lcd(self, position, hex_codes, update=True):
        for hex_code in hex_codes:
            # wrap display and determine position
            position %= 112
            (line, pos) = divmod(position, 56)

            # convert illegal characters to asterisk
            if (hex_code < 0x20) or (hex_code > 0x7F):
                self._lcd_characters[line][pos] = '*'
            else:
                self._lcd_characters[line][pos] = chr(hex_code)

            position += 1

        if update:
            self.update_lcd()

    def set_led(self, internal_id, led_status):
        pass

    def set_display_7seg(self, position, character_code):
        character = self._decode_7seg_character(character_code)
        position = 23 - (position * 2)

        self.display_7seg_characters[position - 1] = character[0]
        self.display_7seg_characters[position] = character[1]

        string_7seg = ''.join(self.display_7seg_characters)
        self._log('7 segment display NOT set to "%s".' % string_7seg)

    @staticmethod
    def _decode_7seg_character(character_code):
        if character_code >= 0x40:
            character_code = character_code - 0x40
            dot = '.'
        else:
            dot = ' '

        if character_code < 0x20:
            return chr(character_code + 0x40), dot

        return chr(character_code), dot

    def set_display_timecode(self, position, character_code):
        character = self._decode_7seg_character(character_code)
        position = 19 - (position * 2)

        self.display_timecode_characters[position - 1] = character[0]
        self.display_timecode_characters[position] = character[1]

        # please note that the logged timecode is not necessarily
        # correct: it will only be dumped when the display's last
        # character has been updated -- there may be other updates
        # still pending!
        if position == 19:
            string_timecode = ''.join(self.display_timecode_characters)
            self._log('timecode display NOT set to "%s".' % string_timecode)

    def set_peak_level(self, meter_id, meter_level):
        if meter_level == 0x0F:
            self._log('Meter #%d overload NOT cleared.' % meter_id)
        elif meter_level == 0x0F:
            self._log('Meter #%d NOT set to overload.' % meter_id)
        else:
            self._log('Meter #%d NOT set to %03d%%.' % (meter_id, meter_level * 10))

    def fader_moved(self, fader_id, fader_position):
        self._log('Hardware fader #%d NOT moved to position %04d.' % (fader_id, fader_position))

    def set_vpot_led_ring(self, vpot_id, vpot_center_led, vpot_mode, vpot_position):
        self._log('V-Pot #%d LED ring NOT set to position %02d (mode %d).' % (vpot_id, vpot_position, vpot_mode))

    def faders_to_minimum(self):
        self._log('Hardware faders NOT set to minimum.')

    def all_leds_off(self):
        self._log('Hardware LEDs NOT set to "off".')

    # --- LCD and menu handling
    def update_lcd(self):
        pass

    def get_lcd_characters(self, line):
        line %= 2

        if self._show_overlay[line]:
            return self._lcd_overlay_characters[line]

        return self._lcd_characters[line]

    def show_menu(self, line, menu_strings):
        assert len(menu_strings) == 8

        menu_string_temp = ''
        for menu_string in menu_strings:
            menu_string_temp += menu_string.center(7)[:7]

        menu_characters = list(menu_string_temp)
        self.show_overlay(line, menu_characters)

    def hide_menu(self, line):
        self.hide_overlay(line)

    def show_overlay(self, line, overlay_characters):
        line %= 2
        assert len(overlay_characters) == 56

        self._show_overlay[line] = True
        self._lcd_overlay_characters[line] = overlay_characters
        self.update_lcd()

    def hide_overlay(self, line):
        line %= 2

        self._show_overlay[line] = False
        self.update_lcd()
