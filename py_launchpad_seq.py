import rtmidi
import rtmidi.midiutil as midiutil
import time

from midiinputcontroller import MidiInputController
from sequencermodel import SequencerModel

n_col = 8
n_row = 4

bpm = 110


if __name__ == '__main__':
    # Get inputs that contain the string 'Launchpad'
    midi_in, midi_in_name = midiutil.open_midiport(port='Launchpad', type_='input')
    print('Opening port \'{0}\' for input'.format(midi_in_name))

    # Get outputs that contain the string 'loopMIDI'
    drum_out, drum_out_name = midiutil.open_midiport(port='loopMIDI', type_='output')
    print('Opening port \'{0}\' for output'.format(drum_out_name))

    # Initialize sequencer models
    sequencer_models = [SequencerModel([0, 3], 32, 38, drum_out),
                        SequencerModel([4, 5], 16, 39, drum_out),
                        SequencerModel([6, 7], 16, 42, drum_out)]

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
