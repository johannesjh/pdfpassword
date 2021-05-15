from importlib import resources

import gi

gi.require_versions({"Gtk": "3.0"})
from gi.repository import Gdk, GObject, Gtk


@Gtk.Template.from_string(resources.read_text("pdfpassword.screens", "file_screen.ui"))
class FileScreen(Gtk.Box):

    __gtype_name__ = "FileScreen"

    __gsignals__ = {
        "save-encrypted-pdf": (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_NONE,
            (GObject.TYPE_STRING,),
        ),
        "save-decrypted-pdf": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
    }

    # ui elements from the template:
    filename_label = Gtk.Template.Child()  # type: Gtk.Label
    status_label = Gtk.Template.Child()  # type: Gtk.Label
    preview_image = Gtk.Template.Child()  # type: Gtk.Image
    unlock_box = Gtk.Template.Child()  # type: Gtk.Box
    unlock_entry = Gtk.Template.Child()  # type: Gtk.Entry
    save_box = Gtk.Template.Child()  # type: Gtk.Box
    pw_entry = Gtk.Template.Child()  # type: Gtk.Entry

    def __init__(self, window):
        super().__init__()
        self.window = window
        self.setup_styling()

    def setup_styling(self):
        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        # custom drag and drop styling, compare `:drop(active)` in
        # https://gitlab.gnome.org/GNOME/gtk/-/blob/gtk-3-24/gtk/theme/Adwaita/_common.scss
        css = b"""
        .pdf-preview-box {
            border: 1px solid black;
            background-color: white;
        }
        """
        provider.load_from_data(css)

    def update_values(self, pdf):
        # keep a reference to the pdf
        self.pdf = pdf

        # display filename
        self.filename_label.set_text(pdf.filename)

        # display status label
        if pdf.file_error:
            self.status_label.set_text(pdf.file_error)
        elif pdf.file_password_protected:
            self.status_label.set_text("PDF with Password-Protection.")
        else:
            self.status_label.set_text("No Password Protection.")

        # reset password entry fields
        self.unlock_entry.set_text("")
        self.pw_entry.set_text("")

        # display (or hide) the file-unlock or the file-save widgets
        if pdf.file_password_missing or pdf.file_password_wrong:
            self.save_box.set_visible(False)
            self.unlock_box.set_visible(True)
            self.preview_image.set_visible(False)
        else:
            self.save_box.set_visible(True)
            self.unlock_box.set_visible(False)
            self.preview_image.set_visible(True)

        # display thumbnail
        if pdf.thumbnail is None:
            self.preview_image.set_from_stock("gtk-file", Gtk.IconSize.DIALOG)
        else:
            self.preview_image.set_from_surface(pdf.thumbnail)

    @Gtk.Template.Callback()
    def on_unlock_button_clicked(self, widget):
        self.pdf.open_pdf(str(self.pdf.path), password=self.unlock_entry.get_text())
        self.update_values(self.pdf)

    @Gtk.Template.Callback()
    def on_save_button_clicked(self, widget):
        print("save")
        pw = self.pw_entry.get_text()
        if pw:
            self.emit("save-encrypted-pdf", self.pw_entry.get_text())
        else:
            self.emit("save-decrypted-pdf")
