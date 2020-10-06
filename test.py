import os
import time
import win32gui
import win32api
import win32con
import psutil
import win32process

from win32gui import PyMakeBuffer, SendMessage, PyGetBufferAddressAndLen, PyGetString

if __name__ == '__main__':
    # win32api.GetFocus()
    while 1:

        hwnd = win32gui.GetForegroundWindow()
        print(hwnd)
        print(win32gui.GetWindowText(hwnd))
        # print(win32gui.Get(hwnd))
        #
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            thread_id, process_id = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(process_id)
            print(process.name(), process_id, process.exe())
            # proc = psutil.Process(pid=process_id)
            # print(proc.name())

        pass

        time.sleep(1)
