import threading
import time
import unittest

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

import pytestshot


class GtkWinInstance(object):
    def start(self):
        self.window = Gtk.Window()
        self.button = Gtk.Button.new_with_label("pouet")
        self.window.add(self.button)
        self.window.show_all()
        self.window.set_size_request(640, 480)

        self.thread = threading.Thread(target=self._gtk_thread)
        self.thread.start()

        time.sleep(1)

    def _gtk_thread(self):
        Gtk.main()

    def stop(self):
        pytestshot.wait()
        self.window.hide()
        pytestshot.wait()
        pytestshot.exit()
        self.thread.join()


class TestBasicWin(unittest.TestCase):
    def setUp(self):
        self.app = GtkWinInstance()

    def test_screenshot(self):
        self.app.start()
        try:
            pil_img = pytestshot.screenshot(self.app.window.get_window())
            self.assertNotEqual(pil_img, None)
        finally:
            self.app.stop()

    def test_ref(self):
        self.app.start()
        try:
            pil_img = pytestshot.screenshot(self.app.window.get_window())
            self.assertNotEqual(pil_img, None)
        finally:
            self.app.stop()
        pytestshot.assertScreenshot(self, "test_basic", pil_img)
