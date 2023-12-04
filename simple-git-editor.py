import platform
import tkinter as tk
from tkinter import messagebox, ttk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import os
import subprocess
import customtkinter as ctk
from dotenv import load_dotenv
from git import Repo
import socket
import json
from jsonschema import validate, ValidationError

load_dotenv()

git_access_token = os.getenv("git_access_token")
repo_url = os.getenv("repo")
app_name = os.getenv("app_name")
file_extensions = os.getenv("file_extensions")
search_folders = os.getenv("search_folders")
repo_path = './repo'
json_schema_path = "./json-schemas"


class GitGUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title(app_name)

        self.json_schemas = self.load_json_schemas(json_schema_path)

        # Frames
        left_frame = ctk.CTkFrame(root)
        left_frame.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)
        right_frame = ctk.CTkFrame(root)
        right_frame.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)

        #buttons
        self.get_files_button = ctk.CTkButton(left_frame, text="📂 Get Files", command=self.get_files)
        self.get_files_button.pack(side=tk.LEFT)
        self.save_files_button = ctk.CTkButton(left_frame, text="💾 Save Files", command=self.save_files)
        self.save_files_button.pack(side=tk.LEFT)


        self.add_file_button = ctk.CTkButton(right_frame, text="➕ Add File", command=self.add_file)
        self.add_file_button.pack(side=tk.RIGHT)
        self.delete_file_button = ctk.CTkButton(right_frame, text="❌ Delete File", command=self.delete_file)
        self.delete_file_button.pack(side=tk.RIGHT)


        style.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0)
        style.map('Treeview', background=[('selected', bg_color)], foreground=[('selected', selected_color)])
        root.bind("<<TreeviewSelect>>", lambda event: root.focus_set())
        
        self.file_list = ttk.Treeview(root)
        self.file_list["columns"] = ("Changed", "Filename")
        self.file_list.column("#0", width=0, stretch=tk.NO)
        self.file_list.column("Changed", anchor=tk.CENTER, width=32, stretch=tk.NO)
        self.file_list.column("Filename", anchor=tk.W, stretch=tk.YES)
        self.file_list.heading("Changed", text="", anchor=tk.CENTER)
        self.file_list.heading("Filename", text="Filename", anchor=tk.W)
        self.file_list.bind("<Double-1>", self.on_file_click)
        self.file_list.pack(fill=tk.BOTH, expand=True, side=tk.BOTTOM)
       
        self.file_states = {}
        self.check_for_changes()
        self.populate_list(repo_path)

    def get_files(self):
        if not repo_url or not git_access_token:
            messagebox.showerror("Error", "Repository URL or Access Token not set in environment variables.")
            return
        
        if not os.path.exists(repo_path):
            try:
                Repo.clone_from(repo_url, repo_path, env={'GIT_ASKPASS': 'echo', 'GIT_USERNAME': git_access_token})
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
        else:
            try:
                repo = Repo(repo_path)
                origin = repo.remote(name='origin')
                origin.fetch()

                default_branch = repo.active_branch.name if repo.active_branch else 'master'
                repo.git.reset('--hard', f'origin/{default_branch}')
                repo.git.pull()

            except Exception as e:
                messagebox.showerror("Error", str(e))
                return

        self.populate_list(repo_path)

    def load_json_schemas(self, schema_dir):
        schemas = {}
        # todo: check if folder exist
        for file in os.listdir(schema_dir):
            if file.endswith('.json'):
                with open(os.path.join(schema_dir, file)) as schema_file:
                    schemas[file] = json.load(schema_file)
        return schemas

    def populate_list(self, repo_path):
        extensions = os.environ.get('file_extensions', '')
        valid_extensions = extensions.split(';')

        search_folders = os.environ.get('search_folders', '')
        if search_folders:
            folders = search_folders.split(';')
        else:
            folders = ['']
        
        self.file_list.delete(*self.file_list.get_children())
        self.file_states = {}

        for folder in folders:
            folder_path = os.path.join(repo_path, folder)
            if os.path.isdir(folder_path):
                for filename in os.listdir(folder_path):
                    if any(filename.endswith(ext) for ext in valid_extensions):
                        file_rel_path = os.path.join(folder, filename)
                        file_full_path = os.path.join(folder_path, filename)
                        self.file_states[file_rel_path] = os.path.getmtime(file_full_path)
                        self.file_list.insert("", tk.END, values=("", file_rel_path), tags=('unchanged',))
        # tag for modified files
        self.file_list.tag_configure('modified', background='yellow')
                
    def check_for_changes(self):
        for filename in self.file_states:
            file_path = os.path.join(repo_path, filename)
            if os.path.exists(file_path) and os.path.getmtime(file_path) != self.file_states[filename]:
                # File has been modified
                self.file_states[filename] = os.path.getmtime(file_path)
                self.highlight_modified(filename)

        # Schedule next check
        self.root.after(5000, self.check_for_changes)

    def highlight_modified(self, filename):
        for item in self.file_list.get_children():
            if self.file_list.item(item, 'values')[1] == filename:
                self.file_list.item(item, values=("⭐", filename), tags=('modified',))
                break

    def on_file_click(self, event):
        item = self.file_list.selection()[0]
        filename = self.file_list.item(item, 'values')[1]
        file_path = os.path.join(repo_path, filename)

        if filename.endswith('.json'):
            with open(file_path) as json_file:
                json_data = json.load(json_file)
                for _, schema in self.json_schemas.items():
                    try:
                        validate(instance=json_data, schema=schema)
                        self.show_json_dialog(json_data, schema, file_path)
                        return
                    except ValidationError:
                        pass

        if os.path.isfile(file_path):
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":
                subprocess.call(["open", file_path])
            else:  # Linux
                subprocess.call(["xdg-open", file_path])

    def show_json_dialog(self, json_data, schema, file_path):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(schema.get('title', 'JSON Data'))

        # Create a canvas and a scrollbar
        canvas = ctk.CTkCanvas(dialog)
        scrollbar = ctk.CTkScrollbar(dialog, command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)

        # Configure canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", on_configure)

        self.widget_references = {}

        row = 0
        for prop, details in schema.get('properties', {}).items():
            label = ctk.CTkLabel(scrollable_frame, text=prop)
            label.grid(row=row, column=0, sticky='ew', padx=10, pady=5)

            value = json_data.get(prop, '')

            if isinstance(value, dict):
                nested_row = 0
                frame = ctk.CTkFrame(scrollable_frame)
                frame.grid(row=row, column=1, padx=10, pady=5, sticky='ew')
                for nested_prop, nested_details in details['properties'].items():
                    nested_label = ctk.CTkLabel(frame, text=nested_prop)
                    nested_label.grid(row=nested_row, column=0, sticky='w', padx=10, pady=2)
                    nested_text = ctk.CTkTextbox(frame, height=60, wrap='word')
                    nested_text.insert('end', str(value.get(nested_prop, '')))
                    nested_text.grid(row=nested_row, column=1, padx=10, pady=2, sticky='ew')
                    frame.grid_columnconfigure(1, weight=1)
                    nested_row += 1
                    self.widget_references[prop] = nested_text
            else:
                text = ctk.CTkTextbox(scrollable_frame, height=60, wrap='word')
                text.insert('end', str(value))
                text.grid(row=row, column=1, padx=10, pady=5, sticky='ew')
                scrollable_frame.grid_columnconfigure(1, weight=1)
                self.widget_references[prop] = text
            
            row += 1

        # Save button
        save_button = ctk.CTkButton(dialog, text="Save", command=lambda: self.save_json_data(json_data, schema, file_path))
        save_button.pack()

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def save_json_data(self, original_data, schema, file_path):
        def parse_input(data, schema_properties, parent=None):
            for prop, details in schema_properties.items():
                if details.get('type') == 'object':
                    # Handle nested object
                    nested_data = data.get(prop, {})
                    parse_input(nested_data, details['properties'], prop)
                    data[prop] = nested_data
                else:
                    widget_key = f"{parent}.{prop}" if parent else prop
                    widget = self.widget_references.get(widget_key)

                    if widget:
                        input_value = widget.get("1.0", "end-1c")  # Get text from Text widget

                        # Convert input value to the correct type based on the schema
                        if details.get('type') == 'number':
                            try:
                                input_value = float(input_value)
                            except ValueError:
                                messagebox.showerror("Validation Error", f"Value for '{prop}' should be a number.")
                                return False
                        elif details.get('type') == 'integer':
                            try:
                                input_value = int(input_value)
                            except ValueError:
                                messagebox.showerror("Validation Error", f"Value for '{prop}' should be a integer.")
                                return False
                        # Add other type conversions as needed

                        data[prop] = input_value
            return True

        # Create a copy of the original data to modify
        updated_data = original_data.copy()

        if not parse_input(updated_data, schema.get('properties', {})):
            return  # Return early if validation fails

        # Validate updated data
        try:
            validate(instance=updated_data, schema=schema)
            # Write back to file if validation passes
            with open(file_path, 'w') as json_file:
                json.dump(updated_data, json_file, indent=4)
            # messagebox.showinfo("Success", "Data saved successfully.")
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))


    def save_files(self):
        if not os.path.exists(repo_path):
            messagebox.showerror("Error", "Repository not cloned.")
            return
        try:
            repo = Repo(repo_path)
            repo.git.add(all=True)
            changed_files = [item.a_path for item in repo.head.commit.diff(None)]
            commit_message = f"Updated {', '.join(changed_files)} from {socket.gethostname()}"
            repo.index.commit(commit_message)
            repo.remote().push()
            self.get_files()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_file(self):
        selected_item = self.file_list.selection()
        if selected_item:
            filename = self.file_list.item(selected_item, 'values')[1]
            file_path = os.path.join(repo_path, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                self.file_list.delete(selected_item)
                del self.file_states[filename]

    def add_file(self):
        extensions = os.environ.get('file_extensions', '')
        valid_extensions = extensions.split(';')

        file_types = [('Allowed files', valid_extensions)]

        # Open file save dialog
        new_file_path = filedialog.asksaveasfilename(initialdir=repo_path, filetypes=file_types, defaultextension=valid_extensions[0])
        if new_file_path:
            with open(new_file_path, 'w') as new_file:
                new_file.write('')  # empty file

            # Open the file
            if platform.system() == "Windows":
                os.startfile(new_file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", new_file_path])
            else:  # Linux
                subprocess.call(["xdg-open", new_file_path])

            filename = os.path.basename(new_file_path)

            # Add to Treeview
            self.file_list.insert("", tk.END, values=("➕", filename), tags=('new_file',))
            self.file_states[filename] = os.path.getmtime(new_file_path)

        # Configure tag for new files
        self.file_list.tag_configure('new_file', background='lime green')

root = ctk.CTk()
root.geometry("1024x768")
###Treeview Customisation (theme colors are selected)
bg_color = root._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
text_color = root._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])
selected_color = root._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])
style = ttk.Style()
style.theme_use("default")


app = GitGUIApp(root)
root.mainloop()
