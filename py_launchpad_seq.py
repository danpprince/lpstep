import rtmidi
import rtmidi.midiutil as midiutil
import time

n_col = 8
n_row = 8

bpm = 110


class MidiNoteHandler(object):
    def __init__(self, lp_midi_out, drum_note_out):
        self.lp_midi_out = lp_midi_out
        self.drum_note_out = drum_note_out
        self.clear()
        # Initialize a 2d list to keep track of the state of every button
        self.button_states = [[0 for i in range(n_col)] for j in range(n_row)]

    def __call__(self, event, data=None):
        message, deltatime = event

        note_num = message[1]

        if message[0] == 144 and message[2] == 127:
            col = note_num % 16
            row = note_num / 16

            if col == 8 and row == 7:
                # Reset the grid
                self.clear()
                self.button_states = [[0 for i in range(n_col)] for j in range(n_row)]
            elif col < 8 and self.button_states[row][col] == 1:
                # This button is currently on, turn it off
                self.button_states[row][col] = 0
                self.lp_midi_out.send_message([144, note_num, 0])
            elif col < 8:
                # This button is currently off, turn it on
                self.button_states[row][col] = 1
                self.lp_midi_out.send_message([144, note_num, 127])

    def clear(self):
        # All LEDs are turned off, and the mapping mode, buffer settings, and 
        # duty cycle are reset to their default values. 
        self.lp_midi_out.send_message([176, 0, 0])

    def send_tick(self, note_num, state):
        green = 3

        col = note_num % 16
        row = note_num / 16

        if state == 1:
            self.lp_midi_out.send_message([144, note_num, green << 4])

            if self.button_states[row][col]:
                self.drum_note_out.send_message([144, 38, 120])
                time.sleep(0.01)
                self.drum_note_out.send_message([144, 38, 0])
        else:
            if self.button_states[row][col] == 1:
                # This button is currently on
                self.lp_midi_out.send_message([144, note_num, 127])
            else:
                # This button is currently off
                self.lp_midi_out.send_message([144, note_num, 0])


if __name__ == '__main__':
    # Get inputs that contain the string 'Launchpad'
    midi_in, midi_in_name = midiutil.open_midiport(port='Launchpad', type_='input')
    print('Opening port \'{0}\' for input'.format(midi_in_name))

    # Get outputs that contain the string 'Launchpad'
    lp_midi_out, lp_midi_out_name = midiutil.open_midiport(port='Launchpad', type_='output')
    print('Opening port \'{0}\' for output'.format(lp_midi_out_name))

    # Get outputs that contain the string 'loopMIDI'
    drum_note_out, drum_note_out_name = midiutil.open_midiport(port='loopMIDI', type_='output')
    print('Opening port \'{0}\' for output'.format(drum_note_out_name))

    midi_note_handler = MidiNoteHandler(lp_midi_out, drum_note_out) 

    midi_in.set_callback(midi_note_handler)

    # Set the period in seconds for one sixteenth note
    period_sec = 1.0/bpm * 60 / 8
    row = 0
    col = 0

    while True:
        # Step through each button at the specified bpm

        midi_note_handler.send_tick(row*16 + col, 1)
        time.sleep(0.1)
        midi_note_handler.send_tick(row*16 + col, 0)

        col = col + 1
        if col >= n_col:
            col = 0
            row = row + 1

        if row >= n_row:
            row = 0

        time.sleep(period_sec)
