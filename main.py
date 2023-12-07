import serial.tools.list_ports
import serial
import dataclasses
import configparser
import time
import keyboard_sim

ARDUINO_PORT_ID='CH340'
SERIAL_BAUD=250000
PORT = None
COMMANDS = {}
RELAY_TIME = 300
SECONDS_BETWEEN_INPUTS = 0.200
alt_pressed = False
DEBUG = False
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

KNOWN_COMMANDS = [Commands.POWER,Commands.UP,Commands.DOWN,Commands.LEFT,Commands.RIGHT,Commands.ENTER,Commands.TAB,Commands.BACK,Commands.MENU,Commands.VOL_UP,Commands.VOL_DOWN,Commands.MUTE,Commands.ALT_TAB]

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
    }
    return (port,
            COMMANDS,
            int(relay_time) if relay_time else RELAY_TIME,
            float(seconds_between_inputs) if seconds_between_inputs else SECONDS_BETWEEN_INPUTS,
            debug)

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
            keyboard_sim.TypeKey(keyboard_sim.VK_ESCAPE)
            if alt_pressed:
                keyboard_sim.ReleaseKey(keyboard_sim.VK_ALT)
                alt_pressed = False
            return
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