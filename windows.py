import win32api
import win32gui

def get_pixel():
    b = win32api.GetKeyState(0x01)
    while True:
        a = win32api.GetKeyState(0x01)
        if a != b:
            return get_position()

def get_position():
    return win32api.GetCursorPos()
