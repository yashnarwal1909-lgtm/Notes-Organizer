
import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

FILE = Path(__file__).with_name("notes.json")
notes = []
selected_index = None


def load_notes():
    global notes
    if FILE.exists():
        try:
            notes = json.loads(FILE.read_text(encoding="utf-8"))
            if not isinstance(notes, list):
                notes = []
        except (json.JSONDecodeError, OSError):
            notes = []
    refresh_notes()


def save_notes():
    try:
        FILE.write_text(
            json.dumps(notes, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )
    except OSError as error:
        messagebox.showerror("Save Error", str(error))


def refresh_notes():
    note_list.delete(0, tk.END)
    keyword = search_var.get().strip().lower()
    subject = subject_var.get()

    for index, note in enumerate(notes):
        if subject != "All Subjects" and note.get("subject") != subject:
            continue

        searchable = (
            note.get("subject", "") + " " +
            note.get("title", "") + " " +
            note.get("content", "")
        ).lower()

        if keyword and keyword not in searchable:
            continue

        note_list.insert(
            tk.END,
            f"{note.get('subject', 'General')} - "
            f"{note.get('title', 'Untitled')}"
        )
        # Keep the original note index for editing.
        visible_indices.append(index)


def update_subjects():
    subjects = sorted({
        note.get("subject", "General")
        for note in notes
    })
    subject_box["values"] = ["All Subjects"] + subjects
    if subject_var.get() not in subject_box["values"]:
        subject_var.set("All Subjects")


def refresh_notes():
    note_list.delete(0, tk.END)
    visible_indices.clear()
    keyword = search_var.get().strip().lower()
    subject = subject_var.get()

    for index, note in enumerate(notes):
        if subject != "All Subjects" and note.get("subject") != subject:
            continue

        searchable = (
            note.get("subject", "") + " " +
            note.get("title", "") + " " +
            note.get("content", "")
        ).lower()

        if keyword and keyword not in searchable:
            continue

        note_list.insert(
            tk.END,
            f"{note.get('subject', 'General')} - "
            f"{note.get('title', 'Untitled')}"
        )
        visible_indices.append(index)


def clear_form():
    global selected_index
    selected_index = None
    title_entry.delete(0, tk.END)
    subject_entry.delete(0, tk.END)
    content_text.delete("1.0", tk.END)
    note_list.selection_clear(0, tk.END)


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

    notes.append({
        "title": title,
        "subject": subject,
        "content": content
    })
    save_notes()
    update_subjects()
    refresh_notes()
    clear_form()
    messagebox.showinfo("Success", "Note added successfully!")


def edit_note():
    if selected_index is None:
        messagebox.showwarning(
            "Select a Note", "Choose a note from the list first."
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

    notes[selected_index] = {
        "title": title,
        "subject": subject,
        "content": content
    }
    save_notes()
    update_subjects()
    refresh_notes()
    clear_form()
    messagebox.showinfo("Success", "Note updated successfully!")


def delete_note():
    if selected_index is None:
        messagebox.showwarning(
            "Select a Note", "Choose a note from the list first."
        )
        return

    if messagebox.askyesno(
        "Confirm Delete", "Are you sure you want to delete this note?"
    ):
        notes.pop(selected_index)
        save_notes()
        update_subjects()
        refresh_notes()
        clear_form()


root = tk.Tk()
root.title("Notes Organizer")
root.geometry("950x620")
root.minsize(750, 500)

root.configure(bg="#f3f5f9")
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", padding=7, font=("Segoe UI", 10))
style.configure("TLabel", background="#f3f5f9", font=("Segoe UI", 10))
style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
style.configure("Tree.TLabel", font=("Segoe UI", 11))

visible_indices = []

header = ttk.Frame(root, padding=15)
header.pack(fill="x")
ttk.Label(
    header, text="My Notes Organizer", style="Title.TLabel"
).pack(side="left")

search_var = tk.StringVar()
search_entry = ttk.Entry(header, textvariable=search_var, width=28)
search_entry.pack(side="right", padx=5)
ttk.Label(header, text="Search:").pack(side="right")
search_var.trace_add("write", lambda *_: refresh_notes())

body = ttk.Frame(root, padding=(15, 0, 15, 15))
body.pack(fill="both", expand=True)

left = ttk.Frame(body, padding=10)
left.pack(side="left", fill="y")

ttk.Label(left, text="Filter by subject").pack(anchor="w")
subject_var = tk.StringVar(value="All Subjects")
subject_box = ttk.Combobox(
    left, textvariable=subject_var, state="readonly", width=22
)
subject_box.pack(fill="x", pady=(5, 15))
subject_box.bind("<<ComboboxSelected>>", lambda event: refresh_notes())

ttk.Label(left, text="Saved Notes").pack(anchor="w")
note_list = tk.Listbox(
    left, width=34, height=20, font=("Segoe UI", 10),
    selectmode=tk.SINGLE, exportselection=False
)
note_list.pack(fill="both", expand=True, pady=5)
note_list.bind("<<ListboxSelect>>", select_note)

right = ttk.LabelFrame(body, text="Note Details", padding=15)
right.pack(side="left", fill="both", expand=True, padx=(15, 0))

ttk.Label(right, text="Note Title").pack(anchor="w")
title_entry = ttk.Entry(right)
title_entry.pack(fill="x", pady=(5, 12))

ttk.Label(right, text="Subject").pack(anchor="w")
subject_entry = ttk.Entry(right)
subject_entry.pack(fill="x", pady=(5, 12))

ttk.Label(right, text="Note Content").pack(anchor="w")
content_text = tk.Text(
    right, height=12, wrap="word", font=("Segoe UI", 11)
)
content_text.pack(fill="both", expand=True, pady=(5, 12))

buttons = ttk.Frame(right)
buttons.pack(fill="x")

ttk.Button(buttons, text="Add Note", command=add_note).pack(
    side="left", padx=(0, 6)
)
ttk.Button(buttons, text="Update Note", command=edit_note).pack(
    side="left", padx=6
)
ttk.Button(buttons, text="Delete Note", command=delete_note).pack(
    side="left", padx=6
)
ttk.Button(buttons, text="Clear", command=clear_form).pack(
    side="right"
)

load_notes()
root.mainloop()
