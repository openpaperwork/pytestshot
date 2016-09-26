#!/usr/bin/env python

import PIL.Image
import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk
from gi.repository import GdkPixbuf

import time


def pixbuf2image(pb):
    (width, height) = (pb.get_width(), pb.get_height())
    return PIL.Image.frombytes(
        "RGB",
        (width, height),
        pb.get_pixels()
    )


def screenshot(gdk_window):
    pb = Gdk.pixbuf_get_from_window(
        gdk_window, 0, 0, gdk_window.get_width(), gdk_window.get_height()
    )
    return pixbuf2image(pb)
