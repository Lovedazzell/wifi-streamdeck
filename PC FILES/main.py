import socket
import subprocess
import os
import time
import threading
import pystray
from PIL import Image, ImageDraw

# ================================================================
#  CONFIG  –  edit these
# ================================================================

UDP_IP   = "0.0.0.0"   # listen on all network interfaces
UDP_PORT = 5005         # must match PC_PORT in ESP32 code

NIRCMD = os.path.join(os.path.dirname(__file__), "nircmd.exe")
DOCKER = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"

# ================================================================
#  VOLUME
# ================================================================

def set_windows_volume(level: int):
    vol = int(level / 100 * 65535)
    subprocess.Popen(
        [NIRCMD, "setsysvolume", str(vol)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

# ================================================================
#  ACTIONS  –  map each button to whatever you want
# ================================================================

COOLDOWN = 0.5
last_action: dict[str, float] = {}

def handle(data: str):
    now = time.time()
    if data in last_action and now - last_action[data] < COOLDOWN:
        return
    last_action[data] = now

    if data == "BTN1":
        subprocess.Popen([DOCKER], shell=True)

    elif data == "BTN2":
        pass

    elif data == "BTN3":
        pass

    elif data == "BTN4":
        pass

    elif data == "BTN5":
        pass

    elif data == "BTN6":
        pass

    elif data == "BTN7":
        pass

    elif data == "BTN8":
        pass  # assign something here

    elif data.startswith("VOL:"):
        try:
            set_windows_volume(int(data.split(":")[1]))
        except ValueError:
            pass

    else:
        print(f"[StreamDesk] Unknown command: {data!r}")

# ================================================================
#  UDP LISTENER  (replaces the old serial_loop)
# ================================================================

def udp_loop():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((UDP_IP, UDP_PORT))
            sock.settimeout(1.0)
            print(f"[StreamDesk] Listening on UDP port {UDP_PORT} ...")

            while True:
                try:
                    raw, addr = sock.recvfrom(128)
                    line = raw.decode("utf-8", errors="ignore").strip()
                    if line:
                        print(f"[StreamDesk] {addr[0]} → {line}")
                        handle(line)
                except socket.timeout:
                    continue   # just keeps the loop alive

        except OSError as e:
            print(f"[StreamDesk] Socket error: {e}  — retrying in 3s")
            time.sleep(3)
        finally:
            try:
                sock.close()
            except Exception:
                pass

# ================================================================
#  SYSTEM TRAY ICON
# ================================================================

def create_icon_image() -> Image.Image:
    img  = Image.new("RGB", (64, 64), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)
    # Green circle = running
    draw.ellipse((8, 8, 56, 56), fill=(0, 210, 110))
    # Small WiFi-ish dot in the middle
    draw.ellipse((28, 28, 36, 36), fill=(20, 20, 20))
    return img

def on_quit(icon, item):
    icon.stop()
    os._exit(0)

# ================================================================
#  ENTRY POINT
# ================================================================

def main():
    # Start UDP listener in background thread
    t = threading.Thread(target=udp_loop, daemon=True)
    t.start()

    # System tray
    icon = pystray.Icon(
        "StreamDesk",
        create_icon_image(),
        "Stream Desk (WiFi) Running",
        menu=pystray.Menu(
            pystray.MenuItem("Quit", on_quit),
        ),
    )
    icon.run()

if __name__ == "__main__":
    main()
