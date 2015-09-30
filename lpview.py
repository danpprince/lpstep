import rtmidi.midiutil as midiutil

NOTE_OFF     = 0
NOTE_ON      = 1
NOTE_PLAYING = 2

class LpView(object):
    # Get outputs that contain the string 'Launchpad'
    lp_midi_out, midi_out_name = midiutil.open_midiport(port='Launchpad', type_='output')

    print('Opening port \'{0}\' for output'.format(midi_out_name))

    def __init__(self, port_name, rows):
        self.rows  = rows

        self.clear()

    def update(self, step, state):
        step_row = step / 8
        step_col = step % 8

        note_num = step_row*16 + step_col

        if state:
            LpView.lp_midi_out.send_message([144, note_num, 127])
        else:
            LpView.lp_midi_out.send_message([144, note_num, 0])

    def tick(self, row, col, state):
        note_num = row*16 + col

        if state:
            LpView.lp_midi_out.send_message([144, note_num, green << 4])
        else:
            LpView.lp_midi_out.send_message([144, note_num, ])

    def clear(self):
        # All LEDs are turned off, and the mapping mode, buffer settings, and 
        # duty cycle are reset to their default values. 
        LpView.lp_midi_out.send_message([176, 0, 0])
