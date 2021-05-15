from importlib import resources

import gi

gi.require_versions({"Gtk": "3.0"})
from gi.repository import Gtk


@Gtk.Template.from_string(
    resources.read_text("pdfpassword.screens", "confirmation_screen.ui")
)
class ConfirmationScreen(Gtk.Box):

    __gtype_name__ = "ConfirmationScreen"

    # ui elements from the template:
    status_image = Gtk.Template.Child()  # type: Gtk.Image
    filename_label = Gtk.Template.Child()  # type: Gtk.Label

    def __init__(self, window):
        super().__init__()
        self.window = window

    def update_values(self, pdf):
        self.status_image.set_from_stock(pdf.confirmation_image, Gtk.IconSize.DIALOG)
        self.filename_label.set_text(pdf.confirmation_filename)

    @Gtk.Template.Callback()
    def on_quit_button_clicked(self, widget):
        self.window.do_destroy()
