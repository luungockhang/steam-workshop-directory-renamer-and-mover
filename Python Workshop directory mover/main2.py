import PySimpleGUI as sg
import os
import shutil
import json

# Read the project.json inside a directory, returns a boolean
def read_json(json_path, keyword):
    json_data = json.load(json_path + "project.json")
    if keyword in json_data["title"]:
        return True
    return False

# Define the layout
layout = [
    [sg.Text("Keyword:"), sg.InputText(key="-KEYWORD-")],
    [sg.Text("Source:"), sg.InputText(key="-SOURCE-"), sg.FolderBrowse()],
    [sg.Text("Destination:"), sg.InputText(key="-DESTINATION-"), sg.FolderBrowse()],
    [sg.Button("Move"), sg.Button("Cancel")]
]

# Create the window
window = sg.Window("File Mover", layout)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == "Move":
        # Handle source folder, destination folder
        folders_to_move = []
        keyword = values["-KEYWORD-"]
        source = values["-SOURCE-"]
        destination = values["-DESTINATION-"]

        if not keyword:
            sg.popup_error("Please enter a keyword.")
            continue

        if not source:
            sg.popup_error("Please select a source folder.")
            continue

        if not destination:
            sg.popup_error("Please select a destination folder.")
            continue

        if not os.path.exists(destination):
            print('Path does not exist and will be newly created.')
            os.makedirs(destination)
            
        try:
            # Read from the source
            for root, dirs, files in os.walk(source):
                # Read the project.json if exists
                if 'project.json' in files:
                    file_path = os.path.join(root,'project.json')
                    # open the json file
                    try:
                        with open(file_path, encoding='utf-8') as json_file:
                            # load json data
                            json_data = json.load(json_file)
                            if keyword in json_data['title']:
                                folders_to_move.append(root)
                    except FileNotFoundError:   
                        print(f"Error: JSON file '{json_file}' not found at '{file_path}'.")
            
            print(f"Found {len(folders_to_move)} folders")
            
            # Move the folders
            for folder_path in folders_to_move:
                print(f"Moving {folder_path}")
                shutil.move(folder_path, destination)
                print('Move complete')

            sg.popup("All folders moved successfully!")
            folders_to_move.clear()

        except Exception as e:
            sg.popup_error(f"An error occurred: {e}")
