import tkinter
from windows import get_position 
from PIL import Image, ImageTk, ImageGrab
import threading

""" Cursor for app rgbsafe
created by Fleserig"""

import win32api

# position of mouse on start
position = win32api.GetKeyState(0x01)

class Cursor(tkinter.Tk):
    def __init__(self, cursor_size = 100, cursor_len = 1.5):
        super().__init__()
        self.cursor_size = cursor_size
        self.cursor_len = cursor_len
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.geometry(f"{cursor_size}x{cursor_size}")
        self.image = tkinter.Label(self)
        self.image.pack()
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.loop4cursor()
        self.loop4mouse()
        self.thread = threading.Thread(target=self.keyboard)
        self.thread.start()
        self.positionew = -1

    # move cursor and when corners change position
    def change_position(self, x, y):
        x2 = round(x+(self.cursor_size/self.cursor_len)/2)
        y2 = round(y+(self.cursor_size/self.cursor_len)/2)
        if x2 > self.screen_width - self.cursor_size:
            x2 = round(x - self.cursor_size - (self.cursor_size/self.cursor_len)/2)
        if y2 > self.screen_height - self.cursor_size:
            y2 = round(y - self.cursor_size - (self.cursor_size/self.cursor_len)/2)
        self.geometry('+{}+{}'.format(x2, y2))

    def track_position(self):
        x, y = get_position()
        self.change_position(x, y)
        return x, y
    
    def keyboard(self):
        import keyboard
        def on_key_event(event):
            if event.event_type == "down":
                if keyboard.is_pressed("ctrl+shift+="):
                    self.cursor_len+=0.5
                if keyboard.is_pressed("ctrl+shift+-"):
                    if self.cursor_len > 1:
                        self.cursor_len-=0.5
        keyboard.hook(on_key_event)
    
    def loop4mouse(self):
        global position
        position2 = win32api.GetKeyState(0x01)
        if position != position2:
            self.positionew = get_position()
            self.destroy()
        self.after(100, self.loop4mouse)
    
    def loop4cursor(self):
        global new_image
        x, y = self.track_position()
        screen_size = (self.cursor_size/self.cursor_len)/2
        screen_size2 = self.cursor_size*self.cursor_len
        screen = ImageGrab.grab(bbox = (x-screen_size, y-screen_size, x+screen_size, y+screen_size)) 
        resized_image = screen.resize((round(screen_size2), round(screen_size2)), Image.Resampling.NEAREST)
        new_image = ImageTk.PhotoImage(resized_image)
        self.image["image"] = new_image
        self.after(50, self.loop4cursor)