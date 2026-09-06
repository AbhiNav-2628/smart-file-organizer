import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path
import json
import shutil
from datetime import datetime


# ============================================================
# FILE PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

CATEGORIES_FILE = BASE_DIR / "categories.json"
LOG_FILE = BASE_DIR / "organizer_log.txt"
BACKUP_FOLDER = BASE_DIR / ".organizer_backups"


# ============================================================
# DEFAULT CATEGORIES
# ============================================================

DEFAULT_CATEGORIES = {
    # Documents
    ".txt": "Documents",
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".rtf": "Documents",
    ".odt": "Documents",

    # Spreadsheets
    ".xls": "Spreadsheets",
    ".xlsx": "Spreadsheets",
    ".csv": "Spreadsheets",
    ".ods": "Spreadsheets",

    # Presentations
    ".ppt": "Presentations",
    ".pptx": "Presentations",
    ".odp": "Presentations",

    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".bmp": "Images",
    ".webp": "Images",
    ".svg": "Images",
    ".ico": "Images",
    ".tiff": "Images",

    # Music
    ".mp3": "Music",
    ".wav": "Music",
    ".flac": "Music",
    ".aac": "Music",
    ".ogg": "Music",
    ".m4a": "Music",

    # Videos
    ".mp4": "Videos",
    ".mkv": "Videos",
    ".avi": "Videos",
    ".mov": "Videos",
    ".wmv": "Videos",
    ".webm": "Videos",

    # Archives
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",

    # Programs
    ".exe": "Programs",
    ".msi": "Programs",
    ".apk": "Programs",
    ".deb": "Programs",

    # Code
    ".py": "Code",
    ".c": "Code",
    ".cpp": "Code",
    ".h": "Code",
    ".hpp": "Code",
    ".java": "Code",
    ".js": "Code",
    ".ts": "Code",
    ".css": "Code",
    ".php": "Code",
    ".rb": "Code",
    ".go": "Code",
    ".rs": "Code",
    ".sh": "Code",

    # Web
    ".html": "Web",
    ".htm": "Web",
    ".json": "Web",
    ".xml": "Web",

    # Fonts
    ".ttf": "Fonts",
    ".otf": "Fonts",
    ".woff": "Fonts",
    ".woff2": "Fonts",

    # 3D Models
    ".obj": "3D Models",
    ".fbx": "3D Models",
    ".stl": "3D Models",
    ".blend": "3D Models",

    # Disk Images
    ".iso": "Disk Images",
    ".img": "Disk Images",

    # Other
    ".xyz": "Others"
}


# ============================================================
# LOAD / SAVE CATEGORIES
# ============================================================

