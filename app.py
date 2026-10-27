
import json
from pathlib import Path
import streamlit as st

FILE = Path(__file__).with_name("notes.json")


def load_notes():
    if FILE.exists():
        try:
            data = json.loads(FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, OSError):
            st.error("Could not read notes.json.")
    return []


def save_notes():
    FILE.write_text(
        json.dumps(st.session_state.notes, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )


if "notes" not in st.session_state:
    st.session_state.notes = load_notes()

st.set_page_config(page_title="Notes Organizer", page_icon="📝", layout="wide")

st.title("📝 Notes Organizer")
st.write("Create, organize, search, and manage your study notes.")

notes = st.session_state.notes

with st.sidebar:
    st.header("Add a Note")
    with st.form("add_note_form", clear_on_submit=True):
        subject = st.text_input("Subject")
        title = st.text_input("Note title")
        content = st.text_area("Note content")
        submitted = st.form_submit_button("Add Note")

        if submitted:
            if subject.strip() and title.strip() and content.strip():
                notes.append({
                    "subject": subject.strip(),
                    "title": title.strip(),
                    "content": content.strip(),
                })
                save_notes()
                st.success("Note added!")
                st.rerun()
            else:
                st.warning("Please complete all fields.")

st.subheader("Your Notes")

search = st.text_input("🔍 Search by title, subject, or content")
subjects = sorted({n.get("subject", "Other") for n in notes})
selected_subject = st.selectbox("Filter by subject", ["All subjects"] + subjects)

filtered_notes = []
for index, note in enumerate(notes):
    text = " ".join([
        str(note.get("subject", "")),
        str(note.get("title", "")),
        str(note.get("content", "")),
    ]).lower()

    if search.lower() in text and (
        selected_subject == "All subjects"
        or note.get("subject", "Other") == selected_subject
    ):
        filtered_notes.append((index, note))

if not filtered_notes:
    st.info("No notes found. Add a note using the sidebar.")
else:
    for index, note in filtered_notes:
        with st.expander(
            f"{note.get('title', 'Untitled')} — {note.get('subject', 'Other')}"
        ):
            st.write(note.get("content", ""))

            with st.form(f"edit_form_{index}"):
                new_subject = st.text_input(
                    "Subject", value=note.get("subject", "")
                )
                new_title = st.text_input(
                    "Title", value=note.get("title", "")
                )
                new_content = st.text_area(
                    "Content", value=note.get("content", "")
                )
                col1, col2 = st.columns(2)
                update = col1.form_submit_button("Update Note")
                delete = col2.form_submit_button("Delete Note")

                if update:
                    if new_subject.strip() and new_title.strip() and new_content.strip():
                        notes[index] = {
                            "subject": new_subject.strip(),
                            "title": new_title.strip(),
                            "content": new_content.strip(),
                        }
                        save_notes()
                        st.success("Note updated!")
                        st.rerun()
                    else:
                        st.warning("Please complete all fields.")

                if delete:
                    notes.pop(index)
                    save_notes()
                    st.success("Note deleted!")
                    st.rerun()
