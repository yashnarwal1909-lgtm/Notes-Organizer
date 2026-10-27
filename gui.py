import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime

FILE = Path(__file__).with_name("notes.json")

notes = []
visible_indices = []
selected_index = None
dark_mode = False


# ---------- Helpers ----------

def now():
    return datetime.now().isoformat(timespec="seconds")


def format_date(value):
    if not value:
        return "Unknown"

    try:
        return datetime.fromisoformat(value).strftime(
            "%d %b %Y, %I:%M %p"
        )
    except (ValueError, TypeError):
        return str(value)


# ---------- Save and load ----------

def save_notes():
    try:
        FILE.write_text(
            json.dumps(notes, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )
        return True
    except OSError as error:
        messagebox.showerror("Save Error", str(error))
        return False


def load_notes():
    global notes

    if FILE.exists():
        try:
            data = json.loads(
                FILE.read_text(encoding="utf-8")
            )

            if not isinstance(data, list):
                raise ValueError(
                    "The notes file must contain a list."
                )

            if not all(isinstance(n, dict) for n in data):
                raise ValueError(
                    "One or more notes have invalid data."
                )

            notes = data

        except (json.JSONDecodeError, OSError, ValueError) as error:
            messagebox.showerror(
                "Load Error",
                f"Could not load notes.json:\n{error}\n\n"
                "Your original file has not been overwritten."
            )
            notes = []
            update_subjects()
            refresh_notes()
            return
    else:
        notes = []

    # Add timestamps to older notes.
    changed = False
    timestamp = now()

    for note in notes:
        if not note.get("created_at"):
            note["created_at"] = timestamp
            changed = True

        if not note.get("updated_at"):
            note["updated_at"] = note["created_at"]
            changed = True

    if changed:
        save_notes()

    update_subjects()
    refresh_notes()


# ---------- Subjects and sorting ----------

def update_subjects():
    subjects = sorted(
        {
            str(note.get("subject", "General"))
            for note in notes
        },
        key=str.lower
    )

    subject_box["values"] = ["All Subjects"] + subjects

    if subject_var.get() not in subject_box["values"]:
        subject_var.set("All Subjects")


def refresh_notes():
    note_list.delete(0, tk.END)
    visible_indices.clear()

    keyword = search_var.get().strip().lower()
    subject = subject_var.get()
    sort_choice = sort_var.get()

    filtered = []

    for index, note in enumerate(notes):
        note_subject = str(note.get("subject", "General"))
        title = str(note.get("title", "Untitled"))
        content = str(note.get("content", ""))

        if subject != "All Subjects" and note_subject != subject:
            continue

        searchable = f"{note_subject} {title} {content}".lower()

        if keyword and keyword not in searchable:
            continue

        filtered.append((index, note))

    if sort_choice == "Title (A-Z)":
        filtered.sort(
            key=lambda item: str(
                item[1].get("title", "")
            ).lower()
        )

    elif sort_choice == "Subject (A-Z)":
        filtered.sort(
            key=lambda item: (
                str(item[1].get("subject", "")).lower(),
                str(item[1].get("title", "")).lower()
            )
        )

    elif sort_choice == "Oldest Updated":
        filtered.sort(
            key=lambda item: item[1].get("updated_at", "")
        )

    else:
        filtered.sort(
            key=lambda item: item[1].get("updated_at", ""),
            reverse=True
        )

    for index, note in filtered:
        title = note.get("title", "Untitled")
        subject_text = note.get("subject", "General")

        note_list.insert(
            tk.END,
            f"{subject_text}  |  {title}"
        )
        visible_indices.append(index)

    count_label.config(text=f"{len(filtered)} note(s)")


# ---------- Form actions ----------

def update_timestamp_display():
    if selected_index is None or selected_index >= len(notes):
        timestamp_label.config(
            text="New note | Timestamps appear after saving."
        )
        return

    note = notes[selected_index]

    timestamp_label.config(
        text=(
            f"Created: {format_date(note.get('created_at'))}\n"
            f"Last updated: {format_date(note.get('updated_at'))}"
        )
    )


def clear_form():
    global selected_index

    selected_index = None

    title_entry.delete(0, tk.END)
    subject_entry.delete(0, tk.END)
    content_text.delete("1.0", tk.END)
    note_list.selection_clear(0, tk.END)

    update_timestamp_display()
    title_entry.focus_set()


def select_note(event=None):
    global selected_index

    selection = note_list.curselection()

    if not selection:
        return

    selected_index = visible_indices[selection[0]]
    note = notes[selected_index]

    title_entry.delete(0, tk.END)
    title_entry.insert(0, note.get("title", ""))

    subject_entry.delete(0, tk.END)
    subject_entry.insert(0, note.get("subject", ""))

    content_text.delete("1.0", tk.END)
    content_text.insert("1.0", note.get("content", ""))

    update_timestamp_display()


def add_note():
    title = title_entry.get().strip()
    subject = subject_entry.get().strip()
    content = content_text.get("1.0", tk.END).strip()

    if not title or not subject or not content:
        messagebox.showwarning(
            "Missing Information",
            "Please enter a title, subject, and note content."
        )
        return

    timestamp = now()

    note = {
        "title": title,
        "subject": subject,
        "content": content,
        "created_at": timestamp,
        "updated_at": timestamp
    }

    notes.append(note)

    if save_notes():
        update_subjects()
        refresh_notes()
        clear_form()
        messagebox.showinfo(
            "Success",
            "Note added successfully!"
        )
    else:
        notes.pop()


def edit_note():
    if selected_index is None:
        messagebox.showwarning(
            "Select a Note",
            "Choose a note from the list first."
        )
        return

    title = title_entry.get().strip()
    subject = subject_entry.get().strip()
    content = content_text.get("1.0", tk.END).strip()

    if not title or not subject or not content:
        messagebox.showwarning(
            "Missing Information",
            "Please fill in all three fields."
        )
        return

    old_note = notes[selected_index]

    updated_note = {
        "title": title,
        "subject": subject,
        "content": content,
        "created_at": old_note.get("created_at", now()),
        "updated_at": now()
    }

    notes[selected_index] = updated_note

    if save_notes():
        update_subjects()
        refresh_notes()
        clear_form()
        messagebox.showinfo(
            "Success",
            "Note updated successfully!"
        )
    else:
        notes[selected_index] = old_note


def delete_note():
    if selected_index is None:
        messagebox.showwarning(
            "Select a Note",
            "Choose a note from the list first."
        )
        return

    if not messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this note?"
    ):
        return

    deleted_note = notes.pop(selected_index)

    if save_notes():
        update_subjects()
        refresh_notes()
        clear_form()
    else:
        notes.insert(selected_index, deleted_note)
        refresh_notes()


