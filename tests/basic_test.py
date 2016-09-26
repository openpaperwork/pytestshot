import threading
import time
import unittest

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

import testshot


class GtkWinInstance(object):
    def start(self):
        self.window = Gtk.Window()
        self.button = Gtk.Button("pouet")
        self.window.add(self.button)
        self.window.show_all()
        self.window.set_size_request(640, 480)

        self.thread = threading.Thread(target=self._gtk_thread)
        self.thread.start()

        time.sleep(1)

    def _gtk_thread(self):
        Gtk.main()

    def stop(self):
        testshot.wait()
        self.window.destroy()
        testshot.wait()
        testshot.exit()
        self.thread.join()


class TestBasicWin(unittest.TestCase):
    def setUp(self):
        self.app = GtkWinInstance()
        self.app.start()

    def test_screenshot(self):
        testshot.wait()
        pil_img = testshot.screenshot(self.app.window.get_window())
        self.assertNotEqual(pil_img, None)

    def test_ref(self):
        testshot.assertWindow(self, "test_basic", self.app.window.get_window())

    def tearDown(self):
        self.app.stop()
