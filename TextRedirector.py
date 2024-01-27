import tkinter as tk

class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, str):
        self.widget.insert(tk.END, str)
        self.widget.see(tk.END)  # Auto-scroll to the end

    def flush(self):
        pass  # Required for compatibility with sys.stdout
