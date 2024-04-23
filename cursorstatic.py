import tkinter
from windows import get_position, get_pixel
from PIL import Image, ImageTk, ImageGrab
import threading

""" Cursor static for app rgbsafe
created by Fleserig"""


# position of mouse on start
position = get_pixel()

class Cursor(tkinter.Tk):
    def __init__(self, cursor_size=300, cursor_len=1.5, position=(0,0)):
        super().__init__()
        self.cursor_size = cursor_size
        self.cursor_len = cursor_len
        self.attributes('-topmost', True)
        self.geometry(f"{cursor_size}x{cursor_size}")
        self.image = tkinter.Label(self)
        self.image.pack()
        self.position = position
        self.bind("<Button-1>", self.choose)
        self.thread = threading.Thread(target=self.keyboard)
        self.thread.start()
        self.positionew = -1
        self.refresh()

    def keyboard(self):
        import keyboard
        def on_key_event(event):
            if event.event_type == "down":
                if keyboard.is_pressed("ctrl+shift+="):
                    self.cursor_len+=0.5
                    self.refresh()
                if keyboard.is_pressed("ctrl+shift+-"):
                    if self.cursor_len > 1:
                        self.cursor_len-=0.5
                        self.refresh()
        keyboard.hook(on_key_event)
    
    def choose(self, e):
        x, y = position
        self.positonew = round(x + e.x/self.cursor_len), round(y + e.y/self.cursor_len)
        self.destroy()

    def refresh(self):
        global new_image
        x, y = self.position
        screen_size = (self.cursor_size/self.cursor_len)/2
        screen_size2 = self.cursor_size*self.cursor_len
        screen = ImageGrab.grab(bbox = (x-screen_size, y-screen_size, x+screen_size, y+screen_size)) 
        resized_image = screen.resize((round(screen_size2), round(screen_size2)), Image.Resampling.NEAREST)
        new_image = ImageTk.PhotoImage(resized_image)
        self.image["image"] = new_image