# ---------- Theme ----------

def apply_theme():
    bg = "#f3f6fb" if not dark_mode else "#171923"
    panel = "#ffffff" if not dark_mode else "#222635"
    field = "#ffffff" if not dark_mode else "#191d29"
    fg = "#202b3c" if not dark_mode else "#edf1f7"
    muted = "#64748b" if not dark_mode else "#aab4c5"
    accent = "#356ae6" if not dark_mode else "#7197ff"
    border = "#dbe3ef" if not dark_mode else "#3a4255"

    root.configure(bg=bg)

    style.configure(".", font=("Segoe UI", 10))

    style.configure("TFrame", background=bg)
    style.configure("Panel.TFrame", background=panel)

    style.configure(
        "TLabel",
        background=bg,
        foreground=fg
    )

    style.configure(
        "Panel.TLabel",
        background=panel,
        foreground=fg
    )

    style.configure(
        "Title.TLabel",
        background=panel,
        foreground=fg,
        font=("Segoe UI", 22, "bold")
    )

    style.configure(
        "TButton",
        padding=(12, 8),
        background=panel,
        foreground=fg,
        bordercolor=border
    )

    style.map(
        "TButton",
        background=[("active", border)],
        foreground=[("disabled", muted)]
    )

    style.configure(
        "Accent.TButton",
        background=accent,
        foreground="#ffffff",
        padding=(12, 8)
    )

    style.map(
        "Accent.TButton",
        background=[
            (
                "active",
                "#2855bd" if not dark_mode else "#5279df"
            )
        ]
    )

    style.configure(
        "TEntry",
        fieldbackground=field,
        foreground=fg,
        insertcolor=fg,
        bordercolor=border,
        padding=8
    )

    style.configure(
        "TCombobox",
        fieldbackground=field,
        background=panel,
        foreground=fg,
        arrowcolor=fg,
        padding=7
    )

    style.map(
        "TCombobox",
        fieldbackground=[("readonly", field)],
        foreground=[("readonly", fg)]
    )

    style.configure(
        "TLabelframe",
        background=panel,
        foreground=fg,
        bordercolor=border
    )

    style.configure(
        "TLabelframe.Label",
        background=panel,
        foreground=fg,
        font=("Segoe UI", 11, "bold")
    )

    # Apply backgrounds to the main frames.
    for widget in (header, left, toolbar):
        widget.configure(style="Panel.TFrame")

    body.configure(style="TFrame")
    right.configure(style="TLabelframe")

    # Apply label styles.
    for widget in (
        title_label,
        search_label,
        filter_label,
        sort_label,
        saved_label,
        editor_title_label,
        subject_title_label,
        content_title_label
    ):
        widget.configure(style="Panel.TLabel")

    # Style the saved notes list.
    note_list.configure(
        bg=field,
        fg=fg,
        selectbackground=accent,
        selectforeground="#ffffff",
        highlightbackground=border,
        highlightcolor=accent,
        relief="flat",
        highlightthickness=1
    )

    # Style the note content editor.
    content_text.configure(
        bg=field,
        fg=fg,
        insertbackground=fg,
        selectbackground=accent,
        selectforeground="#ffffff",
        highlightbackground=border,
        highlightcolor=accent,
        relief="flat",
        highlightthickness=1
    )

    # Style timestamp and note count labels.
    timestamp_label.configure(
        bg=panel,
        fg=muted
    )

    count_label.configure(
        bg=panel,
        fg=muted
    )

    theme_button.configure(
        text="☀ Light mode" if dark_mode else "☾ Dark mode"
    )


