import board
import busio
import displayio
import terminalio
import usb_cdc
import json

from adafruit_display_text import label
from adafruit_displayio_ssd1306 import SSD1306

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.modules.encoder import EncoderHandler
from kmk.extensions.rgb import RGB

from kmk.scanners import MatrixScanner
from kmk.scanners.digitalio import DigitalioScanner
from kmk.scanners.shift_register import ShiftRegisterScanner


keyboard = KMKKeyboard()

from kmk.scanners import MatrixScanner
from kmk.scanners.digitalio import DigitalioScanner
from kmk.scanners.shift_register import ShiftRegisterScanner

ROW_PINS = (
    board.GP0,
    board.GP1,
    board.GP2,
    board.GP3,
    board.GP4,
    board.GP5,
    board.GP6,
    board.GP7,
)

COL_SHIFT_REGISTER = ShiftRegisterScanner(
    data_pin=board.GP8,
    clock_pin=board.GP9,
    latch_pin=board.GP10,
    num_cols=14,
)

keyboard.matrix = MatrixScanner(
    rows=DigitalioScanner(ROW_PINS),
    cols=COL_SHIFT_REGISTER,
    diode_orientation=MatrixScanner.DIODE_COL2ROW,
)


keyboard.keymap = [
        KC.Q, KC.W, KC.E, KC.R, KC.T, KC.Y, KC.U, KC.I, KC.O, KC.P, KC.NO, KC.NO, KC.NO, KC.NO,
        KC.A, KC.S, KC.D, KC.F, KC.G, KC.H, KC.J, KC.K, KC.L, KC.ENTER, KC.NO, KC.NO, KC.NO, KC.NO,
        KC.Z, KC.X, KC.C, KC.V, KC.B, KC.N, KC.M, KC.COMMA, KC.DOT, KC.SLASH, KC.NO, KC.NO, KC.NO, KC.NO,
        KC.ESC, KC.TAB, KC.LCTL, KC.LALT, KC.SPACE, KC.RALT, KC.RCTL, KC.LEFT, KC.DOWN, KC.UP, KC.RIGHT, KC.NO, KC.NO, KC.NO,
        KC.Q, KC.W, KC.E, KC.R, KC.T, KC.Y, KC.U, KC.I, KC.O, KC.P, KC.NO, KC.NO, KC.NO, KC.NO,
        KC.A, KC.S, KC.D, KC.F, KC.G, KC.H, KC.J, KC.K, KC.L, KC.ENTER, KC.NO, KC.NO, KC.NO, KC.NO,
        KC.Z, KC.X, KC.C, KC.V, KC.B, KC.N, KC.M, KC.COMMA, KC.DOT, KC.SLASH, KC.NO, KC.NO, KC.NO, KC.NO,
        KC.ESC, KC.TAB, KC.LCTL, KC.LALT, KC.SPACE, KC.RALT, KC.RCTL, KC.LEFT, KC.DOWN, KC.UP, KC.RIGHT, KC.NO, KC.NO, KC.NO
]

rgb = RGB(
    pixel_pin=board.GP0,
    num_pixels=10,
    brightness=0.3,
)
keyboard.extensions.append(rgb)

KEY_LED_MAP = {
    0: (0, 1),
    1: (2,),
    2: (3,),
    14: (4, 5),
    15: (6,),
    16: (7,),
    28: (8, 9),
}

def led_press(key, *_):
    if key.key_number in KEY_LED_MAP:
        for led in KEY_LED_MAP[key.key_number]:
            rgb.set_hsv(led, 0, 255, 255)

def led_release(*_):
    for i in range(10):
        rgb.set_hsv(i, 160, 255, 40)

keyboard.after_press_handler(led_press)
keyboard.after_release_handler(led_release)

encoders = EncoderHandler()
encoders.pins = (
    (board.GP13, board.GP14, None),
    (board.GP15, board.GP16, None),
)
encoders.map = (
    (KC.VOLD, KC.VOLU),
    (KC.BRIM, KC.BRID),
)
keyboard.modules.append(encoders)

displayio.release_displays()
i2c = busio.I2C(scl=board.GP18, sda=board.GP17)

display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = SSD1306(display_bus, width=128, height=64)

root = displayio.Group()
display.root_group = root

title = label.Label(terminalio.FONT, text="PICO KMK", x=0, y=8)
stats = label.Label(terminalio.FONT, text="", x=0, y=24)
status = label.Label(terminalio.FONT, text="", x=0, y=56)

root.append(title)
root.append(stats)
root.append(status)
serial = usb_cdc.data

host = {
    "cpu": 0,
    "ram": 0,
    "temp": 0,
    "time": "--:--:--",
}

def read_serial():
    if serial.connected and serial.in_waiting:
        try:
            data = json.loads(serial.readline().decode().strip())
            host.update(data)
        except Exception:
            pass
def update_display():
    stats.text = (
        f"CPU:{host['cpu']}%\n"
        f"RAM:{host['ram']}%\n"
        f"TMP:{host['temp']}C\n"
        f"{host['time']}"
    )
    caps = "ON" if keyboard.hid.keyboard_leds.caps_lock else "OFF"
    status.text = f"L{keyboard.active_layers[0]} CAPS:{caps}"
def housekeeping(kbd):
    read_serial()
    update_display()

keyboard.before_matrix_scan_handler(housekeeping)
if __name__ == "__main__":
    keyboard.go()
