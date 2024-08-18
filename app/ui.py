import wx
from pypilot.client import pypilotClient

from gamepad import detect_gamepad, ReaderThread, WorkerThread
import queue


class MyApp(wx.App):
    def __init__(self):
        super().__init__(clearSigInt=True)

        # init frame
        self.InitFrame(pypilot)

    def InitFrame(self, pypilot):
        frame = MyFrame(parent=None, title="xPilot", pos=(100, 100))
        frame.Show()


class MyFrame(wx.Frame):
    # subclass of wx.Window; Frame is a top level window
    # A frame is a window whose size and position can (usually) be changed by the user.
    # Usually represents the first/main window a user will see
    def __init__(self, parent, title, pos):
        super().__init__(parent=parent, title=title, pos=pos)
        self.OnInit()

    def OnInit(self):
        panel = MyPanel(parent=self)


class MyPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)
        welcome = wx.StaticText(self, label="xPilot for pyPilot 0.17 by Felix K. 2024", pos=(20, 20))
        self.gamepad_text = wx.StaticText(self, label="Detecting Gamepad...", pos=(20, 50))
        self.slider = wx.Slider(self, value=0, minValue=-32768, maxValue=32767, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.button = wx.Button(parent=self, label='Enable xPilot', pos=(20, 120))
        self.button.Bind(wx.EVT_BUTTON, self.onSubmit)  # bind action to button

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(welcome, 0)
        vbox.Add(self.gamepad_text, 1)
        vbox.Add(self.slider, 2, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=20)
        vbox.Add(self.button, 0, border=20)

        self.SetSizer(vbox)
        self.Center()

        try:
            self.gamepad = detect_gamepad()
            self.gamepad_text.SetLabelText(f"Detected {self.gamepad.name} on {self.gamepad.path}")
        except RuntimeError as e:
            self.gamepad_text.SetLabelText(f"Error: {e}")
        self.worker = False

        self.reader = ReaderThread(self.gamepad, q, self.slider)
        self.reader.start()

    def onSubmit(self, event):
        if self.worker and self.worker.is_alive():
            self.reader.disable_queue()
            self.worker.stop()
            self.button.SetLabelText("Enable xPilot")
        else:
            self.reader.enable_queue()
            self.worker = WorkerThread(pypilot, q)
            self.worker.start()
            self.button.SetLabelText("Disable xPilot")


if __name__ == "__main__":
    q = queue.Queue()
    pypilot = pypilotClient(lambda x: x)
    app = MyApp()
    app.MainLoop()
