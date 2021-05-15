from importlib import resources
from pathlib import Path
from urllib.parse import unquote, urlparse

import gi

gi.require_versions({"Gtk": "3.0"})
from gi.repository import Gdk, GObject, Gtk


@Gtk.Template.from_string(resources.read_text("pdfpassword.screens", "start_screen.ui"))
class StartScreen(Gtk.Box):
    __gtype_name__ = "StartScreen"

    __gsignals__ = {
        "open-pdf": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,))
    }

    def __init__(self, window):
        super().__init__()
        self.window = window
        self.setup_styling()
        self.setup_drag_and_drop()

    def setup_styling(self):
        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        # Note: for custom drag and drop styling, see `:drop(active)` in
        # https://gitlab.gnome.org/GNOME/gtk/-/blob/gtk-3-24/gtk/theme/Adwaita/_common.scss
        #
        # Note: for pixel distances in GNOME UIs, see
        # https://developer.gnome.org/hig/stable/visual-layout.html.en
        css = b"""
        .drop-target {
            border: 3px dashed #2290e9;
            border-radius: 5px;
            margin: 5px;
            box-shadow: none;
        }
        .drop-target:drop(active) {
            border-color: #1dbf68;
            box-shadow: none;
        }
        .drop-target.drop-forbidden:drop(active) {
            border-color: red;
        }
        """
        provider.load_from_data(css)

    def setup_drag_and_drop(self):
        # Note: for instructions for drag'n'drop in GTK3, see
        # http://www.cs.hunter.cuny.edu/~sweiss/course_materials/csci493.70/lecture_notes/GTK_dragndrop.pdf
        target = Gtk.TargetEntry.new("text/uri-list", Gtk.TargetFlags(4), 129)
        self.drag_dest_set(0, [target], Gdk.DragAction.COPY)
        self.connect("drag-motion", self.on_drag_motion)
        self.connect("drag-data-received", self.on_drag_data_received)
        self.connect("drag-leave", self.on_drag_leave)
        self.connect("drag-drop", self.on_drag_drop)
        self.open_dropped_pdf = False

    # @Gtk.Template.Callback(name="on_startscreen_drag_motion")
    def on_drag_motion(self, widget, context, x, y, time):
        self.open_dropped_pdf = False
        widget.drag_highlight()
        widget.drag_get_data(context, Gdk.atom_intern("text/uri-list", False), time)
        return True

    # @Gtk.Template.Callback(name="on_startscreen_drag_data_received")
    def on_drag_data_received(
        self, widget, context, x, y, data, info, time, open_pdf=False
    ):
        filename = unquote(urlparse(data.get_uris()[0]).path)
        if Path(filename).suffix.lower() != ".pdf":
            # don't allow dropping:
            widget.get_style_context().add_class("drop-forbidden")
            widget.get_style_context().remove_class("drop-allowed")
            Gdk.drag_status(context, 0, time)
        else:
            # allow dropping:
            Gdk.drag_status(context, Gdk.DragAction.COPY, time)
            widget.get_style_context().add_class("drop-allowed")
            widget.get_style_context().remove_class("drop-forbidden")
            if self.open_dropped_pdf:
                # open pdf if it has been dropped:
                self.open_dropped_pdf = False
                self.emit("open-pdf", filename)

    # @Gtk.Template.Callback(name="on_startscreen_drag_leave")
    def on_drag_leave(self, widget, context, time):
        print("drag-leave")
        self.open_dropped_pdf = False
        widget.drag_unhighlight()

    # @Gtk.Template.Callback(name="on_startscreen_drag_drop")
    def on_drag_drop(self, widget, context, x, y, time):
        print("drop")
        self.open_dropped_pdf = True
        widget.drag_get_data(context, Gdk.atom_intern("text/uri-list", False), time)
