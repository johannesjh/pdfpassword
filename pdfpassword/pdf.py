import logging
import os
from pathlib import Path

import cairo
import gi

gi.require_versions({"Gtk": "3.0", "Poppler": "0.18"})
from gi.repository import GObject, Poppler
from pikepdf import Encryption, PasswordError
from pikepdf import Pdf as PikePdf
from pikepdf import PdfError

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))


def human_size(num, suffix="B"):
    # from: https://stackoverflow.com/a/1094933
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return "{:.1f}{}{}".format(num, "Yi", suffix)


class Pdf(GObject.GObject):

    filename = GObject.Property(type=str)
    file_size = GObject.Property(type=int)
    file_size_human = GObject.Property(type=str)
    file_password_protected = GObject.Property(type=bool, default=False)
    file_password_missing = GObject.Property(type=bool, default=False)
    file_password_wrong = GObject.Property(type=bool, default=False)
    file_error = GObject.Property(type=str)
    thumbnail = None

    confirmation_image = GObject.Property(type=str)
    confirmation_filename = GObject.Property(type=str)

    def __init__(self, filename=None):
        super().__init__()
        if filename:
            self.open_pdf(filename)

    def open_pdf(self, filename, password=None):
        # verify that the file exists:
        self.path = Path(filename)
        if not self.path.exists():
            self.file_error = "File does not exist."

        # remember the filename:
        self.filename = self.path.name

        # read file size
        self.file_size = self.path.stat().st_size
        self.file_size_human = human_size(self.file_size)

        # try opening the pdf without a password
        # in order to check if the file is password-protected
        try:
            print(f"trying to open {self.filename} without pw...")
            self.file_password_protected = False
            self.file_password_missing = False
            self.file_password_wrong = False
            self.pike_pdf = PikePdf.open(filename)
        except PasswordError:
            self.file_password_protected = True
            self.file_password_missing = True
            self.file_password_wrong = False
        except PdfError:
            self.file_error = "Error reading PDF file."

        # try opening the pdf using a password:
        if self.file_password_protected and password:
            try:
                print(f"trying to open {self.filename} with pw...")
                self.file_password_protected = True
                self.file_password_missing = False
                self.file_password_wrong = False
                self.pike_pdf = PikePdf.open(filename, password=password)
                print(f"successfully opened {self.filename}")
            except PasswordError:
                self.file_password_protected = True
                self.file_password_missing = False
                self.file_password_wrong = True
            except PdfError:
                self.file_error = "Error reading PDF file."

        # generate PFD thumbnail
        # Note: for rendering of PDF pages to a thumbnail, see
        # https://github.com/pdfarranger/pdfarranger/blob/0a14f24a9d75d974fb3b6370688d9d92d04b382b/pdfarranger/core.py#L41
        if self.file_password_missing or self.file_password_wrong:
            return
        try:
            poppler_pw = password or ""
            poppler_pdf = Poppler.Document.new_from_file(self.path.as_uri(), poppler_pw)
            page = poppler_pdf.get_page(0)
            w, h = page.get_size()
            source_size = max(w, h)
            dest_size = 200
            scale = dest_size / source_size
            self.thumbnail = cairo.ImageSurface(
                cairo.FORMAT_ARGB32, round(w * scale), round(h * scale)
            )
            cr = cairo.Context(self.thumbnail)
            cr.scale(scale, scale)
            page.render(cr)
        except Exception:
            print("could not render thumbnail")
            self.thumbnail = None

    def save_encrypted(self, password):
        path = self.path.parent / (str(self.path.stem) + "_enc" + self.path.suffix)
        self.pike_pdf.save(
            str(path), encryption=Encryption(user=password, owner=password, R=6)
        )
        self.pike_pdf.close()
        self.confirmation_image = "gtk-ok"
        self.confirmation_path = path
        self.confirmation_filename = path.name
        print(f"wrote {path.name} with password protection.")

    def save_decrypted(self):
        path = self.path.parent / (str(self.path.stem) + "_dec" + self.path.suffix)
        self.pike_pdf.save(str(path))
        self.pike_pdf.close()
        self.confirmation_image = "gtk-ok"
        self.confirmation_path = path
        self.confirmation_filename = path.name
        print(f"wrote {path.name} without password protection.")
