#!/bin/bash

pyinstaller --noconfirm --onedir --windowed --add-data ".venv/Lib/site-packages/customtkinter;customtkinter/" simple-git-editor.py

ZIP_FILE="simple-git-editor.zip"

[ -f "$ZIP_FILE" ] && rm "$ZIP_FILE"

zip -r "$ZIP_FILE" "dist/simple-git-editor/"
zip -r "$ZIP_FILE" "json-schemas"
zip -r "$ZIP_FILE" ".env.template"

echo "Files successfully zipped into $ZIP_FILE"
