import time
import queue
import math
import evdev
import threading

from pypilot.client import pypilotClient

CENTER = 1001
STOP = 0

def detect_gamepad() -> evdev.InputDevice:
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for d in devices:
        if d.name == "Logitech Gamepad F710":
            return d
    raise RuntimeError("Device not found")


def debug_loop(gamepad):
    for event in gamepad.read_loop():
        print(event)
        # Buttons
        if event.type == evdev.ecodes.EV_KEY:
            print(event)
        # Analog gamepad
        elif event.type == evdev.ecodes.EV_ABS:
            absevent = evdev.categorize(event)
            print(evdev.ecodes.bytype[absevent.event.type][absevent.event.code], absevent.event.value)


class ReaderThread(threading.Thread):
    def __init__(self, gamepad, queue, slider):
        super().__init__()
        self.gamepad = gamepad
        self.queue = queue
        self.slider = slider
        self.queue_enabled = False
        self.setDaemon(True)

    def run(self):
        previous_offset_from_0 = 0
        print("Starting reader thread")
        for event in self.gamepad.read_loop():
            if event.type == evdev.ecodes.EV_ABS and event.code == evdev.ecodes.ABS_RX:
                self.slider.SetValue(event.value)
                if self.queue_enabled:
                    if event.value == 128:
                        print("Idle mode, joystick in home position, sending 0")
                        previous_offset_from_0 = 0
                        self.queue.queue.clear()
                        self.queue.put(STOP)
                        # continue
                    normalized = event.value / 32768 / -2
                    offset_from_0 = math.fabs(normalized)
                    if offset_from_0 > previous_offset_from_0:
                        self.queue.put(normalized)
                        previous_offset_from_0 = offset_from_0
            elif event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.BTN_SOUTH and event.value == 1:
                print("Button A pressed", "Going to 0")
                self.queue.put(CENTER)
                pass

    def enable_queue(self):
        print("Enable sending events to queue")
        self.queue_enabled = True

    def disable_queue(self):
        print("Disable sending events to queue")
        self.queue_enabled = False


class WorkerThread(threading.Thread):
    def __init__(self, pypilot, queue: queue.Queue):
        super().__init__()
        self.pypilot = pypilot
        self.queue = queue
        self.stopped = False
        self.setDaemon(True)

    def run(self):
        print("Starting worker thread...")
        while True:
            if self.stopped:
                print("Worker Thread stopped")
                break
            try:
                new_command = self.queue.get(timeout=0.1)
                if new_command == STOP:
                    print("Stopping")
                    self.send_servo_command(0)
                elif new_command == CENTER:
                    self.send_position_0()
                else:
                    print(f"Sending new command: {new_command}")
                    self.send_servo_command(new_command)
                    # while self.queue.empty():
                    #     print(f"Repeating command: {new_command}")
                    #     self.send_to_pypilot(new_command)
                    #     time.sleep(0.5)
            except queue.Empty:
                pass

    def send_servo_command(self, value):
        self.pypilot.set("servo.command", value)
        self.pypilot.receive()

    def send_position_0(self):
        self.pypilot.set("servo.position_command", 0)
        self.pypilot.receive()

    def stop(self):
        print("Stopping worker thread...")
        self.stopped = True
