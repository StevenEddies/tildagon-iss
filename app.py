import app

from events.input import Buttons, BUTTON_TYPES

class IssTrackerApp(app.App):
    def __init__(self):
        self.button_states = Buttons(self)
        self.counter = 0

    def update(self, delta):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            self.minimise()
        if self.button_states.get(BUTTON_TYPES["RIGHT"]):
            self.button_states.clear()
            self.counter = self.counter + 1

    def draw(self, ctx):
        ctx.rgb(0, 0.2, 0).rectangle(-120, -120, 240, 240).fill()
        ctx.rgb(0, 1, 0).move_to(-80, 0).text(str(self.counter))

__app_export__ = IssTrackerApp
