import sequencermodel

class MidiInputController(object):
    def __init__(self, sequencer_models):
        self.sequencer_models = sequencer_models

    def __call__(self, event, data=None):
        message, deltatime = event

        # Get buttons on the grid
        if message[0] == 144 and message[2] == 127:
            note_num = message[1]

            col = note_num % 16
            row = note_num / 16

            if col == 8:
                # Mute the sequencer in this row
                for sm in self.sequencer_models:
                    if sm.in_range(row):
                        sm.mute_toggle()
            else:
                for sm in self.sequencer_models:
                    if sm.in_range(row):
                        sm.toggle(8*row + col)
                        
        # Get transport buttons
        elif message[0] == 176 and message[2] == 127:
            cc_num = message[1]

            if cc_num == 107:
                # Right arrow button pressed
                sequencermodel.toggle_playing()

            elif cc_num == 111:
                # Mixer button pressed
                sequencermodel.toggle_randomize()
