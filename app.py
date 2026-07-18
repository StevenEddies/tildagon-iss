import app
import requests
import time
import ntptime
import wifi

from events.input import Buttons, BUTTON_TYPES

class IssCountdownApp(app.App):
    def __init__(self):
        self._button_states = Buttons(self)
        self.query()
    
    def update(self, delta):
        if self._button_states.get(BUTTON_TYPES["CANCEL"]):
            self._button_states.clear()
            self.minimise()
        
        now_timetamp_utc = time.time() + 946684800 # Micropython uses 2000 for epoch
        if (self._next_pass_start_timestamp_utc > now_timetamp_utc):
            countdown_seconds = self._next_pass_start_timestamp_utc - now_timetamp_utc
            countdown_minutes = int(countdown_seconds / 60)
            countdown_hours = int(countdown_minutes / 60)
            countdown_days = int(countdown_hours / 24)
            self._countdown = str(countdown_seconds % 60) + "s"
            if (countdown_minutes > 0):
                self._countdown = str(countdown_minutes % 60) + "m " + self._countdown
            if (countdown_hours > 0):
                self._countdown = str(countdown_hours % 24) + "h " + self._countdown
            if (countdown_days > 0):
                self._countdown = str(countdown_days) + "d " + self._countdown
        elif (self._next_pass_end_timestamp_utc >= now_timetamp_utc):
            self._countdown = "Now"
        else:
            self.query()
    
    def draw(self, ctx):
        ctx.text_align = ctx.CENTER
        ctx.font_size = 25
        ctx.rgb(0.2, 0.2, 0).rectangle(-120, -120, 240, 240).fill()
        ctx.rgb(1, 0.35, 0.25).move_to(0, -40).text("Next ISS pass in")
        ctx.font_size = 35
        ctx.rgb(1, 0.35, 0.25).move_to(0, 0).text(self._countdown)
        ctx.font_size = 25
        ctx.rgb(1, 0.35, 0.25).move_to(0, 30).text(self._next_pass_direction)
        ctx.rgb(1, 0.35, 0.25).move_to(0, 60).text(self._next_pass_quality)
    
    def query(self):
        self._countdown = "Loading..."
        self._connect_wifi()
        ntptime.settime()
        result = requests.get("https://issinfo.net/next-pass?lat=52.03975&lon=-2.38255&format=json").json()
        self._next_pass_start_timestamp_utc = result['pass']['startUTC']
        self._next_pass_end_timestamp_utc = result['pass']['endUTC']
        self._next_pass_direction = result['pass']['startDirection'] + " -> " + result['pass']['endDirection']
        self._next_pass_quality = result['pass']['quality'] + " quality"
    
    def _connect_wifi(self):
        if wifi.status():
            return
        wifi.disconnect()
        wifi.connect()
        wifi.wait()

__app_export__ = IssCountdownApp