def toggle_theme():
    global dark_mode

    dark_mode = not dark_mode
    apply_theme()


# ---------- Main window ----------

root = tk.Tk()
root.title("Notes Organizer")
root.geometry("1100x720")
root.minsize(820, 560)

style = ttk.Style()
style.theme_use("clam")

# Header
header = ttk.Frame(root, padding=(22, 18))
header.pack(fill="x")

title_label = ttk.Label(
    header,
    text="My Notes Organizer",
    style="Title.TLabel"
)
title_label.pack(side="left")

theme_button = ttk.Button(
    header,
    text="☾ Dark mode",
    command=toggle_theme
)
theme_button.pack(side="right", padx=(10, 0))

search_var = tk.StringVar()

search_entry = ttk.Entry(
    header,
    textvariable=search_var,
    width=25
)
search_entry.pack(side="right", padx=(8, 5))

search_label = ttk.Label(
    header,
    text="Search",
    style="Panel.TLabel"
)
search_label.pack(side="right")

search_var.trace_add(
    "write",
    lambda *_: refresh_notes()
)

# Main body
body = ttk.Frame(root, padding=(22, 0, 22, 20))
body.pack(fill="both", expand=True)

# Left panel
left = ttk.Frame(body, padding=15)
left.pack(side="left", fill="y")