def save_categories(data):
    try:
        with open(CATEGORIES_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except Exception as error:
        messagebox.showerror(
            "Categories Error",
            f"Could not save categories.json:\n\n{error}"
        )


def load_categories():
    try:
        if CATEGORIES_FILE.exists():

            with open(
                CATEGORIES_FILE,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            if isinstance(data, dict):

                # Preserve user's existing mappings.
                # Only add defaults that are missing.
                changed = False

                for extension, category in DEFAULT_CATEGORIES.items():

                    if extension not in data:
                        data[extension] = category
                        changed = True

                if changed:
                    save_categories(data)

                return data

    except Exception as error:

        messagebox.showerror(
            "Categories Error",
            f"Could not load categories.json:\n\n{error}"
        )

    data = DEFAULT_CATEGORIES.copy()

    save_categories(data)

    return data


categories = load_categories()


# ============================================================
# GLOBAL STATE
# ============================================================

selected_folder = None


# ============================================================
# CATEGORY
# ============================================================

def get_category(file_path):

    extension = file_path.suffix.lower()

    return categories.get(
        extension,
        "Others"
    )


# ============================================================
# FILE DATE
# ============================================================

def get_file_date(file_path):

    try:

        stat = file_path.stat()

        if hasattr(stat, "st_birthtime"):
            return datetime.fromtimestamp(
                stat.st_birthtime
            )

        return datetime.fromtimestamp(
            stat.st_ctime
        )

    except Exception:

        return datetime.now()


# ============================================================
# UNIQUE DESTINATION
# ============================================================

def get_unique_destination(destination):

    if not destination.exists():
        return destination

    counter = 1

    while True:

        new_destination = (
            destination.parent
            / f"{destination.stem}_{counter}{destination.suffix}"
        )

        if not new_destination.exists():
            return new_destination

        counter += 1


# ============================================================
# PROTECTED FILES
# ============================================================

def is_protected_file(file_path):

    try:

        resolved = file_path.resolve()

        protected_files = {
            LOG_FILE.resolve(),
            CATEGORIES_FILE.resolve(),
            BACKUP_FOLDER.resolve(),
            Path(__file__).resolve()
        }

        # Directly protected files
        if resolved in protected_files:
            return True

        # Everything inside backup folder
        if BACKUP_FOLDER.resolve() in resolved.parents:
            return True

        return False

    except Exception:

        return False


# ============================================================
# BACKUP
# ============================================================

def create_backup(destination):

    try:

        BACKUP_FOLDER.mkdir(
            parents=True,
            exist_ok=True
        )

        backup_path = get_unique_destination(
            BACKUP_FOLDER / destination.name
        )

        shutil.copy2(
            destination,
            backup_path
        )

        return backup_path

    except Exception:

        return None


# ============================================================
# LOGGING
# ============================================================

def log_message(message):

    try:

        with open(
            LOG_FILE,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                message + "\n"
            )

    except Exception:
        pass


# ============================================================
# READ LAST RUN
# ============================================================

def read_last_run():

    result = {
        "moved": [],
        "backups": []
    }

    if not LOG_FILE.exists():
        return result

    try:

        with open(
            LOG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            lines = file.readlines()

        for line in reversed(lines):

            line = line.strip()

            # Stop at the beginning of the latest run
            if line == "RUN START":
                break

            # -----------------------------------------------
            # MOVED
            # -----------------------------------------------

            if line.startswith("MOVED | "):

                parts = line.split(
                    " | ",
                    2
                )

                if len(parts) == 3:

                    source = Path(
                        parts[1]
                    )

                    destination = Path(
                        parts[2]
                    )

                    result["moved"].insert(
                        0,
                        (
                            source,
                            destination
                        )
                    )

            # -----------------------------------------------
            # BACKUP
            # -----------------------------------------------

            elif line.startswith("BACKUP | "):

                parts = line.split(
                    " | ",
                    2
                )

                if len(parts) == 3:

                    destination = Path(
                        parts[1]
                    )

                    backup = Path(
                        parts[2]
                    )

                    result["backups"].insert(
                        0,
                        (
                            destination,
                            backup
                        )
                    )

    except Exception:
        pass

    return result


# ============================================================
# CHECK UNDO
# ============================================================

def has_restorable_files():

    last_run = read_last_run()

    return (
        len(last_run["moved"]) > 0
        or len(last_run["backups"]) > 0
    )


# ============================================================
# UPDATE UNDO BUTTON
# ============================================================

def update_undo_button_state():

    if has_restorable_files():

        undo_button.config(
            state="normal"
        )

    else:

        undo_button.config(
            state="disabled"
        )


# ============================================================
# SELECT FOLDER
# ============================================================

def select_folder():

    global selected_folder

    folder = filedialog.askdirectory(
        title="Select Folder"
    )

    if not folder:
        return

    selected_folder = Path(folder)

    folder_label.config(
        text=str(selected_folder)
    )

    select_button.config(
        state="disabled"
    )

    change_button.config(
        state="normal"
    )

    organize_button.config(
        state="normal"
    )

    # IMPORTANT:
    # Selecting a folder must NOT automatically
    # disable Undo.
    update_undo_button_state()


# ============================================================
# CHANGE FOLDER
# ============================================================

def change_folder():

    global selected_folder

    folder = filedialog.askdirectory(
        title="Change Folder"
    )

    if not folder:
        return

    selected_folder = Path(folder)

    folder_label.config(
        text=str(selected_folder)
    )

    organize_button.config(
        state="normal"
    )

    update_undo_button_state()


# ============================================================
# ORGANIZATION PREVIEW
# ============================================================

def organize_files():

    if selected_folder is None:

        messagebox.showwarning(
            "No Folder",
            "Please select a folder first."
        )

        return

    # Get only files in the selected folder.
    # Subfolders are not scanned.
    files = [
        file_path
        for file_path in selected_folder.iterdir()
        if file_path.is_file()
        and not is_protected_file(file_path)
    ]

    if not files:

        messagebox.showinfo(
            "Nothing to Organize",
            "No files found to organize."
        )

        return

    preview = []

    category_counts = {}

    for file_path in files:

        category = get_category(
            file_path
        )

        destination = (
            selected_folder
            / category
            / file_path.name
        )

        preview.append(
            (
                file_path,
                category,
                destination
            )
        )

        category_counts[category] = (
            category_counts.get(
                category,
                0
            ) + 1
        )

    # ========================================================
    # PREVIEW WINDOW
    # ========================================================

    preview_window = tk.Toplevel(
        root
    )

    preview_window.title(
        "Organization Preview"
    )

    preview_window.geometry(
        "850x700"
    )

    preview_window.minsize(
        700,
        550
    )

    preview_window.resizable(
        True,
        True
    )

    # ========================================================
    # MAIN FRAME
    # ========================================================

    main_frame = tk.Frame(
        preview_window,
        padx=15,
        pady=15
    )

    main_frame.pack(
        fill="both",
        expand=True
    )

    # ========================================================
    # TITLE
    # ========================================================

    tk.Label(
        main_frame,
        text="Organization Preview",
        font=("Arial", 18, "bold")
    ).pack(
        anchor="w"
    )

    tk.Label(
        main_frame,
        text=f"Total files: {len(files)}",
        font=("Arial", 10)
    ).pack(
        anchor="w",
        pady=(2, 8)
    )

    # ========================================================
    # CATEGORY SUMMARY
    # ========================================================

    summary_frame = tk.LabelFrame(
        main_frame,
        text="Category Summary",
        padx=8,
        pady=8
    )

    summary_frame.pack(
        fill="x",
        pady=(0, 8)
    )

    summary_list_frame = tk.Frame(
        summary_frame
    )

    summary_list_frame.pack(
        fill="x"
    )

    summary_scrollbar = tk.Scrollbar(
        summary_list_frame,
        orient="vertical"
    )

    summary_listbox = tk.Listbox(
        summary_list_frame,
        height=5,
        yscrollcommand=summary_scrollbar.set
    )

    summary_scrollbar.config(
        command=summary_listbox.yview
    )

    summary_listbox.pack(
        side="left",
        fill="x",
        expand=True
    )

    summary_scrollbar.pack(
        side="right",
        fill="y"
    )

    for category in sorted(
        category_counts
    ):

        count = category_counts[
            category
        ]

        summary_listbox.insert(
            tk.END,
            f"{category}: {count} file(s)"
        )

    # ========================================================
    # FILE DETAILS
    # ========================================================

    details_frame = tk.LabelFrame(
        main_frame,
        text="File Details",
        padx=8,
        pady=8
    )

    # Expandable section.
    # It uses available space without pushing
    # the buttons off-screen.
    details_frame.pack(
        fill="both",
        expand=True,
        pady=(0, 8)
    )

    details_text_frame = tk.Frame(
        details_frame
    )

    details_text_frame.pack(
        fill="both",
        expand=True
    )

    details_scrollbar = tk.Scrollbar(
        details_text_frame,
        orient="vertical"
    )

    details_text = tk.Text(
        details_text_frame,
        wrap="word",
        yscrollcommand=details_scrollbar.set
    )

    details_scrollbar.config(
        command=details_text.yview
    )

    details_text.pack(
        side="left",
        fill="both",
        expand=True
    )

    details_scrollbar.pack(
        side="right",
        fill="y"
    )

    for (
        file_path,
        category,
        destination
    ) in preview:

        details_text.insert(
            tk.END,
            f"File: {file_path.name}\n"
        )

        details_text.insert(
            tk.END,
            f"Category: {category}\n"
        )

        details_text.insert(
            tk.END,
            f"Destination: {destination}\n"
        )

        details_text.insert(
            tk.END,
            "-" * 80 + "\n\n"
        )

    details_text.config(
        state="disabled"
    )

    # ========================================================
    # BUTTON FRAME
    # ========================================================

    # IMPORTANT:
    # This frame is outside the expanding details area.
    # Therefore these buttons remain visible.
    button_frame = tk.Frame(
        main_frame
    )

    button_frame.pack(
        fill="x",
        side="bottom"
    )

    # ========================================================
    # ORGANIZE CONFIRMATION
    # ========================================================

    def organize_confirmed():

        preview_window.destroy()

        perform_organization(
            preview
        )

    # ========================================================
    # ORGANIZE BUTTON
    # ========================================================

    tk.Button(
        button_frame,
        text="ORGANIZE",
        width=15,
        command=organize_confirmed
    ).pack(
        side="left",
        padx=(0, 10)
    )

    # ========================================================
    # CANCEL BUTTON
    # ========================================================

    tk.Button(
        button_frame,
        text="CANCEL",
        width=15,
        command=preview_window.destroy
    ).pack(
        side="left"
    )

    preview_window.transient(
        root
    )

    preview_window.grab_set()


# ============================================================
# PERFORM ORGANIZATION
# ============================================================

def perform_organization(preview):

    moved_count = 0
    skipped_count = 0
    failed_count = 0

    log_message("")

    log_message(
        "RUN START"
    )

    log_message(
        f"FOLDER | {selected_folder}"
    )

    log_message(
        f"TIME | "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # ========================================================
    # PROCESS FILES
    # ========================================================

    for (
        file_path,
        category,
        destination
    ) in preview:

        try:

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            # =================================================
            # DUPLICATE
            # =================================================

            if destination.exists():

                choice = messagebox.askyesnocancel(
                    "Duplicate File",

                    f"A file named:\n\n"
                    f"{destination.name}\n\n"
                    f"already exists in:\n"
                    f"{destination.parent}\n\n"
                    f"YES = Replace\n"
                    f"NO = Rename\n"
                    f"CANCEL = Skip"
                )

                # ---------------------------------------------
                # CANCEL
                # ---------------------------------------------

                if choice is None:

                    skipped_count += 1

                    log_message(
                        f"SKIPPED | {file_path} | "
                        f"Duplicate cancelled"
                    )

                    continue

                # ---------------------------------------------
                # REPLACE
                # ---------------------------------------------

                elif choice is True:

                    backup_path = create_backup(
                        destination
                    )

                    if backup_path is None:

                        failed_count += 1

                        log_message(
                            f"FAILED | {file_path} | "
                            f"Could not create backup"
                        )

                        continue

                    log_message(
                        f"BACKUP | "
                        f"{destination} | "
                        f"{backup_path}"
                    )

                    destination.unlink()

                # ---------------------------------------------
                # RENAME
                # ---------------------------------------------

                else:

                    destination = (
                        get_unique_destination(
                            destination
                        )
                    )

            # =================================================
            # MOVE
            # =================================================

            shutil.move(
                str(file_path),
                str(destination)
            )

            moved_count += 1

            log_message(
                f"MOVED | "
                f"{file_path} | "
                f"{destination}"
            )

        except Exception as error:

            failed_count += 1

            log_message(
                f"FAILED | "
                f"{file_path} | "
                f"{error}"
            )

    # ========================================================
    # END RUN
    # ========================================================

    log_message(
        f"RUN END | "
        f"Moved={moved_count} "
        f"Skipped={skipped_count} "
        f"Failed={failed_count}"
    )

    update_undo_button_state()

    messagebox.showinfo(
        "Organization Complete",

        f"Files organized: {moved_count}\n"
        f"Skipped: {skipped_count}\n"
        f"Failed: {failed_count}"
    )


# ============================================================
# UNDO
# ============================================================

def undo_last_run():

    last_run = read_last_run()

    moved_items = last_run["moved"]

    backup_items = last_run["backups"]

    if not moved_items and not backup_items:

        messagebox.showinfo(
            "Undo",
            "There is nothing to undo."
        )

        update_undo_button_state()

        return

    confirm = messagebox.askyesno(
        "Undo Last Run",

        "Undo the last organization run?\n\n"
        "All files from the last run will be restored."
    )

    if not confirm:
        return

    restored = 0
    already_restored = 0
    failed = 0

    # ========================================================
    # RESTORE MOVED FILES
    # ========================================================

    for (
        source,
        destination
    ) in reversed(moved_items):

        try:

            # Destination no longer exists.
            if not destination.exists():

                already_restored += 1

                continue

            source.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            # Original location already occupied.
            if source.exists():

                failed += 1

                continue

            shutil.move(
                str(destination),
                str(source)
            )

            restored += 1

        except Exception:

            failed += 1

    # ========================================================
    # RESTORE BACKUPS
    # ========================================================

    for (
        destination,
        backup
    ) in reversed(backup_items):

        try:

            if not backup.exists():
                continue

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            if destination.exists():
                destination.unlink()

            shutil.move(
                str(backup),
                str(destination)
            )

        except Exception:

            failed += 1

    # ========================================================
    # REMOVE EMPTY BACKUP FOLDER
    # ========================================================

    try:

        if BACKUP_FOLDER.exists():

            remaining = list(
                BACKUP_FOLDER.iterdir()
            )

            if not remaining:

                BACKUP_FOLDER.rmdir()

    except Exception:
        pass

    update_undo_button_state()

    messagebox.showinfo(
        "Undo Complete",

        f"Files restored: {restored}\n"
        f"Already restored: {already_restored}\n"
        f"Failed: {failed}"
    )


# ============================================================
# SETTINGS
# ============================================================

def open_settings():

    settings_window = tk.Toplevel(
        root
    )

    settings_window.title(
        "Settings"
    )

    settings_window.geometry(
        "600x500"
    )

    settings_window.minsize(
        500,
        400
    )

    main_frame = tk.Frame(
        settings_window,
        padx=15,
        pady=15
    )

    main_frame.pack(
        fill="both",
        expand=True
    )

    tk.Label(
        main_frame,
        text="Extension Categories",
        font=("Arial", 16, "bold")
    ).pack(
        anchor="w",
        pady=(0, 10)
    )

    # ========================================================
    # LIST
    # ========================================================

    list_frame = tk.Frame(
        main_frame
    )

    list_frame.pack(
        fill="both",
        expand=True
    )

    scrollbar = tk.Scrollbar(
        list_frame,
        orient="vertical"
    )

    category_list = tk.Listbox(
        list_frame,
        yscrollcommand=scrollbar.set
    )

    scrollbar.config(
        command=category_list.yview
    )

    category_list.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    # ========================================================
    # REFRESH
    # ========================================================

    def refresh_list():

        category_list.delete(
            0,
            tk.END
        )

        for extension in sorted(
            categories
        ):

            category = categories[
                extension
            ]

            category_list.insert(
                tk.END,
                f"{extension}  →  {category}"
            )

    refresh_list()

    # ========================================================
    # ADD EXTENSION
    # ========================================================

    def add_extension():

        extension = simpledialog.askstring(
            "Add Extension",
            "Enter extension:\n\nExample: .abc",
            parent=settings_window
        )

        if not extension:
            return

        extension = extension.strip().lower()

        if not extension.startswith("."):
            extension = "." + extension

        if extension in categories:

            messagebox.showwarning(
                "Already Exists",
                f"{extension} already exists."
            )

            return

        category = simpledialog.askstring(
            "Category",
            "Enter category:\n\n"
            "Example: Documents",
            parent=settings_window
        )

        if not category:
            return

        category = category.strip()

        if not category:
            return

        categories[extension] = category

        save_categories(
            categories
        )

        refresh_list()

    # ========================================================
    # REMOVE EXTENSION
    # ========================================================

    def remove_extension():

        selection = category_list.curselection()

        if not selection:

            messagebox.showwarning(
                "No Selection",
                "Please select an extension to remove."
            )

            return

        selected_text = category_list.get(
            selection[0]
        )

        extension = selected_text.split(
            "→"
        )[0].strip()

        confirm = messagebox.askyesno(
            "Remove Extension",
            f"Remove {extension}?"
        )

        if not confirm:
            return

        if extension in categories:

            del categories[
                extension
            ]

            save_categories(
                categories
            )

            refresh_list()

    # ========================================================
    # BUTTONS
    # ========================================================

    button_frame = tk.Frame(
        main_frame
    )

    button_frame.pack(
        fill="x",
        pady=(10, 0)
    )

    tk.Button(
        button_frame,
        text="ADD EXTENSION",
        width=18,
        command=add_extension
    ).pack(
        side="left",
        padx=(0, 10)
    )

    tk.Button(
        button_frame,
        text="REMOVE EXTENSION",
        width=18,
        command=remove_extension
    ).pack(
        side="left"
    )


# ============================================================
# VIEW CATEGORIES
# ============================================================

def view_categories():

    category_window = tk.Toplevel(
        root
    )

    category_window.title(
        "Categories"
    )

    category_window.geometry(
        "500x500"
    )

    category_window.minsize(
        400,
        350
    )

    frame = tk.Frame(
        category_window,
        padx=15,
        pady=15
    )

    frame.pack(
        fill="both",
        expand=True
    )

    tk.Label(
        frame,
        text="Current Categories",
        font=("Arial", 16, "bold")
    ).pack(
        anchor="w",
        pady=(0, 10)
    )

    list_frame = tk.Frame(
        frame
    )

    list_frame.pack(
        fill="both",
        expand=True
    )

    scrollbar = tk.Scrollbar(
        list_frame,
        orient="vertical"
    )

    listbox = tk.Listbox(
        list_frame,
        yscrollcommand=scrollbar.set
    )

    scrollbar.config(
        command=listbox.yview
    )

    listbox.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    for extension in sorted(
        categories
    ):

        listbox.insert(
            tk.END,
            f"{extension}  →  {categories[extension]}"
        )


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title(
    "Smart File Organizer"
)

root.geometry(
    "800x650"
)

root.minsize(
    700,
    550
)


# ============================================================
# MAIN FRAME
# ============================================================

main_frame = tk.Frame(
    root,
    padx=25,
    pady=25
)

main_frame.pack(
    fill="both",
    expand=True
)


# ============================================================
# TITLE
# ============================================================

tk.Label(
    main_frame,
    text="Smart File Organizer",
    font=("Arial", 22, "bold")
).pack(
    pady=(10, 5)
)

tk.Label(
    main_frame,
    text="Organize your files automatically by category",
    font=("Arial", 11)
).pack(
    pady=(0, 20)
)


# ============================================================
# FOLDER SECTION
# ============================================================

folder_frame = tk.LabelFrame(
    main_frame,
    text="Selected Folder",
    padx=15,
    pady=15
)

folder_frame.pack(
    fill="x",
    pady=(0, 15)
)

folder_label = tk.Label(
    folder_frame,
    text="No folder selected",
    anchor="w",
    justify="left"
)

folder_label.pack(
    fill="x",
    pady=(0, 10)
)


# ============================================================
# FOLDER BUTTONS
# ============================================================

folder_button_frame = tk.Frame(
    folder_frame
)

folder_button_frame.pack(
    fill="x"
)

select_button = tk.Button(
    folder_button_frame,
    text="SELECT FOLDER",
    width=18,
    command=select_folder
)

select_button.pack(
    side="left",
    padx=(0, 10)
)

change_button = tk.Button(
    folder_button_frame,
    text="CHANGE FOLDER",
    width=18,
    command=change_folder,
    state="disabled"
)

change_button.pack(
    side="left"
)


# ============================================================
# ACTIONS
# ============================================================

action_frame = tk.LabelFrame(
    main_frame,
    text="Actions",
    padx=15,
    pady=15
)

action_frame.pack(
    fill="x",
    pady=(0, 15)
)

organize_button = tk.Button(
    action_frame,
    text="ORGANIZE FILES",
    width=20,
    command=organize_files,
    state="disabled"
)

organize_button.pack(
    side="left",
    padx=(0, 10)
)

undo_button = tk.Button(
    action_frame,
    text="UNDO LAST RUN",
    width=20,
    command=undo_last_run,
    state="disabled"
)

undo_button.pack(
    side="left"
)


# ============================================================
# OTHER OPTIONS
# ============================================================

options_frame = tk.Frame(
    main_frame
)

options_frame.pack(
    fill="x",
    pady=(5, 10)
)

tk.Button(
    options_frame,
    text="SETTINGS",
    width=18,
    command=open_settings
).pack(
    side="left",
    padx=(0, 10)
)

tk.Button(
    options_frame,
    text="VIEW CATEGORIES",
    width=18,
    command=view_categories
).pack(
    side="left"
)


# ============================================================
# STATUS
# ============================================================

status_frame = tk.LabelFrame(
    main_frame,
    text="Status",
    padx=15,
    pady=15
)

status_frame.pack(
    fill="both",
    expand=True
)

tk.Label(
    status_frame,
    text=(
        "Ready.\n\n"
        "1. Select a folder\n"
        "2. Preview the organization\n"
        "3. Organize your files\n"
        "4. Undo anytime if needed"
    ),
    justify="left",
    anchor="nw"
).pack(
    fill="both",
    expand=True
)


# ============================================================
# START
# ============================================================

update_undo_button_state()

root.mainloop()