import tkinter as tk
import os
import json
from tkinter import filedialog
from tkinter import messagebox

# Program variables:
SOURCE_FOLDER = ""
DESTINATION_FOLDER = ""
folder_names = []


def browse_source_folder():
    """Opens a folder selection dialog and updates the selected folder."""
    global SOURCE_FOLDER
    SOURCE_FOLDER = filedialog.askdirectory()
    update_label1()


def update_label1():
    """Updates the label with the selected folder path."""
    if SOURCE_FOLDER:
        label1.config(text=f"Selected folder: {SOURCE_FOLDER}")
    else:
        label1.config(text="No source folder selected.")


def browse_destination_folder():
    """Opens a folder selection dialog and updates the selected folder."""
    global DESTINATION_FOLDER
    DESTINATION_FOLDER = filedialog.askdirectory()
    update_label2()


def update_label2():
    """Updates the label with the selected folder path."""
    if SOURCE_FOLDER:
        label2.config(text=f"Selected folder: {DESTINATION_FOLDER}")
    else:
        label2.config(text="No destination folder selected.")


# ------------------------- Log Textbox ------------------------------
# --- Update log
def log_to_textbox(message):
    """Appends a message to the log textbox."""
    log_textbox.insert(tk.END, message + "\n")
    log_textbox.see(tk.END)  # Scroll to the end of the textbox


# --- Clear log
def clear_log():
    """Clears the contents of the text box."""
    log_textbox.delete("1.0", "end")


# ------------------------- Business Methods ----------------------------------
def remove_forbidden_characters(title):
    """Handling forbidden characters in path"""
    title = title.replace("*"," ")
    title = title.replace("\""," ")
    title = title.replace("/"," ")
    title = title.replace("\\"," ")
    title = title.replace("<"," ")
    title = title.replace(">"," ")
    title = title.replace(":"," ")
    title = title.replace("|"," ")
    title = title.replace("?"," ")
    return title;
    
def add_folder_to_rename_list(root):
    """Add new folder tuple to the list of folders to be renamed"""
    # Global variables that gets changed along with this method
    global folder_names

    # Method body
    file_path = os.path.join(
        root, "project.json"
    )  # Prepare to the file path to that json to read
    try:
        with open(file_path, encoding="utf-8") as json_file:  # Open and read json file
            # Load json data, and get the title
            json_data = json.load(json_file)
            title = json_data["title"]

            # Remove special character that breaks code
            title = remove_forbidden_characters(title)

            # Create a path for newly-renamed folder
            new_folder_name = os.path.join(
                DESTINATION_FOLDER, title
            )  # New folder path with title
            folder_names.append(
                (root, new_folder_name)
            )  # Add the (old, new) tuple to list,

            # Mark this folder for finished to skip the children when it wants to check
            skipping_folder = root
    # Just error handling, nothing to see here really.
    except FileNotFoundError:
        log_to_textbox(f"Error: JSON file '{json_file}' not found at '{file_path}'.")
    # Return the folder to skip string.
    return skipping_folder


# ------------------------- Rename folders ------------------------------
def rename_folders():
    """Rename all folders that have a project.json inside selected folder"""
    # Initialize the process of renaming
    skipping_folder = ""  # Folder marked for skipping
    log_textbox.configure(state="normal")  # Change log to normal so it can update
    clear_log()  # Clear old logs

    # Check if dir exists, if not then make
    if not os.path.exists(DESTINATION_FOLDER):
        os.makedirs(DESTINATION_FOLDER)
        log_to_textbox(f"{DESTINATION_FOLDER} did not exist so new folder was created.")
        
    # Starting from Source folder, walk through all child folders in the tree to find folders to rename
    for root, dirs, files in os.walk(SOURCE_FOLDER):
        # Skip this child if its parent is marked to skip (added to to-rename list)
        # or if it's Destination folder (in case Destination folder is included inside the source folder)
        if skipping_folder == "" or skipping_folder not in root or DESTINATION_FOLDER not in root:
            if "project.json" in files:  # Look for the project.json
                skipping_folder = add_folder_to_rename_list(
                    root
                )  # Add folder to rename list
        else:
            continue  # To the next child

    # Renaming process
    for folder_name_pair in folder_names:
        old_name = folder_name_pair[0]
        new_name = folder_name_pair[1]
        if os.path.isdir(new_name) or os.path.isfile(new_name):             # If file exists, tell the user
            log_to_textbox(f"Already exists: {old_name} -> {new_name}")     # Old name is logged for convenience of finding it.
        else:
            os.rename(old_name, new_name)                                   # If not, move the folder to destination and rename it. (This method does two things)
            log_to_textbox(f"Renamed: {old_name} -> {new_name}")            # Tell the user of the change

    # Finishing up
    log_textbox.configure(state="disabled")                                 # Disable the textbox to prevent writing
    folder_names.clear()                                                    # Clear the folder_names list
    # Tell user it's done
    messagebox.showinfo(
        "Operation finished",
        "All Steam Workshop folders in selected directory are renamed.",
    )


# Create the main window
window = tk.Tk()
window.title("Steam Workshop Folder Mass Renamer")
window.geometry("400x300")

# Get screen width and height
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Calculate window's x and y coordinates to center it
x = (screen_width - 400) // 2
y = (screen_height - 300) // 2

# Set window size and position
window.geometry("400x300+{}+{}".format(x, y))

# Create a label for the input field
label_input = tk.Label(window, text="Select a folder:")
label_input.pack()

# Create a label for the input field
label_input = tk.Label(
    window,
    foreground="red",
    text="""Please select a folder that is outside the Steam Workshop folder 
and does not contain any active Steam Workshop folders within it,
or this program may render them undetectable by Steam.""",
)
label_input.pack()


# Create a button to browse for a folder
source_browse_button = tk.Button(
    window, text="Select Source Folder", command=browse_source_folder
)
source_browse_button.pack()
# Create a label to display the selected folder path
label1 = tk.Label(window, text="No folder selected.")
label1.pack()

# Create a button to browse for a destination folder folder
destination_browse_button = tk.Button(
    window, text="Select Destination Folder", command=browse_destination_folder
)
destination_browse_button.pack()
# Create a label to display the selected folder path
label2 = tk.Label(window, text="No folder selected.")
label2.pack()

# Create a button to show the selected path
show_button = tk.Button(window, text="Execute", command=rename_folders)
show_button.pack()

# Create a scrollable textbox for displaying logs
log_textbox = tk.Text(
    window, height=10, width=40, wrap="word", state="disabled"
)  # Wrap text at word boundaries
log_scrollbar = tk.Scrollbar(window, command=log_textbox.yview)
log_textbox["yscrollcommand"] = log_scrollbar.set
log_textbox.pack(side="left", fill="both", expand=True)
log_scrollbar.pack(side="right", fill="y")

# Start the GUI event loop
window.mainloop()
