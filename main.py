import serial.tools.list_ports
import serial
import dataclasses
import configparser
import time
import keyboard_sim
import pygetwindow
import subprocess

ARDUINO_PORT_ID='CH340'
SERIAL_BAUD=9600
PORT = None
COMMANDS = {}
RELAY_TIME = 300
SECONDS_BETWEEN_INPUTS = 0.100
alt_pressed = False
DEBUG = False

@dataclasses.dataclass
class Apps:
    plex_name = "Plex HTPC"
    plex_path = r"C:\Program Files\Plex\Plex HTPC\Plex HTPC.exe"
    yttv_name = "YouTube on TV - Google Chrome"
    yttv_path = r"C:\Users\Cleptes\Desktop\yttv.bat"
    kodi_name = "Kodi"
    kodi_path = r"C:\Program Files\Kodi\kodi.exe"
    firefox_name = "Mozilla Firefox"
    firefox_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"

@dataclasses.dataclass
class Commands:
    POWER="POWER"
    UP="UP"
    DOWN="DOWN"
    LEFT="LEFT"
    RIGHT="RIGHT"
    ENTER="ENTER"
    TAB="TAB"
    BACK="BACK"
    MENU="MENU"
    VOL_UP="VOL_UP"
    VOL_DOWN="VOL_DOWN"
    MUTE="MUTE"
    ALT_TAB="ALT_TAB"
    EXIT = "EXIT"
    PLAY_PAUSE = "PLAY_PAUSE"
    STOP = "STOP"
    NEXT_TRACK = "NEXT_TRACK"
    PREV_TRACK = "PREV_TRACK"
    RED_APP_KEY = "RED_APP_KEY"
    GREEN_APP_KEY = "GREEN_APP_KEY"
    YELLOW_APP_KEY = "YELLOW_APP_KEY"
    BLUE_APP_KEY = "BLUE_APP_KEY"
    ALT_F4 = "ALT_F4"

KNOWN_COMMANDS = [Commands.POWER,Commands.UP,Commands.DOWN,Commands.LEFT,Commands.RIGHT,Commands.ENTER,Commands.TAB,Commands.BACK,Commands.MENU,Commands.VOL_UP,Commands.VOL_DOWN,Commands.MUTE,Commands.ALT_TAB,Commands.EXIT,Commands.PLAY_PAUSE,Commands.STOP,Commands.NEXT_TRACK,Commands.PREV_TRACK,Commands.RED_APP_KEY,Commands.GREEN_APP_KEY,Commands.YELLOW_APP_KEY,Commands.BLUE_APP_KEY,Commands.ALT_F4]



def get_config():
    config = configparser.ConfigParser()
    config.read("config.ini")
    port = config.get("Main","port")
    command_set = config.get("Main", "command_set")
    relay_time = config.get("Main", "relay_time")
    seconds_between_inputs = config.get("Main", "seconds_between_inputs")
    debug = config.get("Main","debug") == 'True'
    if not port:
        port = None

    COMMANDS = {
        int(config.get(command_set,"POWER"),16): "POWER",
        int(config.get(command_set,"UP"),16): "UP",
        int(config.get(command_set,"DOWN"),16): "DOWN",
        int(config.get(command_set,"LEFT"),16): "LEFT",
        int(config.get(command_set,"RIGHT"),16): "RIGHT",
        int(config.get(command_set,"ENTER"),16): "ENTER",
        int(config.get(command_set,"TAB"),16): "TAB",
        int(config.get(command_set,"BACK"),16): "BACK",
        int(config.get(command_set,"MENU"),16): "MENU",
        int(config.get(command_set,"VOL_UP"),16): "VOL_UP",
        int(config.get(command_set,"VOL_DOWN"),16): "VOL_DOWN",
        int(config.get(command_set,"MUTE"),16): "MUTE",
        int(config.get(command_set,"ALT_TAB"),16): "ALT_TAB",
        int(config.get(command_set,"EXIT"),16): "EXIT",
        int(config.get(command_set,"PLAY_PAUSE"),16): "PLAY_PAUSE",
        int(config.get(command_set,"STOP"),16): "STOP",
        int(config.get(command_set,"NEXT_TRACK"),16): "NEXT_TRACK",
        int(config.get(command_set,"PREV_TRACK"),16): "PREV_TRACK",
        int(config.get(command_set,"RED_APP_KEY"),16): "RED_APP_KEY",
        int(config.get(command_set,"GREEN_APP_KEY"),16): "GREEN_APP_KEY",
        int(config.get(command_set,"YELLOW_APP_KEY"),16): "YELLOW_APP_KEY",
        int(config.get(command_set,"BLUE_APP_KEY"),16): "BLUE_APP_KEY",
        int(config.get(command_set,"ALT_F4"),16): "ALT_F4",
        
    }
    return (port,
            COMMANDS,
            int(relay_time) if relay_time else RELAY_TIME,
            float(seconds_between_inputs) if seconds_between_inputs else SECONDS_BETWEEN_INPUTS,
            debug)

