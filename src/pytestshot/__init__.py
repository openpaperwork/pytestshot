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


GLib.threads_init()


TESTS_DATA_DIR = os.getenv(
    'TESTS_DATA_DIR',
    os.path.join('tests', 'screenshots')
)


def pixbuf2image(pb):
    (width, height) = (pb.get_width(), pb.get_height())
    pixels = pb.get_pixels()
    colors = "RGB"
    if (width * height * 4 == len(pixels)):
        colors = "RGBA"
    return PIL.Image.frombytes(
        colors,
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
    GLib.idle_add(Gtk.main_quit)
    Gtk.main_quit()


def _swt(pil_img):
    pil_img = pil_img.resize(
        (pil_img.size[0] * 4, pil_img.size[1] * 4),
        PIL.Image.ANTIALIAS
    )
    pil_img = pillowfight.swt(pil_img, pillowfight.SWT_OUTPUT_BW_TEXT)
    pil_img = pil_img.resize(
        (int(pil_img.size[0] / 4), int(pil_img.size[1] / 4)),
        PIL.Image.ANTIALIAS
    )
    return pil_img


def assertScreenshot(test_inst, test_name, real_out_img, focus_on_text=True):
    out_img = real_out_img

    if focus_on_text:
        out_img = _swt(out_img)

    ref_filename = "{}_ref.png".format(test_name)
    out_filename = "{}_out.png".format(test_name)
    real_diff_filename = "{}_diff.png".format(test_name)
    diff_swt_filename = "{}_diff_txt.png".format(test_name)

    if not os.path.exists(os.path.join(TESTS_DATA_DIR, ref_filename)):
        real_out_img.save(os.path.join(TESTS_DATA_DIR, out_filename))
    test_inst.assertTrue(
        (os.path.exists(os.path.join(TESTS_DATA_DIR, ref_filename)))
    )

    ref_img = PIL.Image.open(os.path.join(TESTS_DATA_DIR, ref_filename))
    real_ref_img = ref_img

    if ref_img.size != out_img.size:
        has_diff = True
        real_diff_img = None
        diff_swt_img = None
    else:
        if focus_on_text:
            ref_img = _swt(ref_img)
            (has_diff, diff_swt_img) = pillowfight.diff(out_img, ref_img)
        else:
            (has_diff, real_diff_img) = pillowfight.diff(out_img, ref_img)

    if has_diff:
        real_out_img.save(os.path.join(TESTS_DATA_DIR, out_filename))
        if diff_swt_img:
            diff_swt_img.save(os.path.join(TESTS_DATA_DIR, diff_swt_filename))
            (_, real_diff_img) = pillowfight.diff(real_out_img, real_ref_img)
            real_diff_img.save(os.path.join(TESTS_DATA_DIR, real_diff_filename))
        elif real_diff_img:
            real_diff_img.save(os.path.join(TESTS_DATA_DIR, real_diff_filename))

    test_inst.assertFalse(has_diff)
