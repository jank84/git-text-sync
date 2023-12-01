import platform
import tkinter as tk
from tkinter import messagebox, ttk
import tkinter.filedialog as filedialog
import os
import subprocess

from dotenv import load_dotenv
from git import Repo
import socket

load_dotenv()

git_access_token = os.getenv("git_access_token")
repo_url = os.getenv("repo")
app_name = os.getenv("app_name")
file_extensions = os.getenv("file_extensions")
search_folders = os.getenv("search_folders")
repo_path = './repo'

class GitGUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title(app_name)

        # Frames
        left_frame = tk.Frame(root)
        left_frame.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)
        right_frame = tk.Frame(root)
        right_frame.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)

        #buttons
        self.get_files_button = tk.Button(left_frame, text="📂 Get Files", command=self.get_files)
        self.get_files_button.pack(side=tk.LEFT)
        self.save_files_button = tk.Button(left_frame, text="💾 Save Files", command=self.save_files)
        self.save_files_button.pack(side=tk.LEFT)


        self.add_file_button = tk.Button(right_frame, text="➕ Add File", command=self.add_file)
        self.add_file_button.pack(side=tk.RIGHT)
        self.delete_file_button = tk.Button(right_frame, text="❌ Delete File", command=self.delete_file)
        self.delete_file_button.pack(side=tk.RIGHT)

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

        if os.path.isfile(file_path):
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":
                subprocess.call(["open", file_path])
            else:  # Linux
                subprocess.call(["xdg-open", file_path])

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

root = tk.Tk()
root.geometry("1024x768")
style = ttk.Style()
style.theme_use("clam")


app = GitGUIApp(root)
root.mainloop()
