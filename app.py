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

    def draw(self, ctx):
        ctx.text_align = ctx.CENTER
        ctx.font_size = 25
        ctx.rgb(0.2, 0.2, 0).rectangle(-120, -120, 240, 240).fill()
        ctx.rgb(0.6, 0, 1).move_to(0, -40).text("Next ISS pass in")

__app_export__ = IssTrackerApp
