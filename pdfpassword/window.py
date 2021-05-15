import logging
import os
from importlib import resources

import gi

from pdfpassword.pdf import Pdf
from pdfpassword.screens.confirmation_screen import ConfirmationScreen
from pdfpassword.screens.file_screen import FileScreen
from pdfpassword.screens.start_screen import StartScreen

gi.require_versions({"Gtk": "3.0"})
from gi.repository import GObject, Gtk

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))


@Gtk.Template.from_string(resources.read_text("pdfpassword", "window.ui"))
class ApplicationWindow(Gtk.ApplicationWindow):
    """Main application window."""

    __gtype_name__ = "PdfpasswordWindow"

    __gsignals__ = {
        "show-screen": (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_NONE,
            (GObject.TYPE_STRING,),
        )
    }

    # ui elements from the template
    stack = Gtk.Template.Child()  # type: Gtk.Stack
    back_button = Gtk.Template.Child()  # type: Gtk.Button

    def __init__(self, app):
        super().__init__(application=app)
        self.app = app
        self.pdf = Pdf()

        self.start_screen = StartScreen(self)
        self.stack.add_named(self.start_screen, "start_screen")
        self.start_screen.connect("open-pdf", self.open_pdf)

        self.file_screen = FileScreen(self)
        self.stack.add_named(self.file_screen, "file_screen")
        self.file_screen.connect("save-encrypted-pdf", self.save_encrypted_pdf)
        self.file_screen.connect("save-decrypted-pdf", self.save_decrypted_pdf)

        self.confirmation_screen = ConfirmationScreen(self)
        self.stack.add_named(self.confirmation_screen, "confirmation_screen")

        self.show_all()
        self.connect("show-screen", self.show_screen)
        self.show_screen(self, "start_screen")

    @Gtk.Template.Callback()
    def on_back_button_clicked(self, *args):
        print("back-button")
        self.emit("show-screen", "start_screen")

    def show_screen(self, widget, screen):
        self.stack.set_visible_child_name(screen)
        self.back_button.set_visible(screen != "start_screen")
        self.file_screen.update_values(self.pdf)
        self.confirmation_screen.update_values(self.pdf)

    def open_pdf(self, source_widget, filename):
        print("open-pdf", filename)
        self.pdf = Pdf(filename)
        self.emit("show-screen", "file_screen")

    def save_encrypted_pdf(self, source_widget, password):
        self.pdf.save_encrypted(password)
        self.emit("show-screen", "confirmation_screen")

    def save_decrypted_pdf(self, source_widget):
        self.pdf.save_decrypted()
        self.emit("show-screen", "confirmation_screen")

    def do_destroy(self):
        self.app.remove_window(self)
