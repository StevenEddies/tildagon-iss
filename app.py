import app
import requests
import time
import ntptime
import wifi
from system.eventbus import eventbus
from system.hexpansion.util import get_app_by_vid_pid

from events.input import Buttons, BUTTON_TYPES

PRE_LOADING = 0
LOADING = 1
FUTURE = 2
NOW = 3
ERROR = 4
NO_PASS = 5

class IssCountdownApp(app.App):
    def __init__(self):
        self._button_states = Buttons(self)
        self._state = PRE_LOADING
        self._recheck = 0
        
        self._gps = get_app_by_vid_pid(0x7CAB, 0xBEAC)

        if self._gps:
            eventbus.on(
                self._gps.GPSEvent,
                self.handle_gps_event,
                self
            )
            self._position = None
        else:
            self._position = (52.03975, 2.38255) # Eastnor
        
    
    def update(self, delta):
        if self._button_states.get(BUTTON_TYPES["CANCEL"]):
            self._button_states.clear()
            self.minimise()
            return
        
        if (self._button_states.get(BUTTON_TYPES["CONFIRM"]) and (self._state == ERROR or self._state == NO_PASS)):
            self._button_states.clear()
            self._state = PRE_LOADING
            return
        
        if (self._recheck <= time.time() and (self._state == ERROR or self._state == NO_PASS)):
            self._state = PRE_LOADING
            return
        
        if (self._state == PRE_LOADING):
            self._state = LOADING
            return
            
        if (self._state == LOADING):
            self.query()
            return
            
        if (self._state == ERROR or self._state == NO_PASS):
            return
        
        now_timetamp_utc = time.time() + 946684800 # Micropython uses 2000 for epoch
        if (self._next_pass_start_timestamp_utc > now_timetamp_utc):
            countdown_seconds = self._next_pass_start_timestamp_utc - now_timetamp_utc
            countdown_minutes = int(countdown_seconds / 60)
            countdown_hours = int(countdown_minutes / 60)
            countdown_days = int(countdown_hours / 24)
            self._countdown = ""
            if (countdown_days == 0 and countdown_hours == 0):
                self._countdown = str(countdown_seconds % 60) + "s"
            if (countdown_minutes > 0 and countdown_days == 0):
                self._countdown = str(countdown_minutes % 60) + "m " + self._countdown
            if (countdown_hours > 0):
                self._countdown = str(countdown_hours % 24) + "h " + self._countdown
            if (countdown_days > 0):
                self._countdown = str(countdown_days) + "d " + self._countdown
            self._state = FUTURE
        elif (self._next_pass_end_timestamp_utc >= now_timetamp_utc):
            self._countdown = "Now"
            self._state = NOW
        else:
            self._state = LOADING
    
    def draw(self, ctx):
        ctx.text_align = ctx.CENTER
        if (self._state == LOADING or self._state == PRE_LOADING):
            ctx.rgb(0.2, 0.2, 0).rectangle(-120, -120, 240, 240).fill()
            ctx.font_size = 35
            ctx.rgb(1, 0.35, 0.25).move_to(0, -2).text("Loading...")
        elif (self._state == ERROR):
            ctx.rgb(0.2, 0.2, 0).rectangle(-120, -120, 240, 240).fill()
            ctx.font_size = 35
            ctx.rgb(1, 0.35, 0.25).move_to(0, -2).text("Error loading")
            ctx.font_size = 25
            ctx.rgb(1, 0.35, 0.25).move_to(0, 30).text("Press C to retry")
        elif (self._state == FUTURE):
            ctx.font_size = 25
            ctx.rgb(0.2, 0.2, 0).rectangle(-120, -120, 240, 240).fill()
            ctx.rgb(1, 0.35, 0.25).move_to(0, -40).text("Next ISS pass in")
            ctx.font_size = 35
            ctx.rgb(1, 0.35, 0.25).move_to(0, -2).text(self._countdown)
            ctx.font_size = 25
            ctx.rgb(1, 0.35, 0.25).move_to(0, 30).text(self._next_pass_direction)
            ctx.rgb(1, 0.35, 0.25).move_to(0, 60).text(self._next_pass_quality)
        elif (self._state == NOW):
            ctx.rgb(1, 0.35, 0.25).rectangle(-120, -120, 240, 240).fill()
            ctx.font_size = 35
            ctx.rgb(0.2, 0.2, 0).move_to(0, -40).text("ISS")
            ctx.rgb(0.2, 0.2, 0).move_to(0, -2).text("passing now")
            ctx.font_size = 25
            ctx.rgb(0.2, 0.2, 0).move_to(0, 30).text(self._next_pass_direction)
            ctx.rgb(0.2, 0.2, 0).move_to(0, 60).text(self._next_pass_quality)
        elif (self._state == NO_PASS):
            ctx.font_size = 25
            ctx.rgb(0.2, 0.2, 0).rectangle(-120, -120, 240, 240).fill()
            ctx.rgb(1, 0.35, 0.25).move_to(0, -40).text("Next ISS pass in")
            ctx.font_size = 35
            ctx.rgb(1, 0.35, 0.25).move_to(0, -2).text(">10d")
    
    def query(self):
        if self._position is None:
            return
        try:
            self._countdown = "Loading..."
            self._connect_wifi()
            ntptime.settime()
            result = requests.get("https://issinfo.net/next-pass?lat=" + str(self._position[0]) + "&lon=" + str(self._position[1]) + "&format=json").json()
            if result['pass'] is None:
                self._state = NO_PASS
                self._recheck = time.time() + (3600 * 12)
            else:
                self._next_pass_start_timestamp_utc = result['pass']['startUTC']
                self._next_pass_end_timestamp_utc = result['pass']['endUTC']
                self._next_pass_direction = result['pass']['startDirection'] + " → " + result['pass']['endDirection']
                next_pass_quality = result['pass']['quality']
                self._next_pass_quality = next_pass_quality[0].upper() + next_pass_quality[1:] + " quality"
                self._state = FUTURE
        except Exception as err_obj:
            self._state = ERROR
            self._recheck = time.time() + 60
            print(err_obj)
    
    def _connect_wifi(self):
        if wifi.status():
            return
        wifi.disconnect()
        wifi.connect()
        wifi.wait()
    
    def handle_gps_event(self, event):
        self._position = event.position


__app_export__ = IssCountdownApp
