from lpview import LpView

class SequencerModel(object):
    def __init__(self, rows, sequence_length, note_num):
        self.rows = rows
        self.sequence_length = sequence_length
        self.note_num = note_num

        self.step_states = [False for i in range(sequence_length)]

        self.view = LpView('Launchpad', rows)

    def set_view(self, view):
        self.view = view

    def toggle(self, step):
        step_state = not self.step_states[step % self.sequence_length]
        self.step_states[step % self.sequence_length] = step_state
        self.view.update(step, step_state)
        return self.step_states

    def in_range(self, row):
        return self.rows[0] <= row and row <= self.rows[1]

    def query(self, step):
        if self.step_states[step % self.sequence_length]:
            return self.note_num
        else:
            return 0

    def clear(self):
        self.step_states = [False for i in range(self.sequence_length)]
        self.view.clear()
