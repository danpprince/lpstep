class DrumSequencer(object):

    def __init__(self, sequence_length, note_num):
        self.sequence_length = sequence_length
        self.note_num = note_num

        self.step_states = [False for i in range(sequence_length)]

    def toggle(self, step):
        self.step_states[step] = not self.step_states[step]
        return self.step_states

    def query(self, step):
        """query(query_step)

        Return the note number of this DrumSequencer if the query step 
        is activated.

        Parameters:
        step - The step to query the note state of in the range of 0 to 
        sequence_length-1

        Returns the note number assigned to this object if the query step is
        activated in this object, or zero if the step is not activated.
        """
        if self.step_states[step]:
            return self.note_num
        else:
            return 0

    def clear(self):
        self.step_states = [False for i in range(self.sequence_length)]
