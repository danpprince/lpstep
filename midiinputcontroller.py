class MidiInputController(object):
    def __init__(self, sequencer_models):
        self.sequencer_models = sequencer_models

    def __call__(self, event, data=None):
        message, deltatime = event

        note_num = message[1]

        if message[0] == 144 and message[2] == 127:
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
