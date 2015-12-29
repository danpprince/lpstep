import rtmidi
import rtmidi.midiutil as midiutil
import time

import constants
import extseq
from extseq import ExternalSeq
from midiinputcontroller import MidiInputController
import sequencermodel
from sequencermodel import SequencerModel


if __name__ == '__main__':
    # Get inputs that contain the controller port name string
    midi_in, midi_in_name = midiutil.open_midiport(
            port=constants.CONTROLLER_PORT_NAME, 
            type_='input')
    print('Opening port \'{0}\' for input'.format(midi_in_name))

    # Get outputs that contain the drum out port name string
    drum_out, drum_out_name = midiutil.open_midiport(
            port=constants.DRUM_OUT_PORT_NAME, 
            type_='output')
    print('Opening port \'{0}\' for output'.format(drum_out_name))

    # Initialize sequencer models
    sequencer_models = [SequencerModel([0, 3], 32, 38, drum_out),
                        SequencerModel([4, 5], 16, 39, drum_out),
                        SequencerModel(   [6],  8, 41, drum_out),
                        SequencerModel(   [7],  8, 42, drum_out)]

    # Initialize a MIDI in object for the external sequencer if the option
    # has been enabled
    if constants.USE_EXT_CLOCK:
        clock_in, clock_in_name = midiutil.open_midiport(
                port=constants.EXT_CLOCK_PORT_NAME, 
                type_='input')
        print('Opening port \'{0}\' for clock'.format(clock_in_name))
        clock_in.ignore_types(timing=False)
        clock_in.set_callback(ExternalSeq(sequencer_models))

    midi_input_controller = MidiInputController(sequencer_models) 

    midi_in.set_callback(midi_input_controller)

    sequencermodel.init_view()

    # Set the period in seconds for one sixteenth note
    period_sec = 60.0/constants.INTERNAL_BPM / 4

    step = 0

    if not constants.USE_EXT_CLOCK:
        while True:
            if sequencermodel.sequencer_playing:
                # Step through each button at the specified bpm
                for sm in sequencermodel.get_current_seq_page():
                    sm.start_note(step)

                time.sleep(constants.NOTE_LEN_SEC)

                for sm in sequencermodel.get_current_seq_page():
                    sm.stop_note()

                step = (step + 1) % constants.MAX_NUM_STEPS

                time.sleep(period_sec - constants.NOTE_LEN_SEC)
            else:
                step = 0
                time.sleep(0.1)

    elif constants.USE_EXT_CLOCK:
        while True:
            time.sleep(1)
