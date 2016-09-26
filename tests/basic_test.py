import threading
import time
import unittest

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gtk

import testshot


class GtkWinInstance(object):
    def start(self):
        self.window = Gtk.Window()
        self.button = Gtk.Button("pouet")
        self.window.add(self.button)
        self.window.show_all()
        self.window.set_size_request(640, 480)

        self.condition = threading.Condition()

        thread = threading.Thread(target=self._gtk_thread)
        thread.start()

        time.sleep(1)

    def _gtk_thread(self):
        Gtk.main()

    def _wake_up(self):
        self.condition.acquire()
        try:
            self.condition.notify_all()
        finally:
            self.condition.release()

    def wait(self):
        self.condition.acquire()
        try:
            while Gtk.events_pending():
                GLib.idle_add(self._wake_up)
                self.condition.wait()
        finally:
            self.condition.release()

    def stop(self):
        GLib.idle_add(Gtk.main_quit)


class TestBasicMainWin(unittest.TestCase):
    def setUp(self):
        self.app = GtkWinInstance()
        self.app.start()

    def test_screenshot(self):
        self.app.wait()
        pil_img = testshot.screenshot(self.app.window.get_window())
        self.assertNotEqual(pil_img, None)

    def tearDown(self):
        self.app.stop()