# Plex HTPC
# YouTube on TV - Google Chrome
# Mozilla Firefox
# Kodi
def put_app_in_foreground_or_start_it(window_name, path):
    started_apps = pygetwindow.getWindowsWithTitle(window_name) 
    if len(started_apps) == 0:
        print(f"starting {window_name} at: {path}")
        subprocess.Popen([path])
    else:
        app=started_apps[0]
        print(f"opening app {window_name} {app}")
        app.minimize()
        app.restore()


def execute_command(command_hex):
    global ser
    global alt_pressed

    match COMMANDS.get(command_hex,None):
        case Commands.POWER:
            print("power")
            ser.write(f'0,{RELAY_TIME}\n'.encode())
            return
        case Commands.UP:
            keyboard_sim.TypeKey(keyboard_sim.VK_UP)
            return
        case Commands.DOWN:
            keyboard_sim.TypeKey(keyboard_sim.VK_DOWN)
            return
        case Commands.LEFT:
            keyboard_sim.TypeKey(keyboard_sim.VK_LEFT)
            return
        case Commands.RIGHT:
            keyboard_sim.TypeKey(keyboard_sim.VK_RIGHT)
            return
        case Commands.ENTER:
            keyboard_sim.TypeKey(keyboard_sim.VK_RETURN)
            if alt_pressed:
                keyboard_sim.ReleaseKey(keyboard_sim.VK_ALT)
                alt_pressed = False
            return
        case Commands.TAB:
            keyboard_sim.TypeKey(keyboard_sim.VK_TAB)
            return
        case Commands.BACK:
            keyboard_sim.TypeKey(keyboard_sim.VK_BACKSPACE)
        case Commands.MENU:
            keyboard_sim.TypeKey(keyboard_sim.VK_WIN)
            return
        case Commands.VOL_UP:
            keyboard_sim.TypeKey(keyboard_sim.VK_VOLUME_UP)
            return
        case Commands.VOL_DOWN:
            keyboard_sim.TypeKey(keyboard_sim.VK_VOLUME_DOWN)
            return
        case Commands.MUTE:
            keyboard_sim.TypeKey(keyboard_sim.VK_VOLUME_MUTE)
            return
        case Commands.ALT_TAB:
            keyboard_sim.PressKey(keyboard_sim.VK_ALT)
            keyboard_sim.PressKey(keyboard_sim.VK_TAB)
            alt_pressed = True
            return
        case Commands.EXIT:
            keyboard_sim.TypeKey(keyboard_sim.VK_ESCAPE)
            if alt_pressed:
                keyboard_sim.ReleaseKey(keyboard_sim.VK_ALT)
                alt_pressed = False
            return
        case Commands.PLAY_PAUSE:
            keyboard_sim.TypeKey(keyboard_sim.VK_PLAY_PAUSE)
            return
        case Commands.STOP:
            keyboard_sim.TypeKey(keyboard_sim.VK_STOP)
            return
        case Commands.NEXT_TRACK:
            keyboard_sim.TypeKey(keyboard_sim.VK_NEXT_TRACK)
            return
        case Commands.PREV_TRACK:
            keyboard_sim.TypeKey(keyboard_sim.VK_PREV_TRACK)
            return
        case Commands.RED_APP_KEY:
            put_app_in_foreground_or_start_it(Apps.yttv_name,Apps.yttv_path)
            return
        case Commands.GREEN_APP_KEY:
            put_app_in_foreground_or_start_it(Apps.plex_name,Apps.plex_path)
            return
        case Commands.YELLOW_APP_KEY:
            put_app_in_foreground_or_start_it(Apps.firefox_name, Apps.firefox_path)
            return
        case Commands.BLUE_APP_KEY:
            put_app_in_foreground_or_start_it(Apps.kodi_name,Apps.kodi_path)
            return
        case Commands.ALT_F4:
            keyboard_sim.PressKey(keyboard_sim.VK_ALT)
            keyboard_sim.PressKey(keyboard_sim.VK_F4)
            keyboard_sim.ReleaseKey(keyboard_sim.VK_F4)
            keyboard_sim.ReleaseKey(keyboard_sim.VK_ALT)
            return
        
        case None:
            print("Hex",hex(command_hex),"not implemented.")

def select_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if ARDUINO_PORT_ID in p[1]:
            return p[0]

PORT, COMMANDS, RELAY_TIME, SECONDS_BETWEEN_INPUTS, DEBUG = get_config()
ser = serial.Serial(select_port() if PORT is None else PORT, SERIAL_BAUD)
if __name__ == '__main__':
    prev_millis = 0
    while True:
        cc = str(ser.readline())
        command = int(cc[2:][:-5],16)
        if DEBUG:
                print(hex(command))
        if time.time() - prev_millis > SECONDS_BETWEEN_INPUTS:
            execute_command(command)
            prev_millis = time.time()