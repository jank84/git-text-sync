# README for Git Repository txt Manager

## Overview
clones a repo using a personal git token and displays containing text files, allows modifiing and pushes changes.

## Features
- Clone Git repositories using provided repository URL and access token.
- Display repository files in a list view, highlighting modified and newly added files.
- Open files with the system's default editor on double-click.
- Add new files and delete existing files directly from the GUI.

## Environment Variables
The application requires several environment variables to be set. These variables should be defined in a `.env` file. You can copy the `.env.template` file and fill in the necessary values.

### `.env.template`
```
# Personal Access Token for Git
git_access_token=github_pat_<YOUR-TOKEN-SEE-New Fine-grained Personal Access Token>
# Repository URL (token need write permissions for this repo)
repo=<https://github.com/<username>/<project>>
# App name to show in the app title bar
app_name="git sync: [github.com/<username>/<project>]"
# File Extensions to Display (separated by semicolon)
file_extensions='.txt;.md'
# Folders to Search for Files (separated by semicolon)
search_folders=".;./subfolder/"
```

## Installation
1. Ensure Python is installed on your system.
2. Clone or download this repository to your local machine.
3. Install required dependencies:
   ```
   python -m venv .venv
   source .venv/bin/activate
   # or win: 
   # .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Copy `.env.template` to `.env` and update the environment variables as per your setup.
5. Go to https://github.com/settings/personal-access-tokens/new to create a new personal access token and copy it into the `.env` file `git_access_token`.
![Alt text](<New Fine-grained Personal Access Token.png>)
6. provide a repo with text files in the `.env` under `repo`. (token need write permissions for this repo)

## Running the Application
After setting up the environment variables in the `.env` file, run the application using Python:
```
python simple-git-editor.py
```
### The application can also be packed into a single standalone binary
tbd

## Dependencies
- GitPython: For Git operations.
- Tkinter: For the GUI interface.

## License
MIT