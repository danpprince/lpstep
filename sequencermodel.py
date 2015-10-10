import lpview

class SequencerModel(object):
    def __init__(self, rows, sequence_length, note_num, drum_out):
        self.rows = rows
        self.sequence_length = sequence_length
        self.note_num = note_num
        self.drum_out = drum_out

        self.step_states = [False for i in range(sequence_length)]

        self.muted = False

        self.view = lpview.LpView('Launchpad', rows)

    def set_view(self, view):
        self.view = view

    def toggle(self, step):
        step_state = not self.step_states[step % self.sequence_length]
        self.step_states[step % self.sequence_length] = step_state

        if step_state and not self.muted:
            self.view.update(step, lpview.NOTE_ON)
        elif step_state and self.muted:
            self.view.update(step, lpview.NOTE_MUTED)
        else:
            self.view.update(step, lpview.NOTE_OFF)

        return self.step_states

    def mute_toggle(self):
        self.muted = not self.muted
        # Update all steps in the view
        for step_idx, step in enumerate(self.step_states):
            step_idx = self.rows[0]*8 + (step_idx % self.sequence_length)

            if step and self.muted:
                self.view.update(step_idx, lpview.NOTE_MUTED)
            elif step and not self.muted:
                self.view.update(step_idx, lpview.NOTE_ON)

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
        self.step_states = [False for i in range(self.sequence_length)]
        self.view.clear()

    def tick(self, step, state):
        step = self.rows[0]*8 + (step % self.sequence_length)
        step_state = self.step_states[step % self.sequence_length]

        # Send a tick to the view and a drum note out if this step is turned
        # on and not muted.
        if state and step_state and not self.muted:
            self.view.update(step, lpview.NOTE_PLAYING)
            self.drum_out.send_message([144, self.note_num, 127])

        elif state:
            self.view.update(step, lpview.NOTE_PLAYING)

        elif not state and step_state and not self.muted:
            self.view.update(step, lpview.NOTE_ON)
            self.drum_out.send_message([144, self.note_num, 0])

        elif not state and step_state and self.muted:
            self.view.update(step, lpview.NOTE_MUTED)

        elif not state and not step_state:
            self.view.update(step, lpview.NOTE_OFF)
