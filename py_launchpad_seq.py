import rtmidi
import rtmidi.midiutil as midiutil
import time

from sequencermodel import SequencerModel

n_col = 8
n_row = 4

bpm = 110


class MidiInputController(object):
    def __init__(self, sequencer_models):
        self.sequencer_models = sequencer_models

    def __call__(self, event, data=None):
        message, deltatime = event

        note_num = message[1]

        if message[0] == 144 and message[2] == 127:
            col = note_num % 16
            row = note_num / 16

            if col == 8 and row == 7:
                # Reset the grid
                for sm in self.sequencer_models:
                    sm.clear()
            else:
                for sm in self.sequencer_models:
                    if sm.in_range(row):
                        sm.toggle(8*row + col)

if __name__ == '__main__':
    # Get inputs that contain the string 'Launchpad'
    midi_in, midi_in_name = midiutil.open_midiport(port='Launchpad', type_='input')
    print('Opening port \'{0}\' for input'.format(midi_in_name))

    # Get outputs that contain the string 'loopMIDI'
    drum_out, drum_out_name = midiutil.open_midiport(port='loopMIDI', type_='output')
    print('Opening port \'{0}\' for output'.format(drum_out_name))

    # Initialize sequencer models
    sequencer_models = []
    for i in range(2):
        s_m = SequencerModel([0+4*i, 3+4*i], 32, 38+i, drum_out)
        sequencer_models.append(s_m)

    midi_input_controller = MidiInputController(sequencer_models) 

    midi_in.set_callback(midi_input_controller)

    # Set the period in seconds for one sixteenth note
    period_sec = 1.0/bpm * 60 / 8

    step = 0
    num_steps = 32

    while True:
        # Step through each button at the specified bpm

        for sm in sequencer_models:
            sm.tick(step, 1)

        time.sleep(0.1)

        for sm in sequencer_models:
            sm.tick(step, 0)

        step = (step + 1) % num_steps

        time.sleep(period_sec)
