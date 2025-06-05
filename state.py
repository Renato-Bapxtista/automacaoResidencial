class State:
    def __init__(self, state):
        self.value = state

    def on(self):
        self.value = 1

    def off(self):
        self.value = 0

    def toggle(self):
        self.value = 0 if self.value else 1
