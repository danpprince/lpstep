import notestates
import rtmidi.midiutil as midiutil

NOTE_OFF     = 0
NOTE_MUTED   = 1
NOTE_ON      = 2
NOTE_PLAYING = 3

# Get outputs that contain the string 'Launchpad'
lp_midi_out, midi_out_name = midiutil.open_midiport(port='Launchpad', type_='output')
print('Opening port \'{0}\' for output'.format(midi_out_name))

class GlobalLpView(object):
    def display_playing(self, state):
        # Use the right arrow button to toggle playing
        playing_button_cc = 107
        if state:
            lp_midi_out.send_message([176, playing_button_cc, 48])
        else:
            lp_midi_out.send_message([176, playing_button_cc,  0])

    def display_randomize(self, state):
        # Use the mixer button to toggle randomization of steps
        randomize_button_cc = 111
        if state:
            lp_midi_out.send_message([176, randomize_button_cc, 48])
        else:
            lp_midi_out.send_message([176, randomize_button_cc,  0])

class LpView(object):
    def __init__(self, rows):
        self.rows = rows
        self.clear()

    def update(self, step, state):
        step_row = step / 8
        step_col = step % 8

        note_num = step_row*16 + step_col

        if state == NOTE_PLAYING:
            lp_midi_out.send_message([144, note_num, 3 << 4])
        elif state == NOTE_ON:
            # Alternate the color for active steps between sequences
            if self.rows[0] == 0 or self.rows[0] == 6:
                green = 2
                red   = 1
                lp_midi_out.send_message([144, note_num, (green << 4) + red])
            else:
                green = 1
                red   = 2
                lp_midi_out.send_message([144, note_num, (green << 4) + red])
        elif state == NOTE_MUTED:
            lp_midi_out.send_message([144, note_num,  1])
        else:
            lp_midi_out.send_message([144, note_num,  0])

    def mute_display(self, state, rows):
        if len(rows) == 2:
            for row in range(rows[0], rows[1]+1):
                step_col = 8
                note_num = row*16 + step_col

                if state:
                    lp_midi_out.send_message([144, note_num, 13])
                else:
                    lp_midi_out.send_message([144, note_num, 0])

        elif len(rows) == 1:
            step_col = 8
            note_num = rows[0]*16 + step_col

            if state:
                lp_midi_out.send_message([144, note_num, 13])
            else:
                lp_midi_out.send_message([144, note_num, 0])

    def clear(self):
        # All LEDs are turned off, and the mapping mode, buffer settings, and 
        # duty cycle are reset to their default values. 
        lp_midi_out.send_message([176, 0, 0])
