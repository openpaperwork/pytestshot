import glob
import io
import logging
import os

import PIL.Image

from gi.repository import GdkPixbuf
from gi.repository import GLib
from gi.repository import Gtk


logger = logging.getLogger(__name__)

TESTS_DATA_DIR = os.getenv(
    'TESTS_DATA_DIR',
    os.path.join('tests', 'screenshots')
)

PREFIX = os.environ.get('VIRTUAL_ENV', '/usr')

UI_FILES_DIRS = [
    ".",
    "src/pytestshot",
    "data",
    PREFIX + "/local/share/pytestshot",
    PREFIX + "/share/pytestshot",

    # XXX(Jflesch): The following locations are unexpected
    # but it seems those are the locations used by Pip
    # (sys.prefix in setup.py ?)
    PREFIX + "/local/lib/python*/dist-packages/usr/share/pytestshot",
    PREFIX + "/local/lib/python*/dist-packages/usr/local/share/pytestshot",
    PREFIX + "/lib/python*/dist-packages/usr/share/pytestshot",
    PREFIX + "/lib/python*/dist-packages/usr/local/share/pytestshot",
]


def load_uifile(filename):
    """
    Load a .glade file and return the corresponding widget tree

    Arguments:
        filename -- glade filename to load.
            This function will (try to) figure out from where it must be loaded.

    Returns:
        GTK Widget tree

    Throws:
        Exception -- If the file cannot be found
    """
    widget_tree = Gtk.Builder()
    has_ui_file = False
    for ui_glob_dir in UI_FILES_DIRS:
        for ui_dir in glob.glob(ui_glob_dir):
            ui_file = os.path.join(ui_dir, filename)
            if os.access(ui_file, os.R_OK):
                logger.info("UI file used: " + ui_file)
                widget_tree.add_from_file(ui_file)
                has_ui_file = True
                break
        if has_ui_file:
            break
    if not has_ui_file:
        logger.error("Can't find resource file '%s'. Aborting" % filename)
        raise Exception("Can't find resource file '%s'. Aborting" % filename)
    return widget_tree


def image2pixbuf(img):
    """
    Convert an image object to a gdk pixbuf
    """
    if img is None:
        return None
    file_desc = io.BytesIO()
    try:
        img.save(file_desc, "ppm")
        contents = file_desc.getvalue()
    finally:
        file_desc.close()
    loader = GdkPixbuf.PixbufLoader.new_with_type("pnm")
    try:
        loader.write(contents)
        pixbuf = loader.get_pixbuf()
    finally:
        loader.close()
        return pixbuf


class Comparator(object):
    def __init__(self):
        self.widget_tree = load_uifile("pytestshot-compare.glade")
        self.main_win = self.widget_tree.get_object("mainwindow")
        self.main_win.connect("destroy", Gtk.main_quit)
        self.main_win.set_visible(True)

        self.img_ref = self.widget_tree.get_object("imageRef")
        self.img_out = self.widget_tree.get_object("imageOut")
        self.img_diff = self.widget_tree.get_object("imageDiff")

        self.imgs_idx = 0
        self.imgs = []
        for filename in os.listdir(TESTS_DATA_DIR):
            if not filename.endswith("_out.png"):
                continue
            ref = filename.replace("_out.png", "_ref.png", -1)
            diff = filename.replace("_out.png", "_diff.png", -1)
            self.imgs.append((
                os.path.join(TESTS_DATA_DIR, filename),
                os.path.join(TESTS_DATA_DIR, ref),
                os.path.join(TESTS_DATA_DIR, diff)
            ))

        self.widget_tree.get_object("buttonNo").connect(
            "clicked",
            self.__goto_next
        )
        self.widget_tree.get_object("buttonYes").connect(
            "clicked",
            self.__apply
        )
        self.widget_tree.get_object("buttonPrevious").connect(
            "clicked",
            self.__goto_previous
        )
        self.refresh_imgs()

    def __goto_next(self, _=None):
        self.imgs_idx += 1
        self.refresh_imgs()

    def __goto_previous(self, _=None):
        self.imgs_idx -= 1
        if self.imgs_idx < 0:
            self.imgs_idx = 0
        self.refresh_imgs()

    def __apply(self, _=None):
        imgs = self.imgs[self.imgs_idx]
        try:
            os.unlink(imgs[1])
        except FileNotFoundError:
            pass
        try:
            os.unlink(imgs[2])
        except FileNotFoundError:
            pass
        os.rename(imgs[0], imgs[1])
        self.__goto_next()

    def refresh_imgs(self):
        if self.imgs_idx >= len(self.imgs):
            GLib.idle_add(Gtk.main_quit)
            return
        imgs = self.imgs[self.imgs_idx]

        self.main_win.set_title(os.path.basename(imgs[0]))
        self.img_out.set_from_file(imgs[0])

        if imgs[1] and os.path.exists(imgs[1]):
            self.img_ref.set_from_file(imgs[1])
        else:
            self.img_ref.set_from_icon_name(
                "insert-image",
                Gtk.IconSize.DIALOG
            )
        if imgs[2] and os.path.exists(imgs[2]):
            img = PIL.Image.open(imgs[2])
            img = img.resize((img.size[0] * 2, img.size[1] * 2))
            img = image2pixbuf(img)
            self.img_diff.set_from_pixbuf(img)
        else:
            self.img_diff.set_from_icon_name(
                "insert-image",
                Gtk.IconSize.DIALOG
            )

    def run(self):
        Gtk.main()


def main():
    formatter = logging.Formatter(
        '%(levelname)-6s %(name)-30s %(message)s')
    handler = logging.StreamHandler()
    log = logging.getLogger()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel({
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
    }[os.getenv("PYTESTSHOT_VERBOSE", "INFO")])

    comparator = Comparator()
    comparator.run()
