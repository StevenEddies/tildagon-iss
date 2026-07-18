import app
import requests

from events.input import Buttons, BUTTON_TYPES

class IssCountdownApp(app.App):
    def __init__(self):
        self._button_states = Buttons(self)
        result = requests.get("https://issinfo.net/next-pass?lat=52.03975&lon=-2.38255&format=json").json()
        self._next_pass_start_timestamp_utc = result['pass']['startUTC']
        self._next_pass_end_timestamp_utc = result['pass']['endUTC']

    def update(self, delta):
        if self._button_states.get(BUTTON_TYPES["CANCEL"]):
            self._button_states.clear()
            self.minimise()

    def draw(self, ctx):
        ctx.text_align = ctx.CENTER
        ctx.font_size = 25
        ctx.rgb(0.2, 0.2, 0).rectangle(-120, -120, 240, 240).fill()
        ctx.rgb(1, 0.35, 0.25).move_to(0, -40).text("Next ISS pass in")
        ctx.font_size = 35
        ctx.rgb(1, 0.35, 0.25).move_to(0, 0).text(str(self._next_pass_start_timestamp_utc))

__app_export__ = IssCountdownApp
