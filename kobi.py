#!/usr/bin/env python3

import sys
from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import TextArea, Frame
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.layout.processors import HighlightSearchProcessor
from prompt_toolkit.clipboard import ClipboardData
from pygments.lexers import guess_lexer_for_filename
from pygments.util import ClassNotFound

# ---------------- FILE ----------------
filename = sys.argv[1] if len(sys.argv) > 1 else "newfile.txt"

def load_file(name):
    try:
        with open(name, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

content = load_file(filename)

# ---------------- LEXER ----------------
def make_lexer(name, text):
    try:
        pyg = guess_lexer_for_filename(name, text)
        return PygmentsLexer(type(pyg))
    except ClassNotFound:
        return None

lexer = make_lexer(filename, content)

# ---------------- EDITOR ----------------
editor = TextArea(
    text=content,
    scrollbar=True,
    line_numbers=True,
    lexer=lexer,
    wrap_lines=False,
    multiline=True,
    focus_on_click=True,
    input_processors=[HighlightSearchProcessor()]
)

# ---------------- STATUS + HELP ----------------
message = ""

def get_statusbar_text():
    row = editor.document.cursor_position_row + 1
    col = editor.document.cursor_position_col + 1
    return f" {filename} | Ln {row}, Col {col} {message} "

def get_helpbar_text():
    return " ^S Save  ^Q Quit  ^F Find  ^G GoTo  ^C Copy  ^X Cut  ^V Paste  ^Z Undo  ^Y Redo "

status_bar = Window(height=1, content=FormattedTextControl(get_statusbar_text), style="class:status")
help_bar = Window(height=1, content=FormattedTextControl(get_helpbar_text), style="class:help")

# ---------------- STYLE ----------------
style = Style.from_dict({
    "status": "reverse",
    "help": "bg:#444444 #ffffff",
    "frame.border": "#888888",
})

# ---------------- SAVE ----------------
def save_file(name):
    global message
    with open(name, "w", encoding="utf-8") as f:
        f.write(editor.text)
    message = " [Saved]"

# ---------------- KEY BINDINGS ----------------
kb = KeyBindings()

# Ctrl+S Save
@kb.add("c-s")
def _(event):
    save_file(filename)

# Ctrl+Q Quit
@kb.add("c-q")
def _(event):
    event.app.exit()

# Ctrl+F Find
@kb.add("c-f")
def _(event):
    term = input("Find: ")
    if term:
        editor.buffer.search_state.text = term
        editor.buffer.apply_search(highlight=True)

# Ctrl+G Go to line
@kb.add("c-g")
def _(event):
    line_str = input("Go to line: ")
    global message
    if line_str.isdigit():
        line = int(line_str) - 1
        editor.buffer.cursor_position = editor.document.translate_row_col_to_index(line, 0)
        message = f" [Line {line+1}]"

# ---------------- Clipboard ----------------
# Ctrl+C Copy
@kb.add("c-c")
def _(event):
    global message
    buf = editor.buffer
    if buf.selection_state:
        text = buf.document.selection_range_text
        if text:
            event.app.clipboard.set_data(ClipboardData(text))
            message = " [Copied]"
    else:
        message = " [No Selection]"

# Ctrl+X Cut
@kb.add("c-x")
def _(event):
    global message
    buf = editor.buffer
    if buf.selection_state:
        text = buf.document.selection_range_text
        if text:
            event.app.clipboard.set_data(ClipboardData(text))
            buf.delete_selection()
            message = " [Cut]"
    else:
        message = " [No Selection]"

# Ctrl+V Paste
@kb.add("c-v")
def _(event):
    global message
    data = event.app.clipboard.get_data()
    if data and data.text:
        editor.buffer.insert_text(data.text)
        message = " [Pasted]"

# Ctrl+Z Undo
@kb.add("c-z")
def _(event):
    editor.buffer.undo()
    global message
    message = " [Undo]"

# Ctrl+Y Redo
@kb.add("c-y")
def _(event):
    editor.buffer.redo()
    global message
    message = " [Redo]"

# ---------------- LAYOUT ----------------
root = HSplit([
    Frame(editor, title=" Kobi "),
    status_bar,
    help_bar
])

app = Application(
    layout=Layout(root),
    key_bindings=kb,
    style=style,
    full_screen=True,
    mouse_support=True
)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()

'''
Made by Erik W for Poniek Labs Canada
(c) Copyright 2026 Poniek Labs Canada
Do not redistribute.
'''
