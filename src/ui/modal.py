__author__ = 'Massimiliano'
from tkinter import *


class ModalDialog:

    @staticmethod
    def open(master, make_widgets, on_ok, title=None):
        return ModalDialog(master, make_widgets, on_ok, title).__create()

    def __init__(self, master, make_widgets, on_ok, title=None):
        super().__init__()
        self.master = master
        self.make_widgets = make_widgets
        self.on_ok = on_ok
        self.title = title or ""
        self.result = None

    def __ok(self):
        self.result = self.on_ok()
        self.dialog.destroy()

    def __close(self):
        self.result = None
        self.dialog.destroy()

    def __create(self):
        self.dialog = Toplevel(self.master)
        self.root = Frame(self.dialog)
        self.dialog.title(self.title)
        self.make_widgets(self.root)
        button_bar = Frame(self.dialog, padx=5, pady=5)
        Button(button_bar, text="OK", command=self.__ok, width=10).pack(side=LEFT)
        Button(button_bar, text="Cancel", command=self.__close, width=10).pack(side=RIGHT)
        button_bar.pack(side=BOTTOM, ipadx=5, ipady=5)
        self.root.pack(expand=Y, fill=BOTH)
        self.dialog.grab_set()
        self.master.wait_window(self.dialog)
        return self.result
