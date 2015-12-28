import rtmidi
import rtmidi.midiutil as midiutil
import time

import constants
from midiinputcontroller import MidiInputController
from sequencermodel import SequencerModel
import sequencermodel

bpm = 120


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
                        SequencerModel(   [6],  8, 41, drum_out),
                        SequencerModel(   [7],  8, 42, drum_out)]

    midi_input_controller = MidiInputController(sequencer_models) 

    midi_in.set_callback(midi_input_controller)

    sequencermodel.init_view()

    # Set the period in seconds for one sixteenth note
    period_sec = 60.0/bpm / 4

    step = 0

    if not constants.USE_EXT_SEQUENCER:
        while True:
            if sequencermodel.sequencer_playing:
                # Step through each button at the specified bpm
                for sm in sequencer_models:
                    sm.start_note(step)

                time.sleep(constants.NOTE_LEN_SEC)

                for sm in sequencer_models:
                    sm.stop_note()

                step = (step + 1) % constants.MAX_NUM_STEPS

                time.sleep(period_sec - constants.NOTE_LEN_SEC)
            else:
                step = 0
                time.sleep(0.1)

