import rtmidi.midiutil as midiutil

NOTE_OFF     = 0
NOTE_MUTED   = 1
NOTE_ON      = 2
NOTE_PLAYING = 3

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

        if state == NOTE_PLAYING:
            LpView.lp_midi_out.send_message([144, note_num, 2 << 4])
        elif state == NOTE_ON:
            LpView.lp_midi_out.send_message([144, note_num, 127])
        elif state == NOTE_MUTED:
            LpView.lp_midi_out.send_message([144, note_num, 13])
        else:
            LpView.lp_midi_out.send_message([144, note_num, 0])

    def clear(self):
        # All LEDs are turned off, and the mapping mode, buffer settings, and 
        # duty cycle are reset to their default values. 
        LpView.lp_midi_out.send_message([176, 0, 0])
