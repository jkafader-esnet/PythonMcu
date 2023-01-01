patches = {
    b"Pianoteq": {
        "groups": [
            {"name": "NO",    "layout": "blank" }, 
            {"name": "CTRLS", "layout": "blank" },
            {"name": "JUST",  "layout": "blank" },
            {"name": "PLAY",  "layout": "blank" },
        ],
        "shift": [
            {"name": "NO",    "layout": "blank" }, 
            {"name": "CTRLS", "layout": "blank" },
            {"name": "JUST",  "layout": "blank" },
            {"name": "PLAY",  "layout": "blank" },
        ],
    },
    b"B3 Organ": {
        # concept: "groups" allow us to specify which order and which layout per group
        "groups": [
            {"name": "DRAW",    "layout": "track"}, 
            {"name": "SOUND", "layout": "track"},
            {"name": "",        "layout": "blank" },
            {"name": "OVRDRV",     "layout": "pan" }
        ],
        # concept: "shift" allows us to re-layout soft buttons when shift is held
        # concept: "shift" moves user to shift menu 1 if group menu 1 is active
        "shift": [
            {"name": "DRAW2",   "layout": "track"}, 
            {"name": "SOUND", "layout": "track"},
            {"name": "",        "layout": "blank" },
            {"name": "OVRDRV",     "layout": "pan" }
        ],
        "F0": {"name": "Draw [16']",     "long_name": "16' Drawbar", "groups": ["DRAW"         ], "set": "vtrack_setter", "param": { "track": 0, "invert": True}, "value": 91 },
        "F1": {"name": "Draw [5  1/3']", "long_name": "5 1/3' Drawbar", "groups": ["DRAW", "DRAW2"], "set": "vtrack_setter", "param": { "track": 1, "invert": True}, "value": 91 },
        "F2": {"name": "Draw [8']",      "long_name": "8' Drawbar", "groups": ["DRAW", "DRAW2"], "set": "vtrack_setter", "param": { "track": 2, "invert": True}, "value": 91 },
        "F3": {"name": "Draw [4']",      "long_name": "4' Drawbar", "groups": ["DRAW", "DRAW2"], "set": "vtrack_setter", "param": { "track": 3, "invert": True}, "value": 91 },
        "F4": {"name": "Draw [2  2/3']", "long_name": "2 2/3' Drawbar", "groups": ["DRAW", "DRAW2"], "set": "vtrack_setter", "param": { "track": 4, "invert": True}, "value": 91 },
        "F5": {"name": "Draw [2']",      "long_name": "2' Drawbar", "groups": ["DRAW", "DRAW2"], "set": "vtrack_setter", "param": { "track": 5, "invert": True}, "value": 91 },
        "F6": {"name": "Draw [1  3/5']", "long_name": "1 3/5' Drawbar", "groups": ["DRAW", "DRAW2"], "set": "vtrack_setter", "param": { "track": 6, "invert": True}, "value": 91 },
        "F7": {"name": "Draw [1  1/3']", "long_name": "1 1/3' Drawbar", "groups": ["DRAW", "DRAW2"], "set": "vtrack_setter", "param": { "track": 7, "invert": True}, "value": 91 },
        "F8": {"name": "Draw [1']",      "long_name": "1' Drawbar", "groups": [        "DRAW2"], "set": "vtrack_setter", "param": { "track": 8, "invert": True}, "value": 91 },
        # pressing shift brings 1' into view

        "F9": {"name": "Perc Decay",       "groups": ["SOUND",], "set": "vtrack_setter", "param": { "track": 9, "invert": False }, "value": 91 },
        "F10": {"name": "Perc Harmonic",   "groups": ["SOUND",], "set": "vtrack_setter", "param": { "track": 10, "invert": False }, "value": 91 },
        "F11": {"name": "Perc Volume",     "groups": ["SOUND",], "set": "vtrack_setter", "param": { "track": 11, "invert": False }, "value": 91 },
        "F12": {"name": "Pedal Spkr Func", "groups": ["SOUND",], "set": "vtrack_setter", "param": { "track": 12, "invert": False }, "value": 91 },
        "F13": {"name": "Rotary Speed",    "groups": ["SOUND",], "set": "vtrack_setter", "param": { "track": 13, "invert": False }, "value": 91 },

        "P0": {"name": "Character", "long_name": "Ovrdrv Character", "groups": ["OVRDRV",], "set": "vpot_setter", "param": { "track": 0, }, "value": 91 },
        "P1": {"name": "Gain In",   "long_name": "Ovrdrv In Gain",   "groups": ["OVRDRV",], "set": "vpot_setter", "param": { "track": 1, }, "value": 91 },
        "P2": {"name": "GainOut",   "long_name": "Ovrdrv Out Gain",  "groups": ["OVRDRV",], "set": "vpot_setter", "param": { "track": 2, }, "value": 91 },
        # groups allow us to show the same vbuttons in all 4 menus for the organ.
        "B0": {"name": "Percussion",    "groups": ["DRAW", "DRAW2", "SOUND", "OVRDRV"], "set": "vbutton_setter", "param": {"track": 0}, "value": 0 },
        "B1": {"name": "Overdrive",     "groups": ["DRAW", "DRAW2", "SOUND", "OVRDRV"], "set": "vbutton_setter", "param": {"track": 1}, "value": 127 },
        "B2": {"name": "Vibrato",       "groups": ["DRAW", "DRAW2", "SOUND", "OVRDRV"], "set": "vbutton_setter", "param": {"track": 2}, "value": 127 },
        "B3": {"name": "Vibrato 1",     "groups": ["DRAW", "DRAW2", "SOUND", "OVRDRV"], "set": "vbutton_setter", "param": {"track": 3, "exclusive_with": [4, 5, 6] }, "value": 127 },
        "B4": {"name": "Vibrato 2",     "groups": ["DRAW", "DRAW2", "SOUND", "OVRDRV"], "set": "vbutton_setter", "param": {"track": 4, "exclusive_with": [3, 5, 6] }, "value": 0 },
        "B5": {"name": "Chorus 1",      "groups": ["DRAW", "DRAW2", "SOUND", "OVRDRV"], "set": "vbutton_setter", "param": {"track": 5, "exclusive_with": [3, 4, 6] }, "value": 0 },
        "B6": {"name": "Chorus 2",      "groups": ["DRAW", "DRAW2", "SOUND", "OVRDRV"], "set": "vbutton_setter", "param": {"track": 6, "exclusive_with": [3, 4, 5] }, "value": 0 },
        "B7": {"name": "Leslie Spin",   "groups": ["DRAW", "DRAW2", "SOUND", "OVRDRV"], "set": "vbutton_setter", "param": {"track": 7}, "value": 0 },
    },
    b"Minimoog": {
        "groups": [
            {"name": "OSC", "layout": "track"}, 
            {"name": "ENV", "layout": "track"},
            {"name": "",    "layout": "blank" },
            {"name": "FLT", "layout": "pan" }
        ],
        "shift": [
            {"name": "OSC", "layout": "track"}, 
            {"name": "ENV", "layout": "track"},
            {"name": "",    "layout": "blank" },
            {"name": "FLT", "layout": "pan" }
        ],
        "F0": {"name": "Osc1 Octave",      "groups": ["OSC",],     "set": "vtrack_setter", "param": { "track": 0 },  "value": 91 },
        "F1": {"name": "Osc1 Shape",       "groups": ["OSC",],     "set": "vtrack_setter", "param": { "track": 1 },  "value": 91 },
        "F2": {"name": "Osc2 Octave",      "groups": ["OSC",],     "set": "vtrack_setter", "param": { "track": 2 },  "value": 91 },
        "F3": {"name": "Osc2 Fine",        "groups": ["OSC",],     "set": "vtrack_setter", "param": { "track": 3 },  "value": 91 },
        "F4": {"name": "Osc2 Shape",       "groups": ["OSC",],     "set": "vtrack_setter", "param": { "track": 4 },  "value": 91 },
        "F5": {"name": "Osc3 Octave",      "groups": ["OSC",],     "set": "vtrack_setter", "param": { "track": 5 },  "value": 91 },
        "F6": {"name": "Osc3 Fine",        "groups": ["OSC",],     "set": "vtrack_setter", "param": { "track": 6 },  "value": 91 },
        "F7": {"name": "Osc3 Shape",       "groups": ["OSC",],     "set": "vtrack_setter", "param": { "track": 7 },  "value": 91 },
        "F8": {"name": "VCA  Attack",      "groups": ["ENV",],     "set": "vtrack_setter", "param": { "track": 8 },  "value": 91 },
        "F9": {"name": "VCA  Decay",       "groups": ["ENV",],     "set": "vtrack_setter", "param": { "track": 9 },  "value": 91 },
        "F10": {"name": "VCA  Sustain",    "groups": ["ENV",],     "set": "vtrack_setter", "param": { "track": 10 }, "value": 91 },
        "F11": {"name": "VCA  Release",    "groups": ["ENV",],     "set": "vtrack_setter", "param": { "track": 11 }, "value": 91 },
        "F12": {"name": "VCF  Attack",     "groups": ["ENV",],     "set": "vtrack_setter", "param": { "track": 12 }, "value": 91 },
        "F13": {"name": "VCF  Decay",      "groups": ["ENV",],     "set": "vtrack_setter", "param": { "track": 13 }, "value": 91 },
        "F14": {"name": "VCF  Sustain",    "groups": ["ENV",],     "set": "vtrack_setter", "param": { "track": 14 }, "value": 91 },
        "F15": {"name": "VCF  Release",    "groups": ["ENV",],     "set": "vtrack_setter", "param": { "track": 15 }, "value": 91 },
        "P0": {"name": "Cutoff",    "groups": ["FLT",], "set": "vpot_setter", "param": { "track": 0 }, "value": 64 },
        "P1": {"name": "Resonance", "groups": ["FLT",], "set": "vpot_setter", "param": { "track": 1 }, "value": 64 },
        "P2": {"name": "EnvAmt",    "groups": ["FLT",], "set": "vpot_setter", "param": { "track": 2 }, "value": 64 },
        "P3": {"name": "Glide",     "groups": ["FLT",], "set": "vpot_setter", "param": { "track": 3 }, "value": 64 },
        "P4": {"name": "NSE LVL",     "groups": ["FLT",], "set": "vpot_setter", "param": { "track": 4 }, "value": 64 },
        "P5": {"name": "OSC1LVL",    "groups": ["FLT",], "set": "vpot_setter", "param": { "track": 5 }, "value": 64 },
        "P6": {"name": "OSC2LVL",    "groups": ["FLT",], "set": "vpot_setter", "param": { "track": 6 }, "value": 64 },
        "P7": {"name": "OSC3LVL",    "groups": ["FLT",], "set": "vpot_setter", "param": { "track": 7 }, "value": 64 },
        "B0": {"name": "Oscillator Mod",   "groups": ["OSC", "ENV", "FLT"], "set": "vbutton_setter", "param": { "track": 0 }, "value": 0 },
        "B1": {"name": "Filter Mod",       "groups": ["OSC", "ENV", "FLT"], "set": "vbutton_setter", "param": { "track": 1 }, "value": 0 },
        "B2": {"name": "Keyboard->Osc1",   "groups": ["OSC", "ENV", "FLT"], "set": "vbutton_setter", "param": { "track": 2 }, "value": 127 },
        "B3": {"name": "Keyboard->Osc2",   "groups": ["OSC", "ENV", "FLT"], "set": "vbutton_setter", "param": { "track": 3 }, "value": 127 },
        "B4": {"name": "Keyboard->Osc3",   "groups": ["OSC", "ENV", "FLT"], "set": "vbutton_setter", "param": { "track": 4 }, "value": 0 },
        "B5": {"name": "Noise Color",      "groups": ["OSC", "ENV", "FLT"], "set": "vbutton_setter", "param": { "track": 5 }, "value": 0 },
        "B6": {"name": "A-440 Sync",       "groups": ["OSC", "ENV", "FLT"], "set": "vbutton_setter", "param": { "track": 6 }, "value": 127 },
        "B7": {"name": "Main Output",      "groups": ["OSC", "ENV", "FLT"], "set": "vbutton_setter", "param": { "track": 7 }, "value": 127 },
    },
    b"Oberheim": {
        "groups": [
            {"name": "OSC", "layout": "track"}, 
            {"name": "MOD", "layout": "track"},
            {"name": "ENV", "layout": "track"},
            {"name": "FLT", "layout": "pan" }
        ],
        "shift": [
            {"name": "OSC",   "layout": "track"},
            {"name": "VARY1", "layout": "pan" },
            {"name": "VARY2", "layout": "track"},
            {"name": "FLT",   "layout": "pan" },
        ],

        "F0": {"name": "Osc1 Freq",    "groups": ["OSC",], "set": "vtrack_setter", "param": {"track": 0 }, "value": 10 },
        "F1": {"name": "Osc1 Level",   "groups": ["OSC",], "set": "vtrack_setter", "param": {"track": 1 }, "value": 10 },
        "F2": {"name": "Osc2 Freq",    "groups": ["OSC",], "set": "vtrack_setter", "param": {"track": 2 }, "value": 10 },
        "F3": {"name": "Osc2 Level",   "groups": ["OSC",], "set": "vtrack_setter", "param": {"track": 3 }, "value": 10 },
        "F4": {"name": "Detune",       "groups": ["OSC",], "set": "vtrack_setter", "param": {"track": 4 }, "value": 10 },
        "F5": {"name": "Pulse Width",  "groups": ["OSC",], "set": "vtrack_setter", "param": {"track": 5 }, "value": 10 },

        "F8":  {"name": "LFO Rate",     "groups": ["MOD"], "set": "vtrack_setter", "param": {"track": 8 }, "value": 10 },
        "F9":  {"name": "Freq Mod Amt", "groups": ["MOD"], "set": "vtrack_setter", "param": {"track": 9 }, "value": 10 },
        "F10": {"name": "PW Mod Amt",   "groups": ["MOD"], "set": "vtrack_setter", "param": {"track": 10 }, "value": 10 },

        "F11": {"name": "Amp Attack",   "groups": ["ENV"], "set": "vtrack_setter", "param": {"track": 11}, "value": 10 },
        "F12": {"name": "Amp Decay",    "groups": ["ENV"], "set": "vtrack_setter", "param": {"track": 12}, "value": 10 },
        "F13": {"name": "Amp Sustain",  "groups": ["ENV"], "set": "vtrack_setter", "param": {"track": 13}, "value": 10 },
        "F14": {"name": "Amp Release",  "groups": ["ENV"], "set": "vtrack_setter", "param": {"track": 14}, "value": 10 },
        "F15": {"name": "Filt Attack",  "groups": ["ENV"], "set": "vtrack_setter", "param": {"track": 15}, "value": 10 },
        "F16": {"name": "Filt Decay",   "groups": ["ENV"], "set": "vtrack_setter", "param": {"track": 16}, "value": 10 },
        "F17": {"name": "Filt Sustain", "groups": ["ENV"], "set": "vtrack_setter", "param": {"track": 17}, "value": 10 },
        "F18": {"name": "Filt Release", "groups": ["ENV"], "set": "vtrack_setter", "param": {"track": 18}, "value": 10 },

        "P19":  {"name": "PanVox1",  "groups": ["VARY1",], "set": "vpot_setter", "param": {"track": 19 }, "value": 10 },
        "P20":  {"name": "PanVox2",  "groups": ["VARY1",], "set": "vpot_setter", "param": {"track": 20 }, "value": 10 },
        "P21":  {"name": "PanVox3",  "groups": ["VARY1",], "set": "vpot_setter", "param": {"track": 21 }, "value": 10 },
        "P22":  {"name": "PanVox4",  "groups": ["VARY1",], "set": "vpot_setter", "param": {"track": 22 }, "value": 10 },
        "P23":  {"name": "PanVox5",  "groups": ["VARY1",], "set": "vpot_setter", "param": {"track": 23 }, "value": 10 },
        "P24":  {"name": "PanVox6",  "groups": ["VARY1",], "set": "vpot_setter", "param": {"track": 24 }, "value": 10 },
        "P25":  {"name": "PanVox7",  "groups": ["VARY1",], "set": "vpot_setter", "param": {"track": 25 }, "value": 10 },
        "P26":  {"name": "PanVox8",  "groups": ["VARY1",], "set": "vpot_setter", "param": {"track": 26 }, "value": 10 },

        "F27": {"name": "Filt Slop",     "groups": ["VARY2",], "set": "vtrack_setter", "param": {"track": 27 }, "value": 10 },
        "F28": {"name": "Glide Slop",    "groups": ["VARY2",], "set": "vtrack_setter", "param": {"track": 28 }, "value": 10 },
        "F29": {"name": "Env Slop",      "groups": ["VARY2",], "set": "vtrack_setter", "param": {"track": 29 }, "value": 10 },
        "F30": {"name": "Osc Bright",    "groups": ["VARY2",], "set": "vtrack_setter", "param": {"track": 30 }, "value": 10 },
        "F31": {"name": "Pitch Env",     "groups": ["VARY2",], "set": "vtrack_setter", "param": {"track": 31 }, "value": 10 },

        "P0": {"name": "Cutoff",      "groups": ["FLT"], "set": "vpot_setter", "param": {"track": 0 }, "value": 10 },
        "P1": {"name": "Resonance",   "groups": ["FLT"], "set": "vpot_setter", "param": {"track": 1 }, "value": 10 },
        "P2": {"name": "Flt Env Amt", "groups": ["FLT"], "set": "vpot_setter", "param": {"track": 2 }, "value": 10 },
        "P3": {"name": "Flt Env Amt", "groups": ["FLT"], "set": "vpot_setter", "param": {"track": 3 }, "value": 10 },


        "B0": {"name": "Osc1 Saw",   "groups": ["OSC",], "set": "vbutton_setter", "param": {"track": 0}, "value": 127 },
        "B1": {"name": "Osc1 Pulse", "groups": ["OSC",], "set": "vbutton_setter", "param": {"track": 1}, "value": 127 },
        "B2": {"name": "Osc2 Saw",   "groups": ["OSC",], "set": "vbutton_setter", "param": {"track": 2}, "value": 127 },
        "B3": {"name": "Osc2 Pulse", "groups": ["OSC",], "set": "vbutton_setter", "param": {"track": 3}, "value": 127 },
        "B4": {"name": "Osc Sync",   "groups": ["OSC",], "set": "vbutton_setter", "param": {"track": 4}, "value": 127 },
        "B5": {"name": "Osc Step",   "groups": ["OSC",], "set": "vbutton_setter", "param": {"track": 5}, "value": 127 },
        "B7": {"name": "Unison",     "groups": ["OSC",], "set": "vbutton_setter", "param": {"track": 7}, "value": 127 },

        "B8":  {"name": "LFO Sin",       "groups": ["MOD","VARY1"], "set": "vbutton_setter", "param": {"track": 8}, "value": 127 },
        "B9":  {"name": "LFO Pulse",     "groups": ["MOD","VARY1"], "set": "vbutton_setter", "param": {"track": 9}, "value": 127 },
        "B10": {"name": "LFO S&H",       "groups": ["MOD","VARY1"], "set": "vbutton_setter", "param": {"track": 10}, "value": 127 },
        "B11": {"name": "Freq Mod Osc1", "groups": ["MOD","VARY1"], "set": "vbutton_setter", "param": {"track": 11}, "value": 127 },
        "B12": {"name": "Freq Mod Osc2", "groups": ["MOD","VARY1"], "set": "vbutton_setter", "param": {"track": 12}, "value": 127 },
        "B13": {"name": "Freq Mod Filt", "groups": ["MOD","VARY1"], "set": "vbutton_setter", "param": {"track": 13}, "value": 127 },
        "B14": {"name": "PW Mod Osc1",   "groups": ["MOD","VARY1"], "set": "vbutton_setter", "param": {"track": 14}, "value": 127 },
        "B15": {"name": "PW Mod Osc2",   "groups": ["MOD","VARY1"], "set": "vbutton_setter", "param": {"track": 15}, "value": 127 },

        "B16": {"name": "LFO Saw",       "groups": ["ENV","VARY2"], "set": "vbutton_setter", "param": {"track": 16}, "value": 127 },
        "B17": {"name": "LFO Pulse",     "groups": ["ENV","VARY2"], "set": "vbutton_setter", "param": {"track": 17}, "value": 127 },
        "B18": {"name": "LFO S&H",       "groups": ["ENV","VARY2"], "set": "vbutton_setter", "param": {"track": 18}, "value": 127 },
        "B19": {"name": "Freq Mod Osc1", "groups": ["ENV","VARY2"], "set": "vbutton_setter", "param": {"track": 19}, "value": 127 },
        "B20": {"name": "Freq Mod Osc2", "groups": ["ENV","VARY2"], "set": "vbutton_setter", "param": {"track": 20}, "value": 127 },
        "B21": {"name": "Freq Mod Filt", "groups": ["ENV","VARY2"], "set": "vbutton_setter", "param": {"track": 21}, "value": 127 },
        "B22": {"name": "PW Mod Osc1",   "groups": ["ENV","VARY2"], "set": "vbutton_setter", "param": {"track": 22}, "value": 127 },
        "B23": {"name": "PW Mod Osc2",   "groups": ["ENV","VARY2"], "set": "vbutton_setter", "param": {"track": 23}, "value": 127 },
    },
    b"Wurlitzer": {
        "groups": [
            {"name": "", "layout": "blank" },
            {"name": "", "layout": "blank" },
            {"name": "", "layout": "blank" },
            {"name": "FX", "layout": "pan"},
        ],
        "shift": [
            {"name": "", "layout": "blank" },
            {"name": "", "layout": "blank" },
            {"name": "", "layout": "blank" },
            {"name": "FX", "layout": "pan"},
        ],
        "P0": {"name": "Dist", "groups": "FX", "set": "vpot_setter", "param": { "track": 0 }, "value": 40 },
        "P1": {"name": "VibAmt",   "groups": "FX", "set": "vpot_setter", "param": { "track": 1 }, "value": 40 },
        "P2": {"name": "VibRate",  "groups": "FX", "set": "vpot_setter", "param": { "track": 2 }, "value": 40 },
    },
    b"Solina": {
        "groups": [
            { "name": "4'", "layout": "track" },
            { "name": "8'", "layout": "track" },
            { "name": "ENV", "layout": "track" },
            { "name": "FX", "layout": "pan" },
        ],
        "shift": [
            { "name": "4'", "layout": "track" },
            { "name": "8'", "layout": "track" },
            { "name": "ENV", "layout": "track" },
            { "name": "FX", "layout": "pan" },
        ],
        "F0": {"name": "Osc Detune",     "groups": ["4'","8'"], "set": "vtrack_setter", "param": {"track": 0}, "value": 127 },
        "F1": {"name": "Osc PWM Depth",  "groups": ["4'","8'"], "set": "vtrack_setter", "param": {"track": 1}, "value": 127 },
        "F2": {"name": "Osc PWM Freq",   "groups": ["4'","8'"], "set": "vtrack_setter", "param": {"track": 2}, "value": 127 },
        "F3": {"name": "Osc Enhance 4'", "groups": ["4'",], "set": "vtrack_setter", "param": {"track": 3}, "value": 127 },
        "F4": {"name": "Osc HP 4'",      "groups": ["4'",], "set": "vtrack_setter", "param": {"track": 4}, "value": 127 },
        "F5": {"name": "Filt HP 4'",     "groups": ["4'",], "set": "vtrack_setter", "param": {"track": 5}, "value": 127 },
        "F6": {"name": "Filt LP 4'",     "groups": ["4'",], "set": "vtrack_setter", "param": {"track": 6}, "value": 127 },
        "F7": {"name": "Mix Gain 4'",    "groups": ["4'",], "set": "vtrack_setter", "param": {"track": 7}, "value": 127 },

        "F8": {"name": "Osc Enhance 8'",  "groups": ["8'",], "set": "vtrack_setter", "param": {"track": 8}, "value": 127 },
        "F9": {"name": "Osc HP 8'",       "groups": ["8'",], "set": "vtrack_setter", "param": {"track": 9}, "value": 127 },
        "F10": {"name": "Filt HP 8'",     "groups": ["8'",], "set": "vtrack_setter", "param": {"track": 10}, "value": 127 },
        "F11": {"name": "Filt LP 8'",     "groups": ["8'",], "set": "vtrack_setter", "param": {"track": 11}, "value": 127 },
        "F12": {"name": "Mix Gain 8'",    "groups": ["8'",], "set": "vtrack_setter", "param": {"track": 12}, "value": 127 },

        "F13": {"name": "Env Attack",  "groups": ["ENV",], "set": "vtrack_setter", "param": {"track": 13}, "value": 127 },
        "F14": {"name": "Env Hold",    "groups": ["ENV",], "set": "vtrack_setter", "param": {"track": 14}, "value": 127 },
        "F15": {"name": "Env Decay",   "groups": ["ENV",], "set": "vtrack_setter", "param": {"track": 15}, "value": 127 },
        "F16": {"name": "Env Sustain", "groups": ["ENV",], "set": "vtrack_setter", "param": {"track": 16}, "value": 127 },
        "F17": {"name": "Env Release", "groups": ["ENV",], "set": "vtrack_setter", "param": {"track": 17}, "value": 127 },

        "P0": {"name": "Chorus",         "groups": ["FX",], "set": "vpot_setter", "param": {"track": 0}, "value": 127 },
        "P1": {"name": "Chorus Depth",   "groups": ["FX",], "set": "vpot_setter", "param": {"track": 1}, "value": 127 },
        "P2": {"name": "Chorus Rate 1",  "groups": ["FX",], "set": "vpot_setter", "param": {"track": 2}, "value": 127 },
        "P3": {"name": "Chorus Depth 1", "groups": ["FX",], "set": "vpot_setter", "param": {"track": 3}, "value": 127 },
        "P4": {"name": "Chorus Rate 2",  "groups": ["FX",], "set": "vpot_setter", "param": {"track": 4}, "value": 127 },
        "P5": {"name": "Chorus Depth 2", "groups": ["FX",], "set": "vpot_setter", "param": {"track": 5}, "value": 127 },
        "P6": {"name": "Chorus Model",   "groups": ["FX",], "set": "vpot_setter", "param": {"track": 6}, "value": 127 },
        "P7": {"name": "Polyphony",      "groups": ["FX",], "set": "vpot_setter", "param": {"track": 7}, "value": 127 },
    },
} 
