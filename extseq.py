import time

import constants
import sequencermodel

sequencer_playing = True

class ExternalSeq(object):
    clock_ticking = False

    # step_counter is used to count the number of MIDI clock steps in order
    # to determine divisions of time from the external sequencer.
    # 24 MIDI clock messages = 1 quarter note
    #  6 MIDI clock messages = 1 sixteenth note
    step_counter = 0

    # step is used to count the current beat in the drum sequence
    step = 0

    def __call__(self, event, data=None):
        global sequencer_playing

        message, deltatime = event

        # Get start message
        if message[0] == 250:
            sequencer_playing = True

        # Get clock message
        if message[0] == 250 or message[0] == 248:
            # Check for sixtenth note
            if self.step_counter % 6 == 0:
                # Step through each button at the specified bpm
                for page in sequencermodel.sequencer_models:
                    for sm in page:
                        sm.start_note(self.step)

                time.sleep(constants.NOTE_LEN_SEC)

                for page in sequencermodel.sequencer_models:
                    for sm in page:
                        sm.stop_note()

                self.step = (self.step + 1) % constants.MAX_NUM_STEPS
                self.step_counter = 0

            self.step_counter = self.step_counter + 1

        # Get stop message
        elif message[0] == 252:
            sequencer_playing  = True
            self.clock_ticking = False
            self.step_counter  = 0
            self.step          = 0
