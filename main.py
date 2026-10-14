
import json
from pathlib import Path

FILE = Path(__file__).with_name("notes.json")


def load_notes():
    if FILE.exists():
        try:
            return json.loads(FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            print("Could not read notes.json.")
    return []


def save_notes(notes):
    FILE.write_text(
        json.dumps(notes, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )


def add_note(notes):
    subject = input("Enter subject: ").strip()
    title = input("Enter note title: ").strip()
    content = input("Enter note content: ").strip()

    if not subject or not title or not content:
        print("All fields are required.")
        return

    notes.append({
        "subject": subject,
        "title": title,
        "content": content
    })
    save_notes(notes)
    print("Note added successfully!")


def view_notes(notes):
    if not notes:
        print("No notes saved yet.")
        return

    for i, note in enumerate(notes, start=1):
        print(f"\n{i}. [{note['subject']}] {note['title']}")
        print(note["content"])


def edit_note(notes):
    view_notes(notes)
    if not notes:
        return

    try:
        number = int(input("\nEnter note number to edit: "))
        if not 1 <= number <= len(notes):
            print("Invalid note number.")
            return
    except ValueError:
        print("Please enter a valid number.")
        return

    note = notes[number - 1]
    subject = input(f"Subject [{note['subject']}]: ").strip()
    title = input(f"Title [{note['title']}]: ").strip()
    content = input("New content (leave blank to keep current): ").strip()

    if subject:
        note["subject"] = subject
    if title:
        note["title"] = title
    if content:
        note["content"] = content

    save_notes(notes)
    print("Note updated successfully!")


def search_notes(notes):
    keyword = input("Search by title, subject, or content: ").strip().lower()
    results = [
        note for note in notes
        if keyword and any(
            keyword in note[field].lower()
            for field in ("subject", "title", "content")
        )
    ]

    view_notes(results)


def main():
    notes = load_notes()

    while True:
        print("\n===== NOTES ORGANIZER =====")
        print("1. Add note")
        print("2. View all notes")
        print("3. Edit note")
        print("4. Search notes")
        print("5. Exit")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            add_note(notes)
        elif choice == "2":
            view_notes(notes)
        elif choice == "3":
            edit_note(notes)
        elif choice == "4":
            search_notes(notes)
        elif choice == "5":
            print("Thank you for using Notes Organizer!")
            break
        else:
            print("Invalid choice. Please choose 1-5.")


if __name__ == "__main__":
    main()
