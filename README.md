# Pytestshot

Pytestshot is a small Python module allowing to quickly take
screenshots of a Gtk/Gdk window and compare it to a reference
screenshots. It raises an exception for unittest
(see ```unittest.TestCase.assertTrue()```) when the screenshots
don't match.


## Original issue

I needed a tool to test Paperwork. And Paperwork doesn't support (yet)
accessibility (so [dogtail](https://fedorahosted.org/dogtail/)).
Even if it would, almost half of Paperwork's code is dedicated to custom
GUI rendering. It just cannot be checked with accessibility.

For instance, one things that can hardly be tested with dogtail is:
Are the boxes around the words drawn where they should be ?
(and are they drawn at all ?)


## Example

```py
import pytestshot

from your_application import YourApplication


class TestScreenshot(unittest.TestCase):
    def setUp(self):
        self.app = YourApplication()
        # calls Gtk.main() in another thread and start the application
        self.app.start()

    def test_screenshot(self):
        pil_img = pytestshot.screenshot(self.app.window.get_window())
        pytestshot.assertScreenshot(self, "test_screenshot", pil_img)

    def tearDown(self):
        self.app.stop()
```


## What does it do ?

### Importing pytestshot

* Disable hardware acceleration for GTK. Your window may appear black,
  but the screenshots should work fine (GDK\_RENDERING=image).
* Set the GTK theme to HighContrast (GTK\_THEME=HighContrast) (make
  image treatment easier, and screenshots are smallers when stored
  as PNG)
* Disables locales (LANG=C)

Because of these environment changes, pytestshot must be imported
**before** the GLib, GObject, Gdk or Gtk.


### pytestshot.screenshot()

It takes a screenshot of your Gdk window (See
[Paperwork](https://github.com/jflesch/paperwork-tests/blob/unstable/tests/screenshots/test_main_win_start_ref.png)
for instance).

Returns a Pillow image.


### pytestshot.assertScreenshot()

It compares the screenshot to a reference screenshots.

It takes 3 argument:
* A unittest.TestCase instance running the test
  (used to call ```unittest.TestCase.assertTrue()```)
* A test name. Is the basis for the screenshot filenames.
* A Pillow image to compare to the reference screenshot.

Comparison is done using the method
```pillowfight.compare(tolerance=64)```
(Ex: [Input 1](https://raw.githubusercontent.com/jflesch/libpillowfight/master/tests/data/black_border_problem.jpg) + [Input 2](https://raw.githubusercontent.com/jflesch/libpillowfight/master/tests/data/black_border_problem_blackfilter.jpg) => [Output](https://raw.githubusercontent.com/jflesch/libpillowfight/master/tests/data/black_border_problem_diff.jpg))

If the comparison fails, 2 extra files are created. One show
the actual screenshot, and the other is the difference between
the reference screenshot and the actual one.

Screenshots are stored in ```tests/screenshots``` :
* Reference screenshots are named ```[test_name]_ref.png```
* Actual screeshots are named ```[test_name]_out.png```
* Difference images are named ```[test_name]_diff.png``` (if possible)

If the actual screenshots is actually what you want, you can simply
rename ```[test_name]_out.png``` into ```[test_name]_ref.png```,
and next time, the test will pass.


## An obvious problem

Obviously, the main problem is to always get the same screenshots, every
single time, on every computers.

The simplest solution is to define a reference test system.

For instance, for Paperwork, the reference test sytem is:
* GNU/Linux Debian stable
* Gnome 3

Even then, you have to make sure your application starts everytime in the
very same context. For instance, for Paperwork, it means starting each
test with:
* No index (XDG_DATA_HOME points to a clean empty directory)
* A clearly defined set of documents in the work directory
* A clearly defined window size (part of Paperwork's config file)


## pytestshot-compare

Unfortunately, even then, it seems impossible to get screenshots that
match perfectly a reference.

Therefore, Pytestshot provides a small tool called "pytestshot-compare".
It can be called from command line. It allows to compare manually
and quickly the screenshots. It also allows renaming quickly
"xxx_out.png" into "xxx_ref.png" if the user wants it.
