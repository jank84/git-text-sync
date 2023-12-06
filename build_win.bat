pyinstaller --noconfirm --onedir --windowed --add-data ".venv/Lib/site-packages/customtkinter;customtkinter/" simple-git-editor.py

@echo off
SET ZIP_FILE=simple-git-editor.zip

IF EXIST "%ZIP_FILE%" DEL /F "%ZIP_FILE%"

powershell -command "Compress-Archive -Path 'dist/simple-git-editor/*' -DestinationPath '%ZIP_FILE%' -Update"
powershell -command "Compress-Archive -Path 'json-schemas' -DestinationPath '%ZIP_FILE%' -Update"
powershell -command "Compress-Archive -Path '.env.template' -DestinationPath '%ZIP_FILE%' -Update"

echo Files successfully zipped into %ZIP_FILE%
