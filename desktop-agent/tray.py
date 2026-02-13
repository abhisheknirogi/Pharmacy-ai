import pystray
from PIL import Image, ImageDraw
import threading
from agent import upload_loop  # your upload loop

def create_icon():
    img = Image.new("RGB", (64, 64), "blue")
    d = ImageDraw.Draw(img)
    d.text((10, 20), "PR", fill="white")
    return img

def on_exit(icon, item):
    icon.stop()

def run_tray():
    icon = pystray.Icon("Pharmarec", create_icon(), menu=pystray.Menu(
        pystray.MenuItem("Exit", on_exit)
    ))
    icon.run()

threading.Thread(target=upload_loop).start()
run_tray()
