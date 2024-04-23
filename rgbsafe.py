import sys
import argparse
from PIL import ImageGrab
import getpass
import base64
import itertools
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


f = open("settings.rgb", "r")
lines = f.readlines()
settings = {}
for line in lines:
    setting, value = line.strip().split("=")
    settings[setting.rstrip()] = value.lstrip()
if settings['cursor'] == 'normal':
    from cursor import Cursor
if settings['cursor'] == 'static':
    from cursorstatic import Cursor
f = open(settings['path'], "r")
lines = f.readlines()
names = []
passwords = []

for line in lines:
    name, password = line.strip().split(":")
    names.append(name)
    passwords.append(password)

backend = default_backend()

class Crypto:
    def __init__(self, color):
        self.key = bytes(color) 
        self.encryptor = Cipher(algorithms.AES(self.key), modes.ECB(), backend).encryptor()
        self.decryptor = Cipher(algorithms.AES(self.key), modes.ECB(), backend).decryptor()

    def create_pass(self, password:str):
        return base64.urlsafe_b64encode(self.encrypt(password))
    def get_pass(self, password:str):
        return self.decrypt(base64.urlsafe_b64decode(password))
    
    def encrypt(self, value):
        padder = padding.PKCS7(algorithms.AES(self.key).block_size).padder()
        padded_data = padder.update(value) + padder.finalize()
        encrypted_text = self.encryptor.update(padded_data) + self.encryptor.finalize()
        return encrypted_text

    def decrypt(self, value):
        padder = padding.PKCS7(algorithms.AES(self.key).block_size).unpadder()
        decrypted_data = self.decryptor.update(value)
        unpadded = padder.update(decrypted_data) + padder.finalize()
        return unpadded


def get_color(position):
    # Capture the screen image
    x , y = position
    screen = ImageGrab.grab(bbox = (x-1, y-1, x+2, y+2))
    colors = []
    perm = itertools.product([0, 1, 2], repeat=2)
    for i, j in perm:
        r, g, b = screen.getpixel((i, j))
        colors.append(r)
        colors.append(g)
        colors.append(b)
    return colors + colors[-5:]

def levenshtein(a, b):
    if len(b) == 0:
        return len(a)
    if len(a) == 0:
        return len(b)
    if a[0] == b[0]:
        return levenshtein(a[1::], b[1::])
    else:
        return 1 + min(levenshtein(a[1::], b), min(levenshtein(a, b[1::]), levenshtein(a[1::], b[1::])))

def lev_n(f_name, l_names):
    best_name = l_names[0]
    best_score = levenshtein(f_name, l_names[0])
    for i, n in enumerate(l_names):
        now_score = levenshtein(n, f_name) 
        if now_score < best_score:
            best_score = now_score
            best_name = names[i]
    return best_name

parser = argparse.ArgumentParser(
    prog="rgbsafe",
    description="rgb password manager")
parser.add_argument("name", type=str)
parser.add_argument("-a", "--add", action='store_true')
parser.add_argument("-r", "--rem", action='store_true')
parser.add_argument("-c", "--chg", action='store_true')
parser.add_argument("-s", "--set", action='store_true')
args = parser.parse_args()

cursor = Cursor(cursor_size=int(settings['cursor_size']), cursor_len=float(settings['cursor_len']))
cursor.mainloop()
color = get_color(cursor.positionew)
crypto = Crypto(color)
if args.add:
    password2add = getpass.getpass("write password >")
    names.append(args.name)
    passwords.append(str(crypto.create_pass(bytes(password2add, encoding='ascii')), encoding='ascii'))
elif args.rem:
    to_rem = names.index(lev_n(args.name, names))
    names.pop(to_rem)
    passwords.pop(to_rem)
elif args.chg:
    to_chg = names.index(lev_n(args.name, names))
    print("""change
          [0] name
          [1] password
          [2] color
          """)
    match input():
        case "0":
            names[to_chg] = input(">")
        case "1":
            passwords[to_chg] = str(crypto.create_pass(bytes(input(">"), encoding='ascii')), encoding='ascii')
        case "2":
            old_pass = str(crypto.get_pass(bytes(passwords[to_chg])), encoding='ascii')
            cursor = Cursor()
            cursor.mainloop()
            color = get_color(cursor.positionew)
            crypto = Crypto(color)
            passwords[to_chg] = str(crypto.create_pass(bytes(old_pass, encoding='ascii')), encoding='ascii')
else:
    import win32clipboard
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(str(crypto.get_pass(bytes(passwords[names.index(lev_n(args.name, names))], encoding='ascii')), encoding='ascii'))
    win32clipboard.CloseClipboard()

with open("password.txt", "w") as f:
    for i in range(len(names)-1):
        f.write(str(names[i]) + ":" + str(passwords[i]) +"\n")
    f.write(str(names[-1]) + ":" + str(passwords[-1]))


