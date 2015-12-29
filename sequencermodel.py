import random
import rtmidi.midiutil as midiutil

import constants
import lpview
import notestates

sequencer_playing = False
randomize         = False

input_velocity = notestates.NOTE_VEL_HIGH
global_view = None

current_page = 0

def get_current_seq_page():
    return sequencer_models[current_page]

def init_view():
    global global_view
    global_view = lpview.GlobalLpView(input_velocity)

def increase_velocity():
    global input_velocity
    if input_velocity == notestates.NOTE_VEL_LOW:
        input_velocity = notestates.NOTE_VEL_HIGH
    global_view.display_velocity(input_velocity)

def decrease_velocity():
    global input_velocity
    if input_velocity == notestates.NOTE_VEL_HIGH:
        input_velocity = notestates.NOTE_VEL_LOW
    global_view.display_velocity(input_velocity)

def toggle_playing():
    global sequencer_playing
    sequencer_playing = not sequencer_playing
    global_view.display_playing(sequencer_playing)
    
def select_seq_page(page_num):
    global current_page
    current_page = page_num
    global_view.display_page(page_num)

    for sm in get_current_seq_page():
        sm.display()
    
def toggle_randomize():
    global randomize
    randomize = not randomize
    global_view.display_randomize(randomize)
    
class SequencerModel(object):
    playing_step = None

    def __init__(self, rows, sequence_length, note_num, drum_out):
        self.rows = rows
        self.sequence_length = sequence_length
        self.note_num = note_num
        self.drum_out = drum_out

        self.step_states = [notestates.NOTE_OFF for i in range(sequence_length)]

        self.muted = False

        self.view = lpview.LpView(rows)

    def set_view(self, view):
        self.view = view

    def toggle(self, step):
        step_state = self.step_states[step % self.sequence_length]

        if step_state == notestates.NOTE_OFF:
            step_state = input_velocity
        else:
            step_state = notestates.NOTE_OFF

        self.step_states[step % self.sequence_length] = step_state

        if not self.muted:
            self.view.update(step, step_state)
        elif step_state == notestates.NOTE_VEL_LOW:
            self.view.update(step, notestates.NOTE_MUTED_LOW)
        elif step_state == notestates.NOTE_VEL_HIGH:
            self.view.update(step, notestates.NOTE_MUTED_HIGH)
        else:
            self.view.update(step, notestates.NOTE_OFF)

        return self.step_states

    def mute_toggle(self):
        self.muted = not self.muted

        self.view.mute_display(self.muted, self.rows)

        # Update all steps in the view
        for step_idx, step in enumerate(self.step_states):
            step_idx = self.rows[0]*8 + (step_idx % self.sequence_length)

            if step == notestates.NOTE_VEL_LOW and self.muted:
                self.view.update(step_idx, notestates.NOTE_MUTED_LOW)
            elif step == notestates.NOTE_VEL_HIGH and self.muted:
                self.view.update(step_idx, notestates.NOTE_MUTED_HIGH)
            elif step and not self.muted:
                self.view.update(step_idx, step)

    def in_range(self, row):
        if len(self.rows) == 1:
            return self.rows[0] == row
        else:
            return self.rows[0] <= row and row <= self.rows[1]

    def query(self, step):
        if self.step_states[step % self.sequence_length]:
            return self.note_num
        else:
            return 0

    def clear(self):
        self.step_states = [notestates.NOTE_OFF for i in range(sequence_length)]
        self.view.clear()

    def stop_note(self):
        # Action only required if this sequencer is currently playing a step
        if self.playing_step is None:
            return

        step = self.playing_step
        step_state = self.step_states[step % self.sequence_length]

        if step_state and not self.muted:
            # Update the view if this sequencer is in the displayed page
            if self in get_current_seq_page():
                self.view.update(step, step_state)

            self.drum_out.send_message([144, self.note_num, 0])
        elif step_state == notestates.NOTE_VEL_LOW and self.muted:
            if self in get_current_seq_page():
                self.view.update(step, notestates.NOTE_MUTED_LOW)
        elif step_state == notestates.NOTE_VEL_HIGH and self.muted:
            if self in get_current_seq_page():
                self.view.update(step, notestates.NOTE_MUTED_HIGH)
        elif not step_state:
            if self in get_current_seq_page():
                self.view.update(step, notestates.NOTE_OFF)

        self.playing_step = None

    def start_note(self, step):
        if not randomize:
            step = self.rows[0]*8 + (step % self.sequence_length)
        else:
            # Create a random step and save it in self.randomized_step
            step = self.rows[0]*8 + random.randint(0, self.sequence_length-1)

        step_state = self.step_states[step % self.sequence_length]

        # Send a tick to the view and a drum note out if this step is turned
        # on and not muted.
        if step_state and not self.muted:
            # Update the view if this sequencer is in the displayed page
            if self in get_current_seq_page():
                self.view.update(step, notestates.NOTE_PLAYING)

            if step_state == notestates.NOTE_VEL_HIGH:
                self.drum_out.send_message([144, self.note_num, 127])
            elif step_state == notestates.NOTE_VEL_LOW:
                self.drum_out.send_message([144, self.note_num, 60])
        else:
            # Update the view if this sequencer is in the displayed page
            if self in get_current_seq_page():
                self.view.update(step, notestates.NOTE_PLAYING)

        self.playing_step = step

    def display(self):
        for step, step_state in enumerate(self.step_states):
            step = step + self.rows[0]*8
            if not self.muted:
                self.view.update(step, step_state)
            elif step_state == notestates.NOTE_VEL_LOW:
                self.view.update(step, notestates.NOTE_MUTED_LOW)
            elif step_state == notestates.NOTE_VEL_HIGH:
                self.view.update(step, notestates.NOTE_MUTED_HIGH)
            else:
                self.view.update(step, notestates.NOTE_OFF)


# Get outputs that contain the drum out port name string
drum_out, drum_out_name = midiutil.open_midiport(
        port=constants.DRUM_OUT_PORT_NAME, 
        type_='output')
print('Opening port \'{0}\' for output'.format(drum_out_name))

# Initialize sequencer models
sequencer_models = [[SequencerModel([0, 3], 32, 38, drum_out),
                     SequencerModel([4, 5], 16, 39, drum_out),
                     SequencerModel(   [6],  8, 41, drum_out),
                     SequencerModel(   [7],  8, 42, drum_out)],

                    [SequencerModel([0, 3], 32, 43, drum_out),
                     SequencerModel([4, 7], 32, 44, drum_out)]]