filter_label = ttk.Label(
    left,
    text="FILTER BY SUBJECT",
    style="Panel.TLabel"
)
filter_label.pack(anchor="w", pady=(0, 6))

subject_var = tk.StringVar(value="All Subjects")

subject_box = ttk.Combobox(
    left,
    textvariable=subject_var,
    state="readonly",
    width=24
)
subject_box.pack(fill="x", pady=(0, 18))

subject_box.bind(
    "<<ComboboxSelected>>",
    lambda event: refresh_notes()
)

sort_label = ttk.Label(
    left,
    text="SORT NOTES",
    style="Panel.TLabel"
)
sort_label.pack(anchor="w", pady=(0, 6))

sort_var = tk.StringVar(value="Recently Updated")

sort_box = ttk.Combobox(
    left,
    textvariable=sort_var,
    state="readonly",
    values=[
        "Recently Updated",
        "Oldest Updated",
        "Title (A-Z)",
        "Subject (A-Z)"
    ],
    width=24
)
sort_box.pack(fill="x", pady=(0, 18))

sort_box.bind(
    "<<ComboboxSelected>>",
    lambda event: refresh_notes()
)

saved_label = ttk.Label(
    left,
    text="SAVED NOTES",
    style="Panel.TLabel"
)
saved_label.pack(anchor="w", pady=(0, 6))

note_list = tk.Listbox(
    left,
    width=32,
    height=20,
    font=("Segoe UI", 10),
    selectmode=tk.SINGLE,
    exportselection=False,
    activestyle="none",
    borderwidth=0,
    highlightthickness=1
)
note_list.pack(fill="both", expand=True)

note_list.bind(
    "<<ListboxSelect>>",
    select_note
)

count_label = tk.Label(
    left,
    text="0 note(s)",
    anchor="w",
    font=("Segoe UI", 9),
    padx=2,
    pady=8
)
count_label.pack(fill="x")

# Right editor panel
right = ttk.LabelFrame(
    body,
    text="  Note Editor  ",
    padding=18
)
right.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(18, 0)
)

editor_title_label = ttk.Label(
    right,
    text="NOTE TITLE",
    style="Panel.TLabel"
)
editor_title_label.pack(anchor="w")

title_entry = ttk.Entry(right)
title_entry.pack(fill="x", pady=(6, 14))

subject_title_label = ttk.Label(
    right,
    text="SUBJECT",
    style="Panel.TLabel"
)
subject_title_label.pack(anchor="w")

subject_entry = ttk.Entry(right)
subject_entry.pack(fill="x", pady=(6, 14))

content_title_label = ttk.Label(
    right,
    text="NOTE CONTENT",
    style="Panel.TLabel"
)
content_title_label.pack(anchor="w")

content_text = tk.Text(
    right,
    height=12,
    wrap="word",
    font=("Segoe UI", 11),
    padx=10,
    pady=10,
    undo=True,
    borderwidth=0,
    highlightthickness=1
)
content_text.pack(
    fill="both",
    expand=True,
    pady=(6, 12)
)

timestamp_label = tk.Label(
    right,
    text="New note | Timestamps appear after saving.",
    justify="left",
    anchor="w",
    font=("Segoe UI", 9),
    padx=2,
    pady=5
)
timestamp_label.pack(fill="x", pady=(0, 10))

toolbar = ttk.Frame(right)
toolbar.pack(fill="x")

ttk.Button(
    toolbar,
    text="Add Note",
    style="Accent.TButton",
    command=add_note
).pack(side="left", padx=(0, 6))

ttk.Button(
    toolbar,
    text="Update",
    command=edit_note
).pack(side="left", padx=6)

ttk.Button(
    toolbar,
    text="Delete",
    command=delete_note
).pack(side="left", padx=6)

ttk.Button(
    toolbar,
    text="Clear",
    command=clear_form
).pack(side="right")

# ---------- Start application ----------

apply_theme()
load_notes()

root.mainloop()
