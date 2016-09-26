#!/usr/bin/env python

import os
import threading

import PIL.Image
import pillowfight
import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gtk


TESTS_DATA_DIR = os.getenv(
    'TESTS_DATA_DIR',
    os.path.join('tests', 'screenshots')
)


def pixbuf2image(pb):
    (width, height) = (pb.get_width(), pb.get_height())
    return PIL.Image.frombytes(
        "RGB",
        (width, height),
        pb.get_pixels()
    )


class GtkWait(object):
    def __init__(self):
        self.condition = threading.Condition()

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


def wait():
    GtkWait().wait()


def screenshot(gdk_window):
    wait()
    pb = Gdk.pixbuf_get_from_window(
        gdk_window, 0, 0, gdk_window.get_width(), gdk_window.get_height()
    )
    return pixbuf2image(pb)


def exit():
    wait()
    Gtk.main_quit()


def assertScreenshot(test_inst, test_name, orig_img, focus_on_text=True):
    out_img = orig_img
    if focus_on_text:
        out_img = out_img.resize(
            (out_img.size[0] * 4, out_img.size[1] * 4),
            PIL.Image.ANTIALIAS
        )
        out_img = pillowfight.swt(out_img, pillowfight.SWT_OUTPUT_BW_TEXT)
        out_img = out_img.resize(
            (int(out_img.size[0] / 4), int(out_img.size[1] / 4)),
            PIL.Image.ANTIALIAS
        )

    ref_filename = "{}_ref.png".format(test_name)
    out_filename = "{}_out.png".format(test_name)
    orig_filename = "{}_orig.png".format(test_name)
    diff_filename = "{}_diff.png".format(test_name)

    if not os.path.exists(os.path.join(TESTS_DATA_DIR, ref_filename)):
        out_img.save(os.path.join(TESTS_DATA_DIR, out_filename))
        orig_img.save(os.path.join(TESTS_DATA_DIR, orig_filename))
    assert(os.path.exists(os.path.join(TESTS_DATA_DIR, ref_filename)))
    ref_img = PIL.Image.open(os.path.join(TESTS_DATA_DIR, ref_filename))

    (has_diff, diff_img) = pillowfight.diff(out_img, ref_img)
    if has_diff:
        orig_img.save(os.path.join(TESTS_DATA_DIR, orig_filename))
        out_img.save(os.path.join(TESTS_DATA_DIR, out_filename))
        diff_img.save(os.path.join(TESTS_DATA_DIR, diff_filename))

    test_inst.assertFalse(has_diff)
